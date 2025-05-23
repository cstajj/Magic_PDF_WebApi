from fastapi import FastAPI,UploadFile, File, HTTPException
import uuid
import os
from loguru import logger
from datetime import datetime

from magic_pdf.data.data_reader_writer import FileBasedDataWriter, FileBasedDataReader
from magic_pdf.data.dataset import PymuDocDataset
from magic_pdf.model.doc_analyze_by_custom_model import doc_analyze
from magic_pdf.config.enums import SupportedPdfParseMethod

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "Azure"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/pdf2md2")
def pdf2md2(qpath):
    try:
        # args
        __dir__ = os.path.dirname(os.path.abspath(__file__))
        if qpath=="":
            pdf_file_name = os.path.join(__dir__, "pdfs", "t1.pdf")  # replace with the real pdf path
        elif qpath == "1":
            test = "123"+1
        else:
            pdf_file_name = os.path.join(__dir__, "pdfs", qpath)  # replace with the real pdf path
        name_without_extension = os.path.basename(pdf_file_name).split('.')[0]
        
        # prepare env
        local_image_dir = os.path.join(__dir__, "output", name_without_extension, "images")
        local_md_dir = os.path.join(__dir__, "output", name_without_extension)
        image_dir = str(os.path.basename(local_image_dir))
        os.makedirs(local_image_dir, exist_ok=True)

        ex = "no"
        if os.path.exists(pdf_file_name):
            ex = "yes"

        print("执行成功："+ex)

        return {"status": ex+ " ok !"}
    except Exception as e:
        print("执行错误："+str(e))
        return {"status": "error:"+str(e)}


@app.get("/pdf2md")
def pdf2md(qfilename):
    try:
        log("pdf2md：进入："+qfilename)
        # args
        __dir__ = os.path.dirname(os.path.abspath(__file__))
        pdf_file_name = os.path.join(__dir__, "pdfs", qfilename+".pdf")  # replace with the real pdf path
        name_without_extension = os.path.basename(pdf_file_name).split('.')[0]

        # prepare env
        local_image_dir = os.path.join(__dir__, "output", name_without_extension, "images")
        local_md_dir = os.path.join(__dir__, "output", name_without_extension)
        image_dir = str(os.path.basename(local_image_dir))
        os.makedirs(local_image_dir, exist_ok=True)

        logger.info("pdf2md 1")
        log("pdf2md：pdf2md1")

        image_writer, md_writer = FileBasedDataWriter(local_image_dir), FileBasedDataWriter(local_md_dir)

        logger.info("pdf2md 2")
        log("pdf2md：pdf2md2")

        # read bytes
        reader1 = FileBasedDataReader("")
        pdf_bytes = reader1.read(pdf_file_name)  # read the pdf content

        # proc
        ## Create Dataset Instance
        ds = PymuDocDataset(pdf_bytes)
        log("pdf2md：pdf2md3")
        ## inference
        if ds.classify() == SupportedPdfParseMethod.OCR:
            infer_result = ds.apply(doc_analyze, ocr=True)

            ## pipeline
            pipe_result = infer_result.pipe_ocr_mode(image_writer)

        else:
            infer_result = ds.apply(doc_analyze, ocr=False)

            ## pipeline
            pipe_result = infer_result.pipe_txt_mode(image_writer)

        ### get model inference result
        model_inference_result = infer_result.get_infer_res()
        log("pdf2md：get model inference result")
        ### draw layout result on each page
        pipe_result.draw_layout(os.path.join(local_md_dir, f"{name_without_extension}_layout.pdf"))

        logger.info("pdf2md 4")
        log("pdf2md：pdf2md4")

        ### draw spans result on each page
        pipe_result.draw_span(os.path.join(local_md_dir, f"{name_without_extension}_spans.pdf"))

        ### get markdown content
        md_content = pipe_result.get_markdown(image_dir)
        logger.error("md_content:"+md_content)
        ### dump markdown
        pipe_result.dump_md(md_writer, f"{name_without_extension}.md", image_dir)
        logger.info("pdf2md 5")
        log("pdf2md：pdf2md5:"+md_content)
        return {"status": "ok !"+md_content}
    except Exception as e:
        log("pdf2md：pdf2md error"+str(e))
        logger.exception(e)
        print("执行错误："+str(e))
        return {"status": "error2:"+str(e)}

@app.post("/pdf2mdUpload")
async def pdf2mdUpload(file: UploadFile = File(...)):
    try:
        log("pdf2mdUpload:进入")
        # 确保上传的是PDF文件
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="只能上传PDF文件")

        # 准备目录结构
        __dir__ = os.path.dirname(os.path.abspath(__file__))
        upload_dir = os.path.join(__dir__, "pdfs")
        os.makedirs(upload_dir, exist_ok=True)

        # 生成安全且唯一的文件名
        filename = file.filename
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        pdf_file_path = os.path.join(upload_dir, unique_name)
        
        log("pdf2mdUpload:unique_name："+unique_name)

        # 保存上传文件
        contents = await file.read()
        with open(pdf_file_path, "wb") as f:
            f.write(contents)

        # 准备处理参数
        name_without_extension = os.path.splitext(unique_name)[0]
        
        # 准备输出目录
        local_image_dir = os.path.join(__dir__, "output", name_without_extension, "images")
        local_md_dir = os.path.join(__dir__, "output", name_without_extension)
        image_dir = str(os.path.basename(local_image_dir))
        os.makedirs(local_image_dir, exist_ok=True)

        log("pdf2mdUpload:local_image_dir:"+local_image_dir)

        # 初始化写入器
        image_writer, md_writer = FileBasedDataWriter(local_image_dir), FileBasedDataWriter(local_md_dir)

        # 读取PDF内容
        reader1 = FileBasedDataReader("")
        pdf_bytes = reader1.read(pdf_file_path)

        # 创建数据集实例
        ds = PymuDocDataset(pdf_bytes)

        # 处理流程
        if ds.classify() == SupportedPdfParseMethod.OCR:
            infer_result = ds.apply(doc_analyze, ocr=True)
            pipe_result = infer_result.pipe_ocr_mode(image_writer)
        else:
            infer_result = ds.apply(doc_analyze, ocr=False)
            pipe_result = infer_result.pipe_txt_mode(image_writer)
        log("pdf2mdUpload:处理流程")
        # 获取处理结果
        model_inference_result = infer_result.get_infer_res()
        log("pdf2mdUpload:获取处理结果")
        # 绘制布局结果
        pipe_result.draw_layout(os.path.join(local_md_dir, f"{name_without_extension}_layout.pdf"))
        log("pdf2mdUpload:绘制布局结果")
        # 绘制span结果
        pipe_result.draw_span(os.path.join(local_md_dir, f"{name_without_extension}_spans.pdf"))
        log("pdf2mdUpload:绘制span结果")
        # 生成Markdown内容
        md_content = pipe_result.get_markdown(image_dir)
        pipe_result.dump_md(md_writer, f"{name_without_extension}.md", image_dir)

        # 返回结果（可根据需要返回下载链接）
        return {
            "status": "success",
            "markdown": md_content,
            "download_url": f"/output/{name_without_extension}/{name_without_extension}.md"
        }
        
    except Exception as e:
        log("pdf2mdUpload：error"+str(e))
        logger.exception(f"处理失败: {str(e)}")
        # 清理可能产生的临时文件
        if 'pdf_file_path' in locals() and os.path.exists(pdf_file_path):
            os.remove(pdf_file_path)
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")

def get_subdirs(path):
    """获取指定路径下的所有直接子文件夹"""
    return [name for name in os.listdir(path)
            if os.path.isdir(os.path.join(path, name))]

@app.get("/pdf2mdgetallfile")
async def pdf2mdgetallfile():
    try:
        # 准备目录结构
        __dir__ = os.path.dirname(os.path.abspath(__file__))
        upload_dir = os.path.join(__dir__, "output")
        subdirs =  get_subdirs(upload_dir)
        return {
            "status": "success",
            "markdown": subdirs,
        }
    except Exception as e:
        logger.exception(f"处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")

@app.get("/pdf2mdgetres")
async def pdf2mdgetres(filename,folder):
    try:
        # 准备目录结构
        __dir__ = os.path.dirname(os.path.abspath(__file__))
        upload_dir = os.path.join(__dir__, "output")
        pdf_file_folder_path = os.path.join(upload_dir, folder)
        pdf_file_path = os.path.join(pdf_file_folder_path, filename)
        
        if os.path.exists(pdf_file_path) == False:
            return {
                "status": "error",
                "msg":pdf_file_path+"文件不存在"
            }
        mdStr = ""
        with open(pdf_file_path, 'r', encoding='utf-8') as f:
            mdStr = f.read()
        return {
            "status": "success",
            "data":mdStr
        }
    except Exception as e:
        logger.exception(f"处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")

@app.get("/logs")
async def logs():
    try:
        # 准备目录结构
        __dir__ = os.path.dirname(os.path.abspath(__file__))
        upload_dir = os.path.join(__dir__, "output")
        filename = os.path.join(upload_dir, "example.txt")
        
        if os.path.exists(filename) == False:
            return {
                "status": "error",
                "msg":filename+"文件不存在"
            }
        mdStr = ""
        with open(filename, 'r', encoding='utf-8') as f:
            mdStr = f.read()
        return {
            "status": "success",
            "data":mdStr
        }
    except Exception as e:
        logger.exception(f"处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")
    
def log(str):
    try:
        __dir__ = os.path.dirname(os.path.abspath(__file__))
        upload_dir = os.path.join(__dir__, "output")
        filepath = os.path.join(upload_dir, "example.txt")
        current_time = datetime.now()
        time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
        with open(filepath, "a", encoding="utf-8") as file:
            file.write("["+time_str + "]"+str + "\r\n")
    except PermissionError:
        print("无权限写入文件！")
    except Exception as e:
        print(f"发生错误：{e}")