import os
import time
import json
import hashlib
import base64
import requests
import subprocess
import urllib.parse
import queue
import sys
import traceback
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed

# ================= 警告屏蔽 =================
# 屏蔽 urllib3 等库因为版本不匹配产生的烦人警告信息
warnings.filterwarnings("ignore")

# ================= 配置区 =================
STATE_FILE = "sub_state.json"                       # 记录订阅哈希和上次测试位置
VALID_NODES_FILE = "valid_nodes.json"               # 保存为JSON格式，包含IP、协议等信息
TARGET_COUNT = 20                                   # 目标有效节点数量
CONCURRENT_THREADS = 5                              # 并发测试线程数
CHECK_INTERVAL_SEC = 30 * 60                        # 间隔时间：30分钟
TEST_TIMEOUT = 5                                    # 节点测试超时时间(秒)

# 本地系统代理 (用于拉取订阅链接时翻墙，v2rayN混合端口默认10808)
FETCH_PROXY = "http://127.0.0.1:10808" 

# 1. 自动获取当前目录和核心路径
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
XRAY_CORE_PATH = os.path.join(CURRENT_DIR, "xray.exe")

# 2. 获取上一级目录并读取 vps_config.json
PARENT_DIR = os.path.dirname(CURRENT_DIR)
VPS_CONFIG_PATH = os.path.join(PARENT_DIR, "vps_config.json")

try:
    with open(VPS_CONFIG_PATH, 'r', encoding='utf-8') as f:
        vps_config = json.load(f)
        SUB_URL = vps_config.get("sub_url", "")
        if not SUB_URL:
            raise ValueError("vps_config.json 中没有找到 sub_url 字段！")
except Exception as e:
    print(f"[严重错误] 读取订阅链接失败: {e}")
    print("请先去上一级目录运行『1-首次配置服务器.bat』并输入订阅链接。")
    input("\n按回车键退出...")
    sys.exit(1)

# 3. 创建测试专用的端口队列 (从 20000 开始，绝不会和本地 10808 冲突)
PORT_QUEUE = queue.Queue()
for port in range(20000 + 1, 20000 + CONCURRENT_THREADS + 1):
    PORT_QUEUE.put(port)
# ==========================================

def get_md5(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def b64_decode(text):
    """增强版 Base64 解码，兼容各种奇葩格式"""
    text = text.strip()
    # 兼容 URL-safe 格式的 Base64
    text = text.replace('-', '+').replace('_', '/')
    # 补齐缺少的 = 号
    padding = len(text) % 4
    if padding != 0:
        text += "=" * (4 - padding)
    
    try:
        return base64.b64decode(text).decode('utf-8', errors='ignore')
    except Exception:
        return "{}" # 如果解码彻底失败，返回空 JSON 防止程序崩溃

def fetch_and_decode_sub():
    """获取并解码订阅链接 (已加入本地代理支持)"""
    print(f"[网络] 正在通过代理 {FETCH_PROXY} 拉取订阅数据...")
    proxies = {
        "http": FETCH_PROXY,
        "https": FETCH_PROXY
    }
    try:
        response = requests.get(SUB_URL, proxies=proxies, timeout=15)
        response.raise_for_status()
        raw_text = response.text.strip()
        sub_hash = get_md5(raw_text)
        
        try:
            nodes = [line.strip() for line in b64_decode(raw_text).splitlines() if line.strip()]
        except Exception:
            nodes = [line.strip() for line in raw_text.splitlines() if line.strip()]
            
        print(f"[网络] 成功拉取到 {len(nodes)} 条节点数据！")
        return nodes, sub_hash
    except Exception as e:
        print(f"[错误] 拉取订阅失败，请检查本地代理是否开启，或链接是否有效: {e}")
        return [], None

def parse_node_uri(uri):
    """核心解析器，增加对 Shadowsocks 的支持及更强的容错处理"""
    node_info = {
        "raw_uri": uri, "protocol": "unknown", "ip": "unknown", "port": 0, "country": ""
    }
    try:
        if uri.startswith("vmess://"):
            node_info["protocol"] = "vmess"
            b64_str = uri[8:]
            decoded_str = b64_decode(b64_str)
            vmess_json = json.loads(decoded_str)
            
            node_info["ip"] = str(vmess_json.get("add", "unknown"))
            port_val = vmess_json.get("port", 0)
            node_info["port"] = int(port_val) if port_val else 0
            node_info["vmess_data"] = vmess_json
            
        elif uri.startswith("vless://") or uri.startswith("trojan://"):
            parsed = urllib.parse.urlparse(uri)
            node_info["protocol"] = parsed.scheme
            node_info["ip"] = parsed.hostname
            node_info["port"] = parsed.port
            node_info["uuid"] = parsed.username
            node_info["query"] = urllib.parse.parse_qs(parsed.query)

        elif uri.startswith("ss://"):
            node_info["protocol"] = "shadowsocks"
            # 移除链接末尾的别名注释 (如 #US-01)
            ss_str = uri[5:].split('#')[0]
            
            if '@' in ss_str:
                user_info, host_port = ss_str.split('@', 1)
                if ':' not in user_info:
                    user_info = b64_decode(user_info)
                if ':' in user_info:
                    node_info["method"], node_info["password"] = user_info.split(':', 1)
                
                # 【关键修复】：无情切掉问号后面的参数和斜杠路径
                host_port = host_port.split('?')[0].split('/')[0] 
                
                if ':' in host_port:
                    node_info["ip"], port_str = host_port.split(':', 1)
                    node_info["port"] = int(port_str)
            else:
                decoded = b64_decode(ss_str)
                if '@' in decoded:
                    user_info, host_port = decoded.split('@', 1)
                    if ':' in user_info:
                        node_info["method"], node_info["password"] = user_info.split(':', 1)
                        
                    # 【关键修复】：同样在这里切掉问号
                    host_port = host_port.split('?')[0].split('/')[0]
                    
                    if ':' in host_port:
                        node_info["ip"], port_str = host_port.split(':', 1)
                        node_info["port"] = int(port_str)
                        
    except Exception as e:
        print(f"  [解析异常] 无法识别格式跳过，协议头: {uri[:10]}... 报错: {e}")
        
    return node_info
    
def generate_temp_config(node_info, local_port):
    """生成临时配置文件 (完整支持 Vmess, Vless, Trojan, Shadowsocks)"""
    config = {
        "log": {"loglevel": "none"},
        "inbounds": [{"port": local_port, "listen": "127.0.0.1", "protocol": "socks", "settings": {"udp": True}}],
        "outbounds": []
    }
    
    protocol = node_info.get("protocol")
    outbound = None

    if protocol == "vmess" and "vmess_data" in node_info:
        v_data = node_info["vmess_data"]
        outbound = {
            "protocol": "vmess",
            "settings": {"vnext": [{"address": v_data.get("add"), "port": int(v_data.get("port", 0)), "users": [{"id": v_data.get("id"), "alterId": int(v_data.get("aid", 0))}]}]},
            "streamSettings": {"network": v_data.get("net", "tcp"), "security": v_data.get("tls", "none")}
        }
        if v_data.get("net") == "ws":
            outbound["streamSettings"]["wsSettings"] = {"path": v_data.get("path", "/"), "headers": {"Host": v_data.get("host", "")}}

    elif protocol in ["vless", "trojan"]:
        q = node_info.get("query", {})
        net = q.get("type", ["tcp"])[0]
        tls = q.get("security", ["none"])[0]

        outbound = {
            "protocol": protocol,
            "settings": {},
            "streamSettings": {"network": net, "security": tls}
        }

        if protocol == "vless":
            outbound["settings"]["vnext"] = [{
                "address": node_info["ip"], "port": int(node_info["port"]), "users": [{"id": node_info["uuid"], "encryption": "none"}]
            }]
        else: # trojan
            outbound["settings"]["servers"] = [{
                "address": node_info["ip"], "port": int(node_info["port"]), "password": node_info["uuid"]
            }]

        if tls == "tls":
            sni = q.get("sni", [node_info["ip"]])[0]
            outbound["streamSettings"]["tlsSettings"] = {"serverName": sni, "allowInsecure": True}
            if "fp" in q: outbound["streamSettings"]["tlsSettings"]["fingerprint"] = q["fp"][0]
        elif tls == "reality":
            outbound["streamSettings"]["realitySettings"] = {
                "serverName": q.get("sni", [""])[0], "publicKey": q.get("pbk", [""])[0],
                "shortId": q.get("sid", [""])[0], "fingerprint": q.get("fp", ["chrome"])[0]
            }

        if net == "ws":
            host = q.get("host", [""])[0]
            outbound["streamSettings"]["wsSettings"] = {"path": q.get("path", ["/"])[0], "headers": {"Host": host} if host else {}}
        elif net == "grpc":
            outbound["streamSettings"]["grpcSettings"] = {"serviceName": q.get("serviceName", [""])[0], "multiMode": True}

    # 新增：Shadowsocks 出站配置
    elif protocol == "shadowsocks":
        outbound = {
            "protocol": "shadowsocks",
            "settings": {
                "servers": [{
                    "address": node_info["ip"],
                    "port": int(node_info["port"]),
                    "method": node_info.get("method", "chacha20-ietf-poly1305"),
                    "password": node_info.get("password", "")
                }]
            }
        }

    if outbound:
        config["outbounds"].append(outbound)
    else:
        config["outbounds"].append({"protocol": "freedom"})

    config_path = os.path.join(CURRENT_DIR, f"temp_config_{local_port}.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f)
    return config_path

def test_node(node_uri):
    """测试单个节点"""
    node_info = parse_node_uri(node_uri)
    if node_info["protocol"] == "unknown" or node_info["ip"] == "unknown":
        return None
        
    local_port = PORT_QUEUE.get()
    config_path = generate_temp_config(node_info, local_port)
    process = None
    
    try:
        process = subprocess.Popen([XRAY_CORE_PATH, "-c", config_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1.5)
        
        proxies = {'http': f'socks5://127.0.0.1:{local_port}', 'https': f'socks5://127.0.0.1:{local_port}'}
        start_time = time.time()
        resp = requests.get("https://www.google.com/generate_204", proxies=proxies, timeout=TEST_TIMEOUT)
        
        if resp.status_code == 204:
            delay = int((time.time() - start_time) * 1000)
            print(f"  [成功] IP: {node_info['ip']} | 协议: {node_info['protocol']} | 延迟: {delay}ms")
            node_info["delay_ms"] = delay
            return node_info
    except Exception:
        pass
    finally:
        if process:
            process.terminate()
            process.wait()
        if os.path.exists(config_path):
            os.remove(config_path)
        PORT_QUEUE.put(local_port)
        
    return None

def run_inspection():
    """单次检测的主干流程"""
    if not os.path.exists(XRAY_CORE_PATH):
        raise FileNotFoundError(f"找不到核心文件: {XRAY_CORE_PATH}，请确保 xray.exe 存在！")

    print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] 开始执行节点检测任务...")
    
    all_nodes, current_hash = fetch_and_decode_sub()
    if not all_nodes:
        print("[提示] 本次未能获取到节点，将跳过后续测试。")
        return
    
    state_file_data = {}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            state_file_data = json.load(f)
    last_index = state_file_data.get("last_index", 0)
    
    # 触底重置逻辑
    if current_hash != state_file_data.get("sub_hash"):
        print("[检测] 发现订阅内容更新，测试进度重置为 0")
        last_index = 0
    elif last_index >= len(all_nodes):
        print(f"[检测] 当前订阅内的 {len(all_nodes)} 个节点已全部测完，重置进度，开启新一轮循环！")
        last_index = 0

    valid_nodes_info = []
    
    # 1. 复检历史有效节点
    if os.path.exists(VALID_NODES_FILE):
        try:
            with open(VALID_NODES_FILE, 'r', encoding='utf-8') as f:
                old_valid_nodes = json.load(f)
            
            if old_valid_nodes:
                print(f"[复检] 正在测试上次保存的 {len(old_valid_nodes)} 个有效节点...")
                with ThreadPoolExecutor(max_workers=CONCURRENT_THREADS) as executor:
                    futures = [executor.submit(test_node, node["raw_uri"]) for node in old_valid_nodes]
                    for future in as_completed(futures):
                        result = future.result()
                        if result:
                            valid_nodes_info.append(result)
                print(f"[复检完成] 剩余有效: {len(valid_nodes_info)}/{TARGET_COUNT}")
        except json.JSONDecodeError:
            print("[警告] 历史 valid_nodes.json 文件损坏，将重新开始测试。")

    # 2. 如果不足，继续向下测试
    if len(valid_nodes_info) < TARGET_COUNT:
        print(f"[测试] 继续从第 {last_index} 条节点开始向下测试新节点...")
        with ThreadPoolExecutor(max_workers=CONCURRENT_THREADS) as executor:
            while len(valid_nodes_info) < TARGET_COUNT and last_index < len(all_nodes):
                batch = all_nodes[last_index : last_index + CONCURRENT_THREADS]
                futures = [executor.submit(test_node, uri) for uri in batch]
                
                for future in as_completed(futures):
                    result = future.result()
                    if result and len(valid_nodes_info) < TARGET_COUNT:
                        valid_nodes_info.append(result)
                
                last_index += len(batch)

    # 3. 结果保存
    with open(VALID_NODES_FILE, 'w', encoding='utf-8') as f:
        json.dump(valid_nodes_info, f, indent=4, ensure_ascii=False)
    print(f"[保存] 已将 {len(valid_nodes_info)} 个节点的详细信息保存至 {VALID_NODES_FILE}")
    
    with open(STATE_FILE, 'w') as f:
        json.dump({"sub_hash": current_hash, "last_index": last_index}, f)

def main():
    """系统主循环"""
    while True:
        run_inspection()
        print(f"\n任务结束，等待 {CHECK_INTERVAL_SEC // 60} 分钟后进行下一次轮询...\n")
        time.sleep(CHECK_INTERVAL_SEC)

# ==========================================
# 全局报错拦截器 (防闪退保护壳)
# ==========================================
if __name__ == "__main__":
    try:
        os.system('cls' if os.name == 'nt' else 'clear') 
        main()
    except KeyboardInterrupt:
        print("\n[退出] 检测到用户手动强制停止 (Ctrl+C)。")
    except Exception as e:
        print("\n" + "="*50)
        print("❌ [严重系统异常] 脚本运行中途发生崩溃！")
        print("="*50)
        print(f"👉 具体报错原因:\n{e}\n")
        print("👉 详细堆栈信息 (供排错参考):")
        traceback.print_exc()
        print("="*50)
    finally:
        print("\n----------------------------------------")
        input("💡 提示：按回车键 (Enter) 关闭此窗口...")
        sys.exit()