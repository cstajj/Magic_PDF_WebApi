from pydantic import BaseModel, Field
from typing import TypeVar, Generic, Optional, List

# 使用 TypeVar 来定义一个泛型类型 T
# 这允许我们的 data 字段可以是任何类型
T = TypeVar('T')

class ApiRes(BaseModel, Generic[T]):
    """
    一个标准的 API 响应模型，支持泛型。
    """
    # 状态码，True 表示成功, False 表示失败
    success: bool = Field(..., description="请求是否成功")
    
    # 提示信息
    message: str = Field(..., description="给用户的提示信息")
    
    # 返回的具体数据，可以是任何类型，也可以是 None
    # 使用 Optional[T] 表示 data 字段可以是 T 类型或者 None
    data: Optional[T] = Field(None, description="响应的具体数据负载")

    
    # ---- 为了方便使用，我们可以添加几个静态工厂方法 ----
    
    @staticmethod
    def create(data: T, msg: str = "操作成功") -> "ApiResponse[T]":
        """
        创建一个成功的响应实例。
        """
        return ApiRes(success=True, message=msg, data=data)

    @staticmethod
    def error(msg: str = "操作失败", data: T = None) -> "ApiResponse[T]":
        """
        创建一个失败的响应实例。
        """
        return ApiRes(success=False, message=msg, data=data)