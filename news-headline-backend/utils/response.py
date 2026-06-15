# ============================================================
# 通用成功响应函数
# ============================================================
# 思路：把 {"code":200, "message":"...", "data":...} 这个重复的 JSON 壳
#       抽成一个函数，每个接口只需要传 message 和 data 即可。
#
# 使用方式（在路由中）：
#   from utils.response import success_response
#   return success_response("操作成功", pydantic对象)
# ============================================================

from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

def success_response(message: str, data=None):
    """
    通用成功响应外壳
    :param message: 提示信息，如 "用户注册成功"
    :param data:    响应数据，通常是一个 Pydantic 模型对象
    :return:        JSONResponse

    jsonable_encoder 的作用：
    把 ORM 对象、datetime、Decimal 等 Python 对象转成 JSON 兼容的字典/列表。
    不转的话，ORM 对象直接放 Response 里会报 "not JSON serializable"。
    """
    content = {
        "code": 200,       # 固定 200，表示成功
        "message": message, # 前端用来弹 toast
        "data": data        # 实际数据，由 Pydantic 模型定义结构
    }
    return JSONResponse(content=jsonable_encoder(content))
