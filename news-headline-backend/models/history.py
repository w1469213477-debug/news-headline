from datetime import datetime

from sqlalchemy import Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from models.users import User
from models.news import get_news
from models.favorite import Base

class History(Base):
    """
    用户历史记录表ORM模型
    """
    __tablename__ = 'history'

    # 创建索引
    __table_args__ = (
        Index('fk_history_user_idx', 'user_id'),
        Index('fk_history_news_idx', 'news_id'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="历史记录ID")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(User.id),nullable=False,comment="用户ID")
    news_id: Mapped[int] = mapped_column(Integer, ForeignKey(get_news.id), nullable=False, comment="新闻ID")
    view_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="查看时间")

    def __repr__(self):
        return f"<History(id={self.id}, user_id={self.user_id}, news_id={self.news_id}), view_time={self.view_time})>"