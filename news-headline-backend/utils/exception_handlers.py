# ============================================================
# 异常处理器注册
# ============================================================
# 思路：把所有异常处理函数收拢到一个函数里，main.py 只需要调一行。
#
# 注册顺序必须遵守：子类在前，父类在后；具体在前，抽象在后。
# FastAPI 从上往下匹配，匹配到第一个就停。
#
# 如果 Exception 放第一个 → 所有异常都被它吃掉 → 后面的全白写。
# ============================================================

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# 导入所有处理函数
from utils.exception import (
    http_exception_handler,
    integrity_error_handler,
    sqlalchemy_error_handler,
    general_exception_handler
)


def register_exception_handlers(app):
    """
    注册全局异常处理器

    调用方式（在 main.py 中）：
        from utils.exception_handlers import register_exception_handlers
        register_exception_handlers(app)
    """
    app.add_exception_handler(HTTPException, http_exception_handler)    # ① 业务异常（最具体）
    app.add_exception_handler(IntegrityError, integrity_error_handler)  # ② 数据完整性约束
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler) # ③ 数据库错误
    app.add_exception_handler(Exception, general_exception_handler)     # ④ 兜底（范围最大）
