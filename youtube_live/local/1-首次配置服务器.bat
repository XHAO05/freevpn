@echo off
color 0A

echo =======================================================
echo   [INFO] Installing Python requirements via mirror...
echo   Please wait, this may take a minute.
echo =======================================================

python -m pip install pandas paramiko openpyxl "qrcode[pil]" pillow requests -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo =======================================================
echo   [SUCCESS] Environment is ready! Starting setup...
echo =======================================================
echo.

python init_setup.py

echo.
echo =======================================================
echo   [SUCCESS] Setup complete! Starting main program...
echo =======================================================
pause

python run_all.py

pause