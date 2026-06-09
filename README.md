## VPS服务端:一键部署命令
```
wget -N https://raw.githubusercontent.com/XHAO05/freevpn/main/youtube_live/server/install.sh && bash install.sh
```

## 修改推流地址/秘钥命令
```
bash /root/youtube_live/server/change_key.sh
```
## 启动【换图引擎】：
```
# 看到打印出时间后，按 Ctrl + A，松开再按 D 隐藏到后台
screen -S swapper bash /root/live/loop_images.sh
```

## 启动【推流引擎】：
```
# 看到滚动的代码后，按 Ctrl + A，松开再按 D 隐藏到后台
screen -S stream bash /root/live/run_stream.sh
```

## 关闭推流命令：
```
killall ffmpeg
```

## 关闭screen会话命令：
```
killall screen
```

## 查看后台运行
```
screen -r swapper
```

```
screen -r stream
```

## 聚合订阅链接
```
https://raw.githubusercontent.com/XHAO05/freevpn/refs/heads/main/node_aggregator/sub1.txt
```

```
https://raw.githubusercontent.com/XHAO05/freevpn/refs/heads/main/node_aggregator/sub2.txt
```

```
https://raw.githubusercontent.com/XHAO05/freevpn/refs/heads/main/node_aggregator/sub3.txt
```

```
https://raw.githubusercontent.com/XHAO05/freevpn/refs/heads/main/node_aggregator/sub4.txt
```

```
https://raw.githubusercontent.com/XHAO05/freevpn/refs/heads/main/node_aggregator/sub5.txt
```
