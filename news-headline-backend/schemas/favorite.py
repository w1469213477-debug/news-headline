# ============================================================
# 收藏相关 Schema（请求体 & 响应体）
# ============================================================
# model_config 说明：
#   from_attributes=True  → 让 model_validate(orm对象) 能从 ORM 属性中取值
#   populate_by_name=True → 同时支持 Python 字段名和 alias 别名赋值
# ============================================================

from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from schemas.base import NewsItemBase


class FavoriteCheckResponse(BaseModel):
    """
    检查收藏状态响应
    前端请求：GET /api/favorite/check?newsId=1
    返回：{"code":200, "data":{"isFavorite": true}}
    """
    is_favorite: bool = Field(..., alias="isFavorite")
    #                     ^^^ 必填，没有默认值
    #                          ^^^^^^^^^^^ 前端驼峰命名


class FavoriteAddRequest(BaseModel):
    """
    添加收藏请求体
    前端发送：POST /api/favorite/add  Body: {"newsId": 123}
    """
    news_id: int = Field(..., alias="newsId")


class FavoriteNewsItemResponse(NewsItemBase):
    """
    收藏列表中的单条新闻。
    继承 NewsItemBase → 自动拥有 id/title/image/author 等新闻字段。
    额外加了收藏相关的字段（收藏ID、收藏时间）。
    """
    favorite_id: int = Field(alias="favoriteId")
    favorite_time: datetime = Field(alias="favoriteTime")

    model_config = ConfigDict(
        populate_by_name=True,   # 允许 "favorite_id" 和 "favoriteId" 同时生效
        from_attributes=True     # 允许从 ORM 对象取值
    )


class FavoriteListResponse(BaseModel):
    """
    收藏列表接口响应 data 结构。

    最终 JSON 形态：
    {
        "code": 200,
        "message": "收藏列表成功",
        "data": {
            "list": [{...单条收藏...}, ...],
            "total": 100,
            "hasMore": true
        }
    }
    """
    list: list[FavoriteNewsItemResponse]   # 单条收藏的列表
    total: int                             # 总数
    has_more: bool = Field(alias="hasMore")# 是否还有更多

    model_config = ConfigDict(
        populate_by_name=True,   # 允许 "has_more" 和 "hasMore" 同时生效
        from_attributes=True     # 允许从 ORM 对象取值
    )