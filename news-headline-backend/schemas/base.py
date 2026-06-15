# ============================================================
# 公共基础 Schema
# ============================================================
# 思路：多个模块都会用到的公共字段抽成一个 Base 类，谁用谁继承。
#
# 比如新闻列表、收藏列表、缓存读写都需要 id/title/image 这些字段，
# 不抽的话每个地方都要重复定义一遍。
# ============================================================

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class NewsItemBase(BaseModel):
    """
    新闻条目的公共字段。
    收藏列表的 FavoriteNewsItemResponse 继承它，缓存写入也用它的 model_dump。

    使用方：
        - schemas/favorite.py → FavoriteNewsItemResponse 继承
        - crud/news_cache.py   → ORM 转字典写入 Redis
    """
    id: int
    title: str
    description: Optional[str] = None
    image: Optional[str] = None
    author: Optional[str] = None
    category_id: int = Field(alias="categoryId")
    views: int
    publish_time: Optional[datetime] = Field(None, alias="publishedTime")

    model_config = ConfigDict(
        from_attributes=True,     # 允许从 ORM 对象取值
        populate_by_name=True     # 同时支持 Python 字段名和 alias 别名
    )