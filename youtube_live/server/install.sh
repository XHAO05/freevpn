#!/bin/bash
echo "================================================="
echo "  🚀 科技小V - 24小时无人直播系统 终极自动化部署"
echo "================================================="

# 1. 自动从 GitHub 远程拉取所有必要组件
echo "--> 正在从云端拉取最新版本的直播组件..."
LIVE_DIR="/root/live"
mkdir -p $LIVE_DIR/images
BASE_URL="https://raw.githubusercontent.com/XHAO05/freevpn/main/youtube_live/server"

# 自动下载所有文件到 /root/live/
wget -qO $LIVE_DIR/run_stream.sh $BASE_URL/run_stream.sh
wget -qO $LIVE_DIR/loop_images.sh $BASE_URL/loop_images.sh
wget -qO $LIVE_DIR/bgm.mp3 $BASE_URL/bgm.mp3
wget -qO $LIVE_DIR/current.png $BASE_URL/current.png
wget -qO $LIVE_DIR/change_key.sh $BASE_URL/change_key.sh

# 2. 交互式获取用户的 YouTube 推流配置
echo -e "\n=========================================================="
echo -e "准备配置推流信息..."
echo -e "请登录 YouTube 直播后台获取您的【推流地址】和【直播码】"
echo -e ""
echo -e "【示例格式参考】"
echo -e "推流地址通常为: rtmp://a.rtmp.youtube.com/live2"
echo -e "推流直播码通常为: abcd-efgh-ijkl-mnop-qrst"
echo -e "==========================================================\n"

# 提示输入推流地址
read -p "▶ 请粘贴您的 YouTube 推流地址 (回车默认使用 rtmp://a.rtmp.youtube.com/live2): " user_stream_url
if [ -z "$user_stream_url" ]; then
    user_stream_url="rtmp://a.rtmp.youtube.com/live2"
fi

# 提示输入直播码并进行非空验证
read -p "▶ 请粘贴您的 YouTube 直播码 (格式如 xxxx-xxxx-xxxx-xxxx-xxxx): " user_stream_key
while [ -z "$user_stream_key" ]; do
    echo "⚠️ 错误：直播码不能为空，请重新输入！"
    read -p "▶ 请粘贴您的 YouTube 直播码: " user_stream_key
done

echo "✅ 直播信息已记录，继续下一步部署..."

# 3. 安装环境依赖
echo "--> 正在安装必要软件 (FFmpeg, Screen, 字体)..."
apt-get update -y
apt-get install ffmpeg screen fonts-dejavu-core -y

# 4. 配置脚本中的占位符
echo "--> 正在执行自动化配置..."
# 替换推流密钥
sed -i "s|REPLACE_ME|$user_stream_key|g" $LIVE_DIR/run_stream.sh
# 替换推流地址 (去掉了这行前面的注释符号，让它生效)
sed -i "s|URL_REPLACE_ME|$user_stream_url|g" $LIVE_DIR/run_stream.sh

# 5. 赋予执行权限
chmod +x $LIVE_DIR/*.sh

echo "================================================="
echo "✅ 完美！服务端环境已全自动部署并配置完毕！"
echo ""
echo "【如何开播？只需依次复制执行以下两行命令】"
echo "1. 启动画面轮播: screen -S swapper bash /root/live/loop_images.sh"
echo "2. 启动视频推流: screen -S stream bash /root/live/run_stream.sh"
echo "================================================="