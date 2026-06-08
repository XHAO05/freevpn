import json
import os

def run_setup():
    print("="*50)
    print("🚀 24小时无人直播系统 —— 首次运行配置向导")
    print("="*50)
    print("请输入您的服务器信息（这些信息仅安全地保存在您的本地电脑中）：\n")

    host = input("1. 请输入 VPS 的 IP 地址 (如 154.23.xxx.xxx): ").strip()
    
    port = input("2. 请输入 SSH 端口号 (直接回车默认是 22): ").strip()
    if not port:
        port = "22"
        
    password = input("3. 请输入服务器 root 密码: ").strip()

    # 将用户输入的信息打包成字典
    config = {
        "host": host,
        "port": int(port),
        "user": "root",
        "password": password
    }

    # 获取当前目录，并保存为独立的 vps_config.json 文件
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(BASE_DIR, "vps_config.json")
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)

    print("\n✅ 太棒了！服务器配置已成功保存！")
    print("以后只需要运行 run_all.py 即可全自动生成并上传图片。")
    print("如需更换服务器，随时再次双击运行本向导即可覆盖旧配置。")
    
    # 停顿一下，防止窗口秒关
    input("\n按回车键退出向导...")

if __name__ == "__main__":
    run_setup()