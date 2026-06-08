import requests
import base64
import os
import datetime

today = datetime.datetime.now()
nodefree_date = today.strftime('%Y/%m/%Y%m%d')
openrunner_date = today.strftime('%Y%m%d')

SUBSCRIPTION_URLS = [
    f"https://nodefree.org/dy/{nodefree_date}.txt",
    "https://raw.githubusercontent.com/mfuu/v2ray/master/v2ray",
    "https://raw.fastgit.org/freefq/free/master/v2",
    "https://raw.githubusercontent.com/ermaozi/get_subscribe/main/subscribe/v2ray.txt",
    "https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2",
    f"https://freenode.openrunner.net/uploads/{openrunner_date}-v2ray.txt",
    "https://tt.vg/freev2"
]

# 获取当前脚本所在文件夹的路径，确保输出文件始终生成在该文件夹内
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(script_dir, "my_custom_sub.txt")

def merge_subscriptions():
    all_nodes = []
    for url in SUBSCRIPTION_URLS:
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                encoded_text = response.text.strip()
                try:
                    padding = len(encoded_text) % 4
                    if padding:
                        encoded_text += '=' * (4 - padding)
                    decoded_bytes = base64.b64decode(encoded_text)
                    decoded_text = decoded_bytes.decode('utf-8', errors='ignore')
                except Exception:
                    decoded_text = encoded_text
                for line in decoded_text.splitlines():
                    if line.startswith(('vmess://', 'vless://', 'trojan://', 'ss://')):
                        all_nodes.append(line.strip())
        except Exception:
            pass

    if all_nodes:
        unique_nodes = list(set(all_nodes))
        merged_text = "\n".join(unique_nodes)
        final_b64_string = base64.b64encode(merged_text.encode('utf-8')).decode('utf-8')
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(final_b64_string)

if __name__ == "__main__":
    merge_subscriptions()
