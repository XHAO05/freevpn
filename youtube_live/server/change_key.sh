#!/bin/bash
echo "======================================"
echo "   🔄 科技小V - 一键更换推流地址和密钥"
echo "======================================"

echo "💡 提示：如果地址没变，直接按回车即可使用默认的 YouTube 地址。"
read -p "👉 请粘贴推流地址 (默认: rtmp://a.rtmp.youtube.com/live2): " new_url

# 如果用户直接按回车输入为空，则使用默认的 YouTube 推流地址
if [ -z "$new_url" ]; then
    new_url="rtmp://a.rtmp.youtube.com/live2"
fi
# 容错处理：自动移除链接末尾可能多带的斜杠 "/"
new_url=${new_url%/}

read -p "👉 请粘贴您新的 YouTube 直播码: " new_key

if [ -z "$new_key" ]; then
    echo "❌ 错误：直播码输入为空，操作已取消。"
    exit 1
fi

# 核心魔法升级版：无视原有错误格式，直接暴力替换 STREAM_URL 双引号内的所有内容
sed -i -E "s|STREAM_URL=\".*\"|STREAM_URL=\"$new_url/$new_key\"|g" /root/live/run_stream.sh

echo "✅ 完美！推流地址和直播码已成功更新到推流脚本中。"
echo "======================================"
echo "⚠️ 【最后一步：重启推流才能生效】"
echo "请依次执行以下命令重启画面："
echo "1. 进入推流控制台: screen -r stream"
echo "2. 掐断旧的推流: 按键盘 Ctrl + C"
echo "3. 启动新的推流: bash /root/live/run_stream.sh"
echo "4. 安全切回后台: 按 Ctrl + A，松开再按 D"
echo "======================================"