# ============================================================
# 全局异常处理函数
# ============================================================
# 思路：和成功响应一样，把错误返回也统一成 {"code":..., "message":..., "data":...} 的 JSON 格式。
#
# FastAPI 机制：
#   app.add_exception_handler(异常类型, 处理函数)
#   当某处抛出该类型异常时，FastAPI 自动调用对应的处理函数，不用每个路由手写 try/except。
#
# 四个处理器，覆盖范围从小到大：
#   HTTPException      → 业务主动抛的（404 用户不存在、400 参数错误）
#   IntegrityError     → 数据库约束冲突（唯一键重复、外键不存在）
#   SQLAlchemyError    → 数据库其他错误（连接超时、语法错误）
#   Exception          → 兜底（上面都没接住的，比如代码 bug 导致的 TypeError）
#
# DEBUG_MODE：
#   开发时 True  → data 里返回 traceback，方便定位问题
#   上线后 False → data 为 None，不暴露内部细节
# ============================================================

import traceback

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette import status

# 开发模式：返回详细错误信息
# 生产模式：返回简化错误信息
DEBUG_MODE = True  # 教学项目保持开启


async def http_exception_handler(request: Request, exc: HTTPException):
    """
    处理 HTTPException（业务逻辑主动抛出的异常）

    示例：
        raise HTTPException(status_code=404, detail="用户不存在")
        raise HTTPException(status_code=400, detail="用户名已存在")

    返回：{"code": 404, "message": "用户不存在", "data": None}
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,   # HTTP 状态码就是业务错误码
            "message": exc.detail,     # 抛异常时写的提示信息
            "data": None               # 业务异常不需要额外数据
        }
    )


async def integrity_error_handler(request: Request, exc: IntegrityError):
    """
    处理数据库完整性约束错误（唯一键冲突 / 外键不存在等）

    常见场景：
        - 注册时用户名重复 → "用户名已存在"
        - 外键关联的数据被删了 → "关联数据不存在"
    """
    error_msg = str(exc.orig)  # 从原始 MySQL 错误信息中提取线索

    # 根据错误信息判断具体是哪种约束冲突
    if "username_UNIQUE" in error_msg or "Duplicate entry" in error_msg:
        detail = "用户名已存在"
    elif "FOREIGN KEY" in error_msg:
        detail = "关联数据不存在"
    else:
        detail = "数据约束冲突，请检查输入"

    # 开发模式下，data 里附带原始错误信息帮助调试
    error_data = None
    if DEBUG_MODE:
        error_data = {
            "error_type": "IntegrityError",
            "error_detail": error_msg,
            "path": str(request.url)
        }

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "code": 400,
            "message": detail,
            "data": error_data
        }
    )


async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    """
    处理 SQLAlchemy 数据库错误（连接超时、语法错误等）

    IntegrityError 是 SQLAlchemyError 的子类，但由于注册顺序（子类在前），
    IntegrityError 会先被 integrity_error_handler 接住，不会走到这里。
    """
    error_data = None
    if DEBUG_MODE:
        error_data = {
            "error_type": type(exc).__name__,       # 异常类名，如 "OperationalError"
            "error_detail": str(exc),                # 异常详细信息
            "traceback": traceback.format_exc(),     # 完整堆栈，定位代码位置
            "path": str(request.url)                 # 请求路径，方便复现
        }

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "数据库操作失败，请稍后重试",   # 不暴露细节给前端
            "data": error_data                       # 开发模式下有 traceback
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """
    兜底处理：所有上面没接住的异常（代码 bug、未知错误等）

    比如：TypeError、ValueError、AttributeError 等意料之外的错误。
    这些不应该发生，但万一发生了，至少前端收到的是 JSON，不是 HTML 堆栈。
    """
    error_data = None
    if DEBUG_MODE:
        error_data = {
            "error_type": type(exc).__name__,       # 异常类名
            "error_detail": str(exc),                # 异常信息
            "traceback": traceback.format_exc(),     # 完整堆栈
            "path": str(request.url)                 # 请求路径
        }

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "服务器内部错误",              # 对外统一说法
            "data": error_data
        }
    )
