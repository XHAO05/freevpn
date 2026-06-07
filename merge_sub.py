name: 自动聚合节点并同步

on:
  push:
    branches: [ "main" ] # 当你修改代码时触发
  schedule:
    - cron: '0 */4 * * *' # 【核心：定时器】每 4 小时自动在云端运行一次 (UTC时间)

jobs:
  build:
    runs-on: ubuntu-latest # 使用 Linux 云服务器运行

    steps:
    - name: 检出仓库代码
      uses: actions/checkout@v3

    - name: 安装 Python 环境
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: 安装 requests 依赖库
      run: |
        pip install requests

    - name: 运行聚合脚本
      run: |
        python merge_sub.py

    - name: 将生成的 txt 文件自动提交回仓库
      run: |
        git config --local user.email "actions@github.com"
        git config --local user.name "GitHub Actions"
        git add my_custom_sub.txt
        # 只有在文件内容确实发生变化时才提交，防止无意义的报错
        git diff --cached --quiet || (git commit -m "自动更新节点池 [$(date '+%Y-%m-%d %H:%M:%S')]" && git push)
