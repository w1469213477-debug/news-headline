from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, func, Integer, String, Index, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="添加时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")


class get_news_category(Base):
    __tablename__ = "news_category"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="分类ID")
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="分类名称")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="排序")

    def __repr__(self):
        return f"<get_news_category(id={self.id}, name={self.name}, sort_order={self.sort_order})>"

class get_news(Base):
    __tablename__ = "news"
    # 创建索引：提升查询速度 -> 创建索引
    __table_args__ = (
        Index('fk_name_category_idx', 'category_id'),#高频查询场景
        Index('idx_publish_time', 'publish_time'),#按发布时间排序
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="新闻ID")
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="新闻标题")
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=False, comment="新闻描述")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="新闻内容")
    image: Mapped[Optional[str]] = mapped_column(String(255), nullable=False, comment="新闻图片")
    author: Mapped[Optional[str]] = mapped_column(String(50), nullable=False, comment="新闻作者")
    category_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="新闻分类ID")
    views: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="新闻浏览量")
    publish_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="发布时间")

    # 拿当前场景需要的
    def __repr__(self):
        return f"<get_news(id={self.id}, title={self.title},  views={self.views})>"

