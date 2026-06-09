import os
import json
import pandas as pd
import shutil
from PIL import Image, ImageDraw, ImageFont

def start_batch_render():
    print("正在初始化批量渲染引擎...")
    
    # --- 【清理防残留机制】彻底删除旧的成品图文件夹重建 ---
    output_dir = "live_images"
    if os.path.exists(output_dir):
        print(f"正在清理旧的图片文件夹: {output_dir}...")
        shutil.rmtree(output_dir) 
    os.makedirs(output_dir, exist_ok=True) 
    
    # 1. 加载坐标配置文件
    config_file = "render_config.json"
    if not os.path.exists(config_file):
        print("❌ 找不到 render_config.json，请先在调试器中保存配置！")
        return

    with open(config_file, 'r', encoding='utf-8') as f:
        cfg = json.load(f)

    # 2. 加载正确的表格和子表
    excel_file = "节点统计.xlsx" 
    if not os.path.exists(excel_file):
        print(f"❌ 找不到 {excel_file}！请检查文件名。")
        return
    
    try:
        df = pd.read_excel(excel_file, sheet_name="当天")
    except ValueError:
        print(f"❌ 在 {excel_file} 中找不到名为 '当天' 的子表格，请检查！")
        return

    # 3. 准备字体
    try:
        font = ImageFont.truetype(cfg['font_path'], cfg['font_size'])
    except:
        font = ImageFont.load_default()

    text_color = cfg.get('font_fill', '#000000')

    print(f"✅ 配置读取成功！开始为您生成 {len(df)} 张直播卡片...")
    print("-" * 40)

    # 4. 开始批量合成
    for index, row in df.iterrows():
        try:
            node_idx = str(index + 1).zfill(2) 
            
            # 【容错提取】防止单元格为空导致脚本崩溃
            ip_text = str(row.get('服务器IP', '未知IP')) if pd.notna(row.get('服务器IP')) else '未知IP'
            region_text = str(row.get('IP归属地', '未知地区')) if pd.notna(row.get('IP归属地')) else '未知地区'
            protocol_text = str(row.get('协议类型', '未知协议')) if pd.notna(row.get('协议类型')) else '未知协议'

            qr_path = f"qr_codes/node_{index}.png"

            # A. 铺上底图
            base_img = Image.open(cfg['bg_image']).copy()
            draw = ImageDraw.Draw(base_img)

            # B. 贴上二维码
            if os.path.exists(qr_path):
                qr_img = Image.open(qr_path)
                qr_size = cfg['qr_size']
                qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
                base_img.paste(qr_img, (cfg['qr_x'], cfg['qr_y']))
            else:
                print(f"   ⚠️ 第 {node_idx} 个节点找不到对应的二维码文件 {qr_path}，已跳过贴图。")

            # C. 印上文字
            draw.text((cfg['index_x'], cfg['index_y']), node_idx, fill=text_color, font=font)
            draw.text((cfg['ip_x'], cfg['ip_y']), ip_text, fill=text_color, font=font)
            draw.text((cfg['region_x'], cfg['region_y']), region_text, fill=text_color, font=font)
            draw.text((cfg['protocol_x'], cfg['protocol_y']), protocol_text, fill=text_color, font=font)

            # D. 保存成品图片
            output_filename = f"node_{node_idx}.png"
            output_path = os.path.join(output_dir, output_filename)
            base_img.save(output_path)
            # print(f"   -> 成功生成: {output_filename}") # 如果觉得刷屏可以保持注释

        except Exception as e:
            print(f"   ❌ 渲染第 {index + 1} 个节点时出错，已跳过。报错信息：{e}")
            continue

    print("-" * 40)
    print(f"🎉 全部搞定！请打开同目录下的【{output_dir}】文件夹查看您的直播成品图。")

if __name__ == "__main__":
    start_batch_render()