import os
import json
import base64
import urllib.parse
import urllib.request
import qrcode
import socket
import ipaddress
import traceback
import time

# ================= 配置区 =================
TXT_INPUT_FILE = "good_nodes.txt"   # 输入：你要读取的节点文本
JSON_OUTPUT_FILE = "nodes_info.json" # 输出：汇总数据文件（供下一个渲染脚本读取）
QR_OUTPUT_DIR = "qr_codes"          # 输出：存放生成的二维码的文件夹
# ==========================================

def resolve_to_ip(address):
    """智能解析：如果是域名则尝试转为IP，如果是IP则原样返回"""
    address = address.strip()
    try:
        ipaddress.ip_address(address)
        return address 
    except ValueError:
        pass 

    try:
        real_ip = socket.gethostbyname(address)
        return real_ip
    except socket.gaierror:
        return address

def get_country_by_ip(ip):
    """
    在线检测：使用免费的 ip-api 接口查询 IP 对应的真实国家/地区（中文）
    """
    if not ip or ip == "unknown":
        return "未知"
        
    # 支持 IPv4 和 IPv6 的中文位置查询
    url = f"http://ip-api.com/json/{ip}?lang=zh-CN"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get("status") == "success":
                return data.get("country", "未知")
    except Exception as e:
        print(f"  ⚠️ 提示: 接口查询 IP [{ip}] 国家失败 (原因: {e})，将启用名字兜底逻辑")
    return "未知"

def parse_node(url):
    """
    智能解析节点，提取：协议、原始地址、地区/节点名称
    """
    url = url.strip()
    protocol = "unknown"
    raw_host = "unknown"
    region_name = "未命名" 
    
    if not url or "://" not in url:
        return protocol, raw_host, region_name

    protocol = url.split("://")[0].lower()
    rest = url.split("://")[1]

    # 提取非 vmess 协议的别名/名称（通常在 # 之后）
    if protocol != "vmess" and "#" in rest:
        encoded_name = rest.split("#")[1]
        region_name = urllib.parse.unquote(encoded_name)

    try:
        if protocol == "vmess":
            b64_str = rest
            b64_str += "=" * ((4 - len(b64_str) % 4) % 4)
            node_data = json.loads(base64.b64decode(b64_str).decode('utf-8'))
            raw_host = node_data.get("add", "unknown")
            region_name = node_data.get("ps", "未命名")
            
        elif protocol in ["vless", "trojan"]:
            if "@" in rest:
                host_part = rest.split("@")[1].split("/")[0].split("?")[0].split("#")[0]
                raw_host = host_part.split(":")[0]
                
        elif protocol == "ss":
            if "@" in rest:
                host_part = rest.split("@")[1].split("/")[0].split("?")[0].split("#")[0]
                raw_host = host_part.split(":")[0]
            else:
                b64_str = rest.split("#")[0]
                b64_str += "=" * ((4 - len(b64_str) % 4) % 4)
                decoded = base64.b64decode(b64_str).decode('utf-8')
                if "@" in decoded:
                    host_part = decoded.split("@")[1]
                    raw_host = host_part.split(":")[0]
                    
        else:
            if "@" in rest:
                host_part = rest.split("@")[1].split("/")[0].split("?")[0].split("#")[0]
                raw_host = host_part.split(":")[0]
    except Exception as e:
        print(f"  ⚠️ 解析细节出错: {e}")

    return protocol, raw_host, region_name

def main():
    if not os.path.exists(QR_OUTPUT_DIR):
        os.makedirs(QR_OUTPUT_DIR)

    if not os.path.exists(TXT_INPUT_FILE):
        print(f"❌ 找不到文件: {TXT_INPUT_FILE}，请确保它和脚本在同一目录下！")
        return

    with open(TXT_INPUT_FILE, "r", encoding="utf-8") as f:
        node_urls = [line.strip() for line in f if line.strip()]

    print(f"📦 共读取到 {len(node_urls)} 个节点，开始执行『全自动信息提取与国家检测』...\n")
    
    nodes_data_list = []

    for index, url in enumerate(node_urls):
        # 1. 基础解析
        protocol, raw_host, region_name = parse_node(url)
        real_ip = resolve_to_ip(raw_host)
        
        # 2. 自动检测国家地理位置
        print(f"🔄 [{index}] 正在检测真实国家地区 (IP: {real_ip})...")
        detected_country = get_country_by_ip(real_ip)
        
        # 3. 智能兜底：如果在线接口没查到，就拿节点别名的前两个字（比如 韩国、日本、香港）当作国家
        if (detected_country == "未知" or not detected_country) and region_name != "未命名":
            detected_country = region_name[:2]
        
        # 4. 生成二维码（100%保持原始url，确保扫码可用）
        qr_filename = f"node_{index}.png"
        qr_filepath = os.path.join(QR_OUTPUT_DIR, qr_filename)
        img = qrcode.make(url)
        img.save(qr_filepath)
        
        # 5. 组装完整且精准匹配的数据链条
        node_dict = {
            "id": index,
            "url": url,                 # 原始链接
            "protocol": protocol,       # 协议类型
            "name_region": region_name, # 原始节点名
            "raw_host": raw_host,       # 原始Host
            "ip": real_ip,              # 真实数字IP
            "country": detected_country,# 自动检测出的国家/地区（渲染脚本的核心数据）
            "qr_image": qr_filepath     # 二维码路径
        }
        nodes_data_list.append(node_dict)
        
        print(f"   ➔ 检测结果: 协议={protocol.upper()} | 国家={detected_country} | 别名={region_name}\n")
        
        # 频率控制：免费接口请求太快容易被封，稍微暂停 0.3 秒，保证稳定
        time.sleep(0.3)

    # 6. 保存为完美的结构化 JSON，供下一步渲染直接读取
    with open(JSON_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(nodes_data_list, f, indent=4, ensure_ascii=False)

    print("-" * 50)
    print(f"🎉 全部处理完成！")
    print(f"👉 包含所有国家、协议、IP和二维码路径的数据已保存至: {JSON_OUTPUT_FILE}")
    print(f"👉 下一步脚本（图片渲染脚本）直接读取这个 JSON 即可完美匹配，绝不错位！")

# ================= 核心防闪退逻辑 =================
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("\n" + "="*50)
        print("❌ 糟糕，脚本运行中途报错了！")
        traceback.print_exc() 
        print("="*50 + "\n")
    finally:
        input("👉 运行结束，请按回车键 (Enter) 关闭窗口...")