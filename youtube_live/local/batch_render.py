import os
import json
import shutil
from PIL import Image, ImageDraw, ImageFont

def start_batch_render():
    # 统一读取 extract_nodes.py 生成的文件
    DATA_FILE = "nodes_info.json"
    if not os.path.exists(DATA_FILE):
        print(f"❌ 找不到 {DATA_FILE}！请先运行 extract_nodes.py。"); return

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        nodes = json.load(f)
    with open("render_config.json", 'r', encoding='utf-8') as f:
        cfg = json.load(f)

    output_dir = "live_images"
    if os.path.exists(output_dir): shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    font = ImageFont.truetype(cfg['font_path'], cfg['font_size'])
    
    for index, node in enumerate(nodes):
        node_idx = str(index + 1).zfill(2)
        qr_path = f"qr_codes/node_{index}.png"
        
        base_img = Image.open(cfg['bg_image']).copy()
        draw = ImageDraw.Draw(base_img)

        # 贴图与印字
        if os.path.exists(qr_path):
            qr_img = Image.open(qr_path).resize((cfg['qr_size'], cfg['qr_size']))
            base_img.paste(qr_img, (cfg['qr_x'], cfg['qr_y']))

        draw.text((cfg['index_x'], cfg['index_y']), node_idx, fill=cfg['font_fill'], font=font)
        draw.text((cfg['ip_x'], cfg['ip_y']), node.get('ip', '未知'), fill=cfg['font_fill'], font=font)
        draw.text((cfg['region_x'], cfg['region_y']), node.get('country', '未知'), fill=cfg['font_fill'], font=font)
        draw.text((cfg['protocol_x'], cfg['protocol_y']), node.get('protocol', '未知'), fill=cfg['font_fill'], font=font)

        base_img.save(os.path.join(output_dir, f"node_{node_idx}.png"))
        print(f"  [渲染成功] 第 {node_idx} 个节点: {node.get('country')}")

if __name__ == "__main__":
    start_batch_render()
    input("\n💡 按回车键退出...")