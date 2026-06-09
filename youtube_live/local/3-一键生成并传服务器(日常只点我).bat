@echo off
chcp 65001
echo 正在启动全自动流水线...
python run_all.py
timeout /t 5