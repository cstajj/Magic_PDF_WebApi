from fastapi import FastAPI,UploadFile, File, HTTPException,Form,APIRouter
from loguru import logger
from datetime import datetime

from db.database import db_manager
from utils.tokenVerify import verify_token
from utils.api.response_models import ApiRes

# 这个 router 只关心文件转换
router = APIRouter(
    prefix="/system",
    tags=["System"]
)

@router.get("/checkdb")
async def checkdb():
    try:
        result = db_manager.scalar("select 'Hello from DB! NowTime:'+format(getdate(),'yyyy-MM-dd HH:mm:ss') ")
        return ApiRes.create(result)
    except Exception as e:
        logger.exception(f"处理失败: {str(e)}")
        return ApiRes.error(f"处理失败: {str(e)}")