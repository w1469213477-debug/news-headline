from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_conf import get_db
from crud import history
from models.users import User
from schemas.history import HistoryAddRequest , HistoryResponse
from utils.auth import get_current_user
from utils.response import success_response


router = APIRouter(prefix="/api/history", tags=["history"])

# 添加历史记录
@router.post("/add")
async def add_history(
        data: HistoryAddRequest,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await history.add_history(db, user.id, data.news_id)
    return success_response(message="添加历史记录成功", data=result)

# 删除历史记录
@router.delete("/delete/{news_id}")
async def remove_history(
        news_id: int,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await history.delete_history(db, user.id, news_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="历史记录不存在"
        )

    return success_response(message="删除历史记录成功")


@router.get("/list")
async def get_history_list(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    rows, total = await history.get_history_list(db, user.id, page, page_size)
    history_list = [{
        **news.__dict__,
        "history_time": history_time,
        "history_id": history_id
    } for news, history_time, history_id in rows]
    has_more = total > page * page_size

    data = HistoryResponse(list=history_list, total=total, hasMore=has_more)
    return success_response(message="获取历史记录列表成功", data=data)

@router.delete("/clear")
async def clear_history(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    count = await history.remove_all_historys(db, user.id)
    return success_response(message=f"清空了{count}条记录")