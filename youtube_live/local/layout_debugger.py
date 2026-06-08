import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
import json
import os

# --- 核心：自动获取当前脚本所在目录 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- 拼接动态配置文件和资源路径 ---
CONFIG_FILE = os.path.join(BASE_DIR, "render_config.json")
BG_IMAGE_PATH = os.path.join(BASE_DIR, "template.png")  
QR_IMAGE_PATH = os.path.join(BASE_DIR, "qr_codes", "node_0.png") 
FONT_PATH = os.path.join(BASE_DIR, "msyh.ttc")
class LayoutDebugger:
    def __init__(self, root):
        self.root = root
        self.root.title("直播卡片布局可视化调试器 v3.0 (配置记忆版)")
        
        # 1. 检查底图文件是否存在
        if not os.path.exists(BG_IMAGE_PATH):
            messagebox.showerror("错误", f"找不到底图文件！请确保 {BG_IMAGE_PATH} 存在。")
            root.destroy()
            return
            
        self.orig_bg = Image.open(BG_IMAGE_PATH)
        self.orig_w, self.orig_h = self.orig_bg.size
        
        # 检查二维码样本，如果没有则创建一个临时空白图防止崩溃
        if os.path.exists(QR_IMAGE_PATH):
            self.orig_qr = Image.open(QR_IMAGE_PATH)
        else:
            messagebox.showwarning("警告", "找不到二维码样本文件，将使用灰色占位块代替预览。\n建议先跑一次 extract_nodes.py 生成二维码。")
            self.orig_qr = Image.new('RGB', (500, 500), color='gray')
        
        self.display_scale = 0.5 
        if self.orig_w > 1200:
            self.display_scale = 1200 / self.orig_w
            
        self.display_w = int(self.orig_w * self.display_scale)
        self.display_h = int(self.orig_h * self.display_scale)
        
        # 2. 初始默认坐标值
        default_values = {
            'qr_x': 600, 'qr_y': 208, 'qr_size': 337, 'font_size': 44,
            'index_x': 45, 'index_y': 917,
            'ip_x': 575, 'ip_y': 417,
            'region_x': 575, 'region_y': 489,
            'protocol_x': 575, 'protocol_y': 560
        }

        # 3. 核心功能：读取已有的配置文件覆盖默认值
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    saved_cfg = json.load(f)
                    for k in default_values.keys():
                        if k in saved_cfg:
                            default_values[k] = saved_cfg[k]
                print("✅ 成功加载已有坐标配置！")
            except Exception as e:
                print(f"⚠️ 读取配置文件出错，将使用默认坐标。原因: {e}")

        # 4. 初始化 Tkinter 变量
        self.vars = {k: tk.IntVar(value=v) for k, v in default_values.items()}
        
        self.setup_ui()
        self.update_composite()

    def setup_ui(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        canvas = tk.Canvas(main_frame, width=320)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        self.control_frame = tk.Frame(canvas, padx=10, pady=10)
        
        self.control_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.control_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # --- UI 控制滑块创建 ---
        tk.Label(self.control_frame, text="--- 二维码位置 ---", fg="blue", font=("", 10, "bold")).pack(pady=(0, 5))
        self.create_slider("QR X坐标", self.vars['qr_x'], 0, self.orig_w)
        self.create_slider("QR Y坐标", self.vars['qr_y'], 0, self.orig_h)
        self.create_slider("QR 尺寸", self.vars['qr_size'], 50, 800)
        
        tk.Label(self.control_frame, text="--- 字体设置 ---", fg="blue", font=("", 10, "bold")).pack(pady=(10, 5))
        self.create_slider("统一字号", self.vars['font_size'], 10, 100)
        
        tk.Label(self.control_frame, text="--- 节点序号 位置 ---", fg="#9C27B0", font=("", 10, "bold")).pack(pady=(10, 5))
        self.create_slider("序号 X", self.vars['index_x'], 0, self.orig_w)
        self.create_slider("序号 Y", self.vars['index_y'], 0, self.orig_h)

        tk.Label(self.control_frame, text="--- 服务器IP 位置 ---", fg="#E65100", font=("", 10, "bold")).pack(pady=(10, 5))
        self.create_slider("IP X", self.vars['ip_x'], 0, self.orig_w)
        self.create_slider("IP Y", self.vars['ip_y'], 0, self.orig_h)
        
        tk.Label(self.control_frame, text="--- 国家/地区 位置 ---", fg="#E65100", font=("", 10, "bold")).pack(pady=(10, 5))
        self.create_slider("地区 X", self.vars['region_x'], 0, self.orig_w)
        self.create_slider("地区 Y", self.vars['region_y'], 0, self.orig_h)

        tk.Label(self.control_frame, text="--- 协议类型 位置 ---", fg="#E65100", font=("", 10, "bold")).pack(pady=(10, 5))
        self.create_slider("协议 X", self.vars['protocol_x'], 0, self.orig_w)
        self.create_slider("协议 Y", self.vars['protocol_y'], 0, self.orig_h)
        
        save_btn = tk.Button(self.control_frame, text="保存最终配置", command=self.save_config, bg="#4CAF50", fg="white", font=("", 12, "bold"))
        save_btn.pack(side=tk.BOTTOM, fill=tk.X, pady=20)

        # --- 右侧预览 ---
        self.canvas_preview = tk.Canvas(self.root, width=self.display_w, height=self.display_h, bg="#2c2c2c")
        self.canvas_preview.pack(side=tk.RIGHT, expand=True, padx=10, pady=10)

    def create_slider(self, label, var, from_, to):
        frame = tk.Frame(self.control_frame)
        frame.pack(fill=tk.X, pady=2)
        tk.Label(frame, text=label, width=8, anchor=tk.W).pack(side=tk.LEFT)
        scale = tk.Scale(frame, from_=from_, to=to, orient=tk.HORIZONTAL, variable=var, command=lambda e: self.update_composite())
        scale.pack(side=tk.RIGHT, expand=True, fill=tk.X)

    def update_composite(self):
        base = self.orig_bg.copy()
        
        qr_size = self.vars['qr_size'].get()
        qr_reshaped = self.orig_qr.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
        base.paste(qr_reshaped, (self.vars['qr_x'].get(), self.vars['qr_y'].get()))
        
        draw = ImageDraw.Draw(base)
        font_size = self.vars['font_size'].get()
        try:
            font = ImageFont.truetype(FONT_PATH, font_size)
        except:
            font = ImageFont.load_default()
            
        text_color = "#000000" 
        
        draw.text((self.vars['index_x'].get(), self.vars['index_y'].get()), "01", fill=text_color, font=font)
        draw.text((self.vars['ip_x'].get(), self.vars['ip_y'].get()), "155.117.198.86", fill=text_color, font=font)
        draw.text((self.vars['region_x'].get(), self.vars['region_y'].get()), "美国 芝加哥", fill=text_color, font=font)
        draw.text((self.vars['protocol_x'].get(), self.vars['protocol_y'].get()), "trojan", fill=text_color, font=font)
        
        base_display = base.resize((self.display_w, self.display_h), Image.Resampling.NEAREST)
        self.photo = ImageTk.PhotoImage(base_display)
        self.canvas_preview.create_image(0, 0, image=self.photo, anchor=tk.NW)

    def save_config(self):
        config_data = {k: v.get() for k, v in self.vars.items()}
        # 这里统一写死为相对路径，保证跨设备通用
        config_data['bg_image'] = "template.png"
        config_data['font_path'] = FONT_PATH
        config_data['font_fill'] = "#000000" 
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
        messagebox.showinfo("成功", f"完美！所有坐标已保存到配置文件！\n下次打开将自动读取此布局。")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1200x700")
    app = LayoutDebugger(root)
    root.mainloop()