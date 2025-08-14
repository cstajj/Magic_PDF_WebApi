from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FileConvertRecordSchema(BaseModel):
    id: int
    convertType: Optional[int] = None
    content: Optional[str] = None
    resultPath: Optional[str] = None
    originalFilePath: Optional[str] = None
    startTime: Optional[datetime] = None
    endTime: Optional[datetime] = None
    status: Optional[int] = None
    info: Optional[str] = None
    errorMessage: Optional[str] = None
    deleted: bool
    created: datetime

    class Config:
        from_attributes = True  # Pydantic V2