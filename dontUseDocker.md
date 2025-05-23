# 不使用docker运行 需要安装这些
# 安装migic-pdf
pip install -U magic-pdf[full] --extra-index-url https://wheels.myhloli.com -i https://pypi.tuna.tsinghua.edu.cn/simple
# 安装安装模型支持
pip install modelscope
# 运行此py文件安装模型
python Scripts/download_models.py
# 运行
uvicorn main:app --host 127.0.0.1 --port 8000