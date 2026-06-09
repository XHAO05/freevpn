import json
import os

def load_existing_config(config_path):
    """尝试加载已有的配置文件"""
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    return None

def run_setup():
    print("="*50)
    print("🚀 24小时无人直播系统 —— 首次运行配置向导")
    print("="*50)
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(BASE_DIR, "vps_config.json")
    
    # 1. 尝试读取本地已有的配置
    existing_config = load_existing_config(config_path)
    
    if existing_config:
        print("\n🔍 发现本地已保存的配置信息：")
        print(f"  [-] VPS IP地址 : {existing_config.get('host', '未设置')}")
        print(f"  [-] SSH 端口号 : {existing_config.get('port', 22)}")
        
        # 密码脱敏显示 (只显示星号)
        pwd = existing_config.get('password', '')
        print(f"  [-] root 密码  : {'*' * len(pwd) if pwd else '未设置'}")
        
        # 显示订阅链接 (过长的话截断显示)
        sub_url = existing_config.get('sub_url', '未设置')
        display_sub = sub_url if len(sub_url) < 40 else sub_url[:30] + "..." + sub_url[-5:]
        print(f"  [-] 订阅链接   : {display_sub}")
        print("-" * 50)
        
        choice = input("\n以上信息是否仍然正确？(输入 Y 保持不变并退出，输入 N 重新配置) [默认Y]: ").strip().upper()
        if choice != 'N':
            print("\n✅ 配置未修改。您可以直接运行主程序了！")
            input("\n按回车键退出向导...")
            return
            
        print("\n--- 开始重新配置 (若某项无需修改，可直接回车跳过) ---")
    else:
        print("未找到本地配置或配置为空，请输入您的信息：\n")

    # 2. 交互式获取新配置 (带默认值逻辑)
    def get_input(prompt, default_val=""):
        val = input(prompt).strip()
        return val if val else default_val

    # 提取旧值作为参考
    old_host = existing_config.get('host', '') if existing_config else ''
    old_port = str(existing_config.get('port', '22')) if existing_config else '22'
    old_pwd = existing_config.get('password', '') if existing_config else ''
    old_sub = existing_config.get('sub_url', '') if existing_config else ''

    # 逐项询问
    host_prompt = f"1. 请输入 VPS 的 IP 地址 {f'[回车保持: {old_host}]' if old_host else '(如 154.23.xxx.xxx)'}: "
    host = get_input(host_prompt, old_host)

    port_prompt = f"2. 请输入 SSH 端口号 {f'[回车保持: {old_port}]' if old_port else '(直接回车默认是 22)'}: "
    port = get_input(port_prompt, old_port)

    pwd_prompt = f"3. 请输入服务器 root 密码 {f'[回车保持旧密码]' if old_pwd else ''}: "
    password = get_input(pwd_prompt, old_pwd)

    sub_prompt = f"4. 请输入节点订阅链接 {f'[回车保持旧链接]' if old_sub else ''}: "
    sub_url = get_input(sub_prompt, old_sub)

    # 3. 组装并保存配置
    config = {
        "host": host,
        "port": int(port) if port.isdigit() else 22,
        "user": "root",
        "password": password,
        "sub_url": sub_url
    }

    with open(config_path, 'w', encoding='utf-8') as f:
        # ensure_ascii=False 保证如果链接或内容里有中文，JSON中不会乱码
        json.dump(config, f, indent=4, ensure_ascii=False)

    print("\n✅ 太棒了！服务器及订阅配置已成功保存！")
    print("以后只需要运行 run_all.py 即可全自动执行。")
    print("如需再次修改，随时双击运行 1-首次配置服务器.bat 即可。")
    
    input("\n按回车键退出向导...")

if __name__ == "__main__":
    run_setup()