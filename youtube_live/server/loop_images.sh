#!/bin/bash

# 只要不终止，就一直循环
while true; do
    # 遍历 images 文件夹下的所有 png 文件
    for img in /root/live/images/*.png; do
        
        # 防错机制：如果文件夹是空的，休息 10 秒再说
        if [ ! -f "$img" ]; then
            echo "未找到图片，等待上传..."
            sleep 10
            break
        fi

        # 【核心修复区：使用 cat 原地覆盖内容】
        # 这样做不会改变 current.png 的底层文件编号(Inode)，FFmpeg 就能瞬间捕捉到画面变化
        cat "$img" > /root/live/current.png

        echo "[$(date '+%H:%M:%S')] 切换图片 -> $(basename "$img")"

        # 停留时间：300秒 = 5分钟
        sleep 300
    done
done