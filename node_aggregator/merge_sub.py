import urllib.request
import base64
import random
import os
import datetime  # ⚠️ 帮你把被我误删的时间模块加回来了！

# --- 1. 恢复你的时间动态变量（绝对不能删的部分） ---
today = datetime.datetime.now()
nodefree_date = today.strftime('%Y/%m/%Y%m%d')
openrunner_date = today.strftime('%Y%m%d')

# --- 2. 终极大聚合：你的原链接 + 我的新链接 ---
SUBSCRIPTION_URLS = [
    # ---- 下面是你原本辛辛苦苦收集的链接 ----
    f"https://nodefree.org/dy/{nodefree_date}.txt",
    "https://raw.githubusercontent.com/mfuu/v2ray/master/v2ray",
    "https://raw.fastgit.org/freefq/free/master/v2",
    "https://raw.githubusercontent.com/ermaozi/get_subscribe/main/subscribe/v2ray.txt",
    "https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2",
    f"https://freenode.openrunner.net/uploads/{openrunner_date}-v2ray.txt",
    "https://tt.vg/freev2",
    # ---- 下面是我给你补充的 3 个高频更新链接 ----
    "https://raw.githubusercontent.com/ebrasha/free-v2ray-public-list/main/V2Ray-Config-By-EbraSha-All-Type.txt",
    "https://raw.githubusercontent.com/Danialsamadi/v2go/main/AllConfigsSub.txt",
    "https://raw.githubusercontent.com/Mahdi0024/ProxyCollector/master/sub/proxies.txt"
]

all_nodes = []
print("🚀 开始执行全网节点大聚合，请稍候...\n")

# --- 3. 自动下载并解析所有节点 ---
for url in SUBSCRIPTION_URLS:
    try:
        # 加上浏览器伪装，防止被某些网站屏蔽
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=15) as response:
            content = response.read().decode('utf-8').strip()
            
            # 判断是否是 Base64 编码并解码
            if "://" not in content[:50]:
                try:
                    content += "=" * ((4 - len(content) % 4) % 4)
                    content = base64.b64decode(content).decode('utf-8')
                except:
                    pass
            
            lines = content.splitlines()
            count = 0
            for line in lines:
                if "://" in line:  # 确保抓取到的是有效节点格式
                    all_nodes.append(line.strip())
                    count += 1
            print(f"✅ 获取到 {count} 个节点 | 来源: {url}")
    except Exception as e:
        print(f"❌ 抓取失败 (可能源已失效或被墙): {url} | 报错: {e}")

# --- 4. 去重并彻底打乱节点池 ---
all_nodes = list(set(all_nodes))
random.shuffle(all_nodes) 
print(f"\n🌍 合并去重后，总共拥有绝赞节点池: {len(all_nodes)} 个\n")

# --- 5. 核心魔法：将海量节点切分为 5 份，每份 200 个 ---
num_files = 5
nodes_per_file = 200
script_dir = os.path.dirname(os.path.abspath(__file__))

for i in range(num_files):
    # 计算每次抓取的起始和结束位置
    start_idx = i * nodes_per_file
    end_idx = start_idx + nodes_per_file
    
    # 切走这 200 个节点
    chunk = all_nodes[start_idx:end_idx]
    
    # 极端情况防爆保护：如果节点总数不足，直接终止
    if not chunk:
        print(f"⚠️ 剩余节点已被抽干，无法继续生成 sub{i+1}.txt。")
        break

    # 转换为 v2rayN 识别的 Base64 格式
    final_text = '\n'.join(chunk)
    encoded_text = base64.b64encode(final_text.encode('utf-8')).decode('utf-8')
    
    # 生成文件名及路径 (sub1.txt 到 sub5.txt)
    output_filename = f"sub{i+1}.txt"
    output_file = os.path.join(script_dir, output_filename)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(encoded_text)
        
    print(f"🎉 成功生成 [{output_filename}]，包含 {len(chunk)} 个独立节点！")

print("\n✅ 所有任务执行完毕！准备让 GitHub Actions 提交变动。")