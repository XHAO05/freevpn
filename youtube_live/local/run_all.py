import subprocess
import sys
import os

def main():
    # 获取当前脚本所在的文件夹路径，确保执行目录正确
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 按照你需要的先后顺序，把脚本名字放进列表里
    scripts_to_run = ["extract_nodes.py", "batch_render.py", "upload_to_vps.py"]
    
    for script in scripts_to_run:
        script_path = os.path.join(current_dir, script)
        print(f"========== 正在启动: {script} ==========")
        
        # 使用 subprocess 运行脚本，sys.executable 会自动调用当前环境的 python.exe
        # cwd=current_dir 确保了它们在这个文件夹下运行，不会找不到配套图片
        result = subprocess.run([sys.executable, script_path], cwd=current_dir)
        
        # 错误拦截机制：如果当前脚本崩溃或报错，立刻停止，不执行下一个
        if result.returncode != 0:
            print(f"\n❌ 严重错误: {script} 执行失败！流水线已强制中断。")
            sys.exit(result.returncode)
            
        print(f"========== {script} 执行完毕 ==========\n")

    print("✅ 所有节点提取与渲染任务已全部完成！")

if __name__ == "__main__":
    main()