# 当前版本直接运行
准备
1.复制exlaunch.json的内容到新的调试配置文件内
2.修改调试配置文件的[MINERU_TOOLS_CONFIG_JSON]节点为当前项目内[magic-pdf.json]文件的绝对路径
3.安装包：pip install -r requirements.txt 

运行
调试：工具栏 [运行]=>[启动调试] 或 F5
直接运行：uvicorn main:app --host 127.0.0.1 --port 8000




# 更新magic-pdf
# 安装migic-pdf
pip install -U magic-pdf[full] --extra-index-url https://wheels.myhloli.com -i https://pypi.tuna.tsinghua.edu.cn/simple
# 安装安装模型支持
pip install modelscope
# 运行此py文件安装模型
python Scripts/download_models.py
# 运行
uvicorn main:app --host 127.0.0.1 --port 8000
# 默认的配置文件为用户目录下的magic-pdf.json
# 默认的模型文件在运行项目的磁盘下的tmp文件夹下
# 固定包
pip freeze > requirements.txt

# 此操作会覆盖freeze结果
pip install pip-tools
pip-compile requirements.in 


