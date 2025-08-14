from sqlalchemy import Column, Integer, String, Numeric, DateTime, func,Boolean
from .database import ModelBase

class FileConvertRecord(ModelBase):
    __tablename__ = "AITra_FileConvertRecord"

    id = Column(Integer, primary_key=True, index=True)
    convertType = Column(Integer) # 转换类型 （1-pdf转md）
    content = Column(String) # 转换后内容
    resultPath = Column(String) # 转换后文件路径
    originalFilePath = Column(String) # 原文件路径
    startTime = Column(DateTime) # 开始时间
    endTime = Column(DateTime) # 结束时间
    status = Column(Integer) # 状态 （1-完成 2-未开始 3-进行中 4-失败）
    info = Column(String) # 信息
    errorMessage = Column(String) # 错误信息
    deleted = Column(Boolean) # 是否删除
    created = Column(DateTime) # 创建时间

    def __repr__(self):
        return f"<AITra_FileConvertRecord(id='{self.id}')>"