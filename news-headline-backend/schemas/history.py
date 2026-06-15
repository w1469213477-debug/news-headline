from datetime import datetime
from pydantic import BaseModel, Field
from pydantic import BaseModel, Field, ConfigDict

from schemas.base import NewsItemBase

# 添加历史记录
class HistoryAddRequest(BaseModel):
    news_id: int = Field(..., alias="newsId")


# 规划两个类： 一个是新闻模型类 + 收藏的模型类
class HistoryItemResponse(NewsItemBase):
    history_id: int = Field(alias="historyId")
    history_time: datetime = Field(alias="historyTime")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )


# 收藏列表接口响应模型类
class HistoryResponse(BaseModel):
    list: list[HistoryItemResponse]
    total: int
    has_more: bool = Field(alias="hasMore")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )