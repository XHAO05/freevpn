import urllib.request
import base64
import random
import os
import datetime

# --- 1. 初始化时间动态变量 ---
today = datetime.datetime.now()
nodefree_date = today.strftime('%Y/%m/%Y%m%d')
openrunner_date = today.strftime('%Y%m%d')

# --- 2. 核心策略：将订阅源划分为 A、B 两组 ---
# A组：你原本收集的 7 个相对稳定的常规源
GROUP_A_URLS = [
    f"https://nodefree.org/dy/{nodefree_date}.txt",
    "https://raw.githubusercontent.com/mfuu/v2ray/master/v2ray",
    "https://raw.fastgit.org/freefq/free/master/v2",
    "https://raw.githubusercontent.com/ermaozi/get_subscribe/main/subscribe/v2ray.txt",
    "https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2",
    f"https://freenode.openrunner.net/uploads/{openrunner_date}-v2ray.txt",
    "https://tt.vg/freev2"
]

# B组：新加的 3 个海量但无效节点多的动态爬虫源
GROUP_B_URLS = [
    "https://raw.githubusercontent.com/ebrasha/free-v2ray-public-list/main/V2Ray-Config-By-EbraSha-All-Type.txt",
    "https://raw.githubusercontent.com/Danialsamadi/v2go/main/AllConfigsSub.txt",
    "https://raw.githubusercontent.com/Mahdi0024/ProxyCollector/master/sub/proxies.txt"
]

script_dir = os.path.dirname(os.path.abspath(__file__))

# --- [提取函数] 负责下载、智能Base64解码并清洗节点 ---
def fetch_and_clean_nodes(url_list, group_name):
    print(f"📦 开始抓取 【{group_name}】 的节点数据...")
    nodes_pool = []
    for url in url_list:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, timeout=15) as response:
                content = response.read().decode('utf-8').strip()
                
                if "://" not in content[:50]:
                    try:
                        content += "=" * ((4 - len(content) % 4) % 4)
                        content = base64.b64decode(content).decode('utf-8')
                    except:
                        pass
                
                lines = content.splitlines()
                count = 0
                for line in lines:
                    if "://" in line:
                        nodes_pool.append(line.strip())
                        count += 1
                print(f"  ✅ 成功拉取 {count} 个节点 | 源: {url}")
        except Exception as e:
            print(f"  ❌ 抓取失败 (可能墙或断更): {url} | 错误: {e}")
            
    unique_nodes = list(set(nodes_pool))
    print(f"📊 【{group_name}】 聚合去重完成，共计独特节点: {len(unique_nodes)} 个\n")
    return unique_nodes

# --- [写入函数] 负责将节点转为标准订阅并保存 ---
def save_sub_file(nodes_list, filename):
    final_text = '\n'.join(nodes_list)
    encoded_text = base64.b64encode(final_text.encode('utf-8')).decode('utf-8')
    output_file = os.path.join(script_dir, filename)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(encoded_text)
    print(f"🎉 写入成功 -> [{filename}] | 包含节点: {len(nodes_list)} 个")

# ==================== 主程序逻辑 ====================

# 初始化空列表，防止因网络问题抓取失败导致后续变量未定义
nodes_a = []
nodes_b = []

# 🚀 第一步：处理优质 A 组，合流并直接生成 sub1.txt
nodes_a = fetch_and_clean_nodes(GROUP_A_URLS, "A组-优质常规源")
if nodes_a:
    save_sub_file(nodes_a, "sub1.txt")
else:
    print("⚠️ 警告：A组未获取到任何节点，sub1.txt 未生成")

print("-" * 50)

# 🚀 第二步：处理海量 B 组，彻底洗牌打乱，切割分发到 sub2 ~ sub5 (每份500个)
nodes_b = fetch_and_clean_nodes(GROUP_B_URLS, "B组-海量噪点源")
if nodes_b:
    random.shuffle(nodes_b)
    
    # 循环生成后面的 4 个文档 (sub2, sub3, sub4, sub5)
    for i in range(4):
        file_num = i + 2  # 从 sub2 开始
        start_idx = i * 500
        end_idx = start_idx + 500
        
        # 截取对应的 500 个独立节点
        chunk = nodes_b[start_idx:end_idx]
        
        if chunk:
            save_sub_file(chunk, f"sub{file_num}.txt")
        else:
            print(f"⚠️ B组节点总数不足，无法生成 sub{file_num}.txt")
else:
    print("⚠️ 警告：B组未获取到任何节点，后续盲盒文件未生成")

print("-" * 50)

# 🚀 第三步：生成包含所有节点的全量汇总文件
print("🚀 开始生成全量节点汇总文件...")
# 将 A 组和 B 组相加，并再次使用 set() 进行全局去重，防止两个组之间有重复的节点
all_nodes = list(set(nodes_a + nodes_b))

if all_nodes:
    # 你可以把 sub_all.txt 改成你想要的汇总文件名
    save_sub_file(all_nodes, "sub_all.txt") 
else:
    print("⚠️ 警告：A组和B组均未获取到任何节点，汇总文件未生成")

print("\n✅ 扩容版规则及全量汇总执行完毕！等待 GitHub Actions 自动同步回仓库。")