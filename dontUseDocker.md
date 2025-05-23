# 不使用docker运行 需要安装这些
pip install -U magic-pdf[full] --extra-index-url https://wheels.myhloli.com -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install modelscope
python Scripts/download_models.py