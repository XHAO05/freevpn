import paramiko
import os
import json

def upload_to_vps():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(BASE_DIR, "vps_config.json")

    # 1. 安全拦截：如果没有配置文件，提示先去配置
    if not os.path.exists(config_path):
        print("❌ 找不到服务器配置文件！请先双击运行 init_setup.py 进行初始设置。")
        return

    # 2. 读取配置文件中的敏感信息
    with open(config_path, 'r', encoding='utf-8') as f:
        vps_cfg = json.load(f)

    host = vps_cfg['host']
    port = vps_cfg['port']
    user = vps_cfg['user']
    password = vps_cfg['password']
    
    local_dir = os.path.join(BASE_DIR, "live_images")
    remote_dir = '/root/live/images/'

    # 3. 开始执行上传逻辑
    print(f"正在建立与 VPS ({host}) 的加密连接...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(host, port, user, password, timeout=10)
        
        print("连接成功！正在清理远程旧图片...")
        ssh.exec_command(f"rm -f {remote_dir}*.png")
        
        print("清理完毕，开始同步最新节点图...")
        sftp = ssh.open_sftp()
        
        if not os.path.exists(local_dir):
            print(f"❌ 找不到本地图片文件夹: {local_dir}")
            return

        upload_count = 0
        for file in os.listdir(local_dir):
            if file.endswith('.png'):
                local_path = os.path.join(local_dir, file)
                remote_path = remote_dir + file
                sftp.put(local_path, remote_path)
                print(f"  -> 成功上传: {file}")
                upload_count += 1
                
        sftp.close()
        print(f"✅ 完美！共同步了 {upload_count} 张直播图片！")
        
    except Exception as e:
        print(f"❌ 上传过程发生严重错误: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    upload_to_vps()