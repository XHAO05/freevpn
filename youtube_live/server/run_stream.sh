#!/bin/bash

# 这里使用了占位符，等待 install.sh 来动态替换它们
STREAM_URL="URL_REPLACE_ME/REPLACE_ME"

# 加入 while true 死循环，打造断线自动重连的“不死鸟”守护进程
while true; do
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 启动推流进程..."
    
    ffmpeg \
    -re -f image2 -loop 1 -framerate 1 -i /root/live/current.png \
    -re -stream_loop -1 -i /root/live/bgm.mp3 \
    -map 0:v:0 -map 1:a:0 \
    -vf "scale=1920:1080,format=yuv420p,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='%{localtime}':x=(w-text_w)/2:y=h-text_h-35:fontcolor=white:fontsize=50:shadowx=2:shadowy=2:shadowcolor=black@0.8" \
    -r 30 \
    -c:v libx264 -preset ultrafast -tune stillimage \
    -b:v 1500k -maxrate 2000k -bufsize 4000k \
    -g 60 -keyint_min 60 -sc_threshold 0 -pix_fmt yuv420p \
    -threads 1 \
    -c:a aac -b:a 128k -ar 44100 \
    -drop_pkts_on_overflow 1 -flvflags no_duration_filesize \
    -f flv "$STREAM_URL"
    
    # 如果 FFmpeg 运行结束或异常崩溃，会走到下面这两行
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️ 推流意外中断，3 秒后自动尝试重连..."
    sleep 3
done