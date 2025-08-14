from fastapi import APIRouter
from .endpoints import file_conversion,system

api_router = APIRouter(prefix="/v1")

# 引入所有模块
api_router.include_router(file_conversion.router)
api_router.include_router(system.router)
