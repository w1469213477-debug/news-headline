from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from models.news import get_news_category
from models.news import get_news

# 新闻分类标签
async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100):
    smmt = select(get_news_category).offset(skip).limit(limit)
    result = await db.execute(smmt)
    return result.scalars().all()

# 新闻列表
async def get_news_list(db: AsyncSession, category_id: int ,skip: int = 0, limit: int = 10):
    # 查询指定分类下的所有新闻
    stmt = select(get_news).where(get_news.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

# 获取新闻数量
async def get_news_count(db: AsyncSession, category_id: int):
    stmt = select(func.count(get_news.id)).where(get_news.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one()

# 获取新闻详情
async def get_news_detail(db: AsyncSession, id: int):
    stmt = select(get_news).where(get_news.id == id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def increment_news_views(db: AsyncSession, id: int):
    stmt = update(get_news).where(get_news.id == id).values(views=get_news.views + 1)
    res = await db.execute(stmt)
    # 当前会话执行完提交
    await db.commit()

    # 更新 -> 检查数据库是否真的命中了数据 -> 命中了返回true
    return res.rowcount > 0

# 查找相关新闻
async def get_related_news(db: AsyncSession, id: int, category_id: int ,limit: int = 5):

    stmt = select(get_news).where( get_news.category_id == category_id,get_news.id != id).order_by(
        get_news.views.desc(),
        get_news.publish_time.desc()
    ).limit(limit)
    result = await db.execute(stmt)
    related_news =  result.scalars().all()
    # 列表推导式 推导出新闻的核心数据,然后再return
    return [{
        "id": news_detail.id,
        "title": news_detail.title,
        "image": news_detail.image,
        "author": news_detail.author,
        "publishTime": news_detail.publish_time,
        "categoryId": news_detail.category_id,
        "views": news_detail.views,
    } for news_detail in related_news]