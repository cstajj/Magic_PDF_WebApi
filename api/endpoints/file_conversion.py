from fastapi import FastAPI,UploadFile, File, HTTPException,Form,APIRouter
import uuid
import os
from loguru import logger
from datetime import datetime

from magic_pdf.data.data_reader_writer import FileBasedDataWriter, FileBasedDataReader
from magic_pdf.data.dataset import PymuDocDataset
from magic_pdf.model.doc_analyze_by_custom_model import doc_analyze
from magic_pdf.config.enums import SupportedPdfParseMethod

from db.database import db_manager
from db.models import FileConvertRecord
from db.schemas import FileConvertRecordSchema
from utils.tokenVerify import verify_token
from utils.api.response_models import ApiRes
from utils.formatTime import getDateTime

router = APIRouter(
    prefix="/convert",
    tags=["File Conversion"]
)

@router.post("/pdf2mdnew")
async def pdf2mdnew(file: UploadFile = File(...),
                        timestamp: str = Form(...),
                        userId: str = Form(...),
                        token: str = Form(...)):
    try:
        if not verify_token(timestamp,userId,token):
            return ApiRes.error("验证失败")
        
        if not file.filename.lower().endswith('.pdf'):
            return ApiRes.error("只能上传PDF文件")

        # 准备目录结构
        __dir__ = os.path.dirname(os.path.abspath(__file__))
        upload_dir = os.path.join(__dir__, "pdfs")
        os.makedirs(upload_dir, exist_ok=True)

        # 生成安全且唯一的文件名
        filename = file.filename
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        pdf_file_path = os.path.join(upload_dir, unique_name)
        
        # 保存上传文件
        contents = await file.read()
        with open(pdf_file_path, "wb") as f:
            f.write(contents)

        record = FileConvertRecord(
            convertType=1,
            content="",
            resultPath="",
            originalFilePath=pdf_file_path,
            status=2,
            info=f"[{getDateTime()}]任务已创建",
            errorMessage= "",
            deleted=False,
            created=datetime.now()
        )
        with db_manager.get_session() as session:
            session.add(record)
            session.commit()
            session.refresh(record)

            record_schema = FileConvertRecordSchema.model_validate(record)
            return ApiRes.create(record_schema)
    except Exception as e:
        logger.exception(f"处理失败: {str(e)}")
        return ApiRes.error(f"处理失败: {str(e)}")


def get_subdirs(path):
    """获取指定路径下的所有直接子文件夹"""
    return [name for name in os.listdir(path)
            if os.path.isdir(os.path.join(path, name))]

@router.get("/pdf2mdgetallfile")
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

@router.get("/pdf2mdgetres")
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
    
@router.get("/logs")
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
