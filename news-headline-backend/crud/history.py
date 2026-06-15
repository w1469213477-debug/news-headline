from datetime import datetime

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.history import History
from models.news import get_news

# 添加/更新历史浏览记录（存在则刷新时间，不存在则新增）
async def add_history(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    # 先盲删（存在就删，不存在也不报错），再插入新记录
    await db.execute(
        delete(History).where(
            History.user_id == user_id,
            History.news_id == news_id
        )
    )
    history = History(user_id=user_id, news_id=news_id)
    db.add(history)
    await db.commit()
    await db.refresh(history)
    return history

async def delete_history(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    """
    删除历史记录
    :param db:
    :param user_id:
    :param news_id:
    :return:
    """
    stmt = delete(History).where(
        History.user_id == user_id,
        History.news_id == news_id
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0

# 获取历史记录列表：获取的是某个用户的收藏列表 + 分页功能
async def get_history_list(
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        page_size: int = 10
):
    count_query = select(func.count()).where(History.user_id == user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()
    offset = (page - 1) * page_size
    query = (select(get_news, History.view_time.label("history_time"), History.id.label("history_id"))
             .join(History, History.news_id == get_news.id)
             .where(History.user_id == user_id)
             .order_by(History.view_time.desc())
             .offset(offset).limit(page_size)
             )
    result = await db.execute(query)
    rows = result.all()
    return rows, total

async def remove_all_historys(
        db: AsyncSession,
        user_id: int
):
    stmt = delete(History).where(History.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()

    # 返回一个删除的数量
    return result.rowcount or 0