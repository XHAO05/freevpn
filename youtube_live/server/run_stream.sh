#!/bin/bash

# 这里使用了占位符，等待 install.sh 来动态替换它们
STREAM_URL="URL_REPLACE_ME/REPLACE_ME"

ffmpeg \
-re -f image2 -loop 1 -framerate 1 -i /root/live/current.png \
-re -stream_loop -1 -i /root/live/bgm.mp3 \
-map 0:v:0 -map 1:a:0 \
-vf "scale=1920:1080,format=yuv420p,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='%{localtime}':x=(w-text_w)/2:y=h-text_h-35:fontcolor=white:fontsize=50:shadowx=2:shadowy=2:shadowcolor=black@0.8" \
-r 30 \
-c:v libx264 -preset ultrafast -tune stillimage \
-b:v 3000k -maxrate 4000k -bufsize 8000k \
-g 60 -keyint_min 60 -sc_threshold 0 -pix_fmt yuv420p \
-threads 1 \
-c:a aac -b:a 128k -ar 44100 \
-f flv "$STREAM_URL"