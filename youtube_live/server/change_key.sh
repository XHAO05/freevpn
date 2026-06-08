#!/bin/bash
echo "======================================"
echo "   🔄 科技小V - 一键更换直播密钥"
echo "======================================"

read -p "👉 请粘贴您新的 YouTube 直播码: " new_key

if [ -z "$new_key" ]; then
    echo "❌ 错误：输入为空，操作已取消。"
    exit 1
fi

# 核心魔法：使用正则精准替换 run_stream.sh 里的旧密钥
sed -i -E "s|rtmp://a.rtmp.youtube.com/live2/[^\"]*|rtmp://a.rtmp.youtube.com/live2/$new_key|g" /root/live/run_stream.sh

echo "✅ 完美！直播码已成功更新到推流脚本中。"
echo "======================================"
echo "⚠️ 【最后一步：重启推流才能生效】"
echo "请依次执行以下命令重启画面："
echo "1. 进入推流控制台: screen -r stream"
echo "2. 掐断旧的推流: 按键盘 Ctrl + C"
echo "3. 启动新的推流: bash /root/live/run_stream.sh"
echo "4. 安全切到后台: 按 Ctrl + A，松开再按 D"
echo "======================================"