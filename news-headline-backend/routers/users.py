# ============================================================
# 用户路由（注册 / 登录 / 个人资料）
# ============================================================
# 每个接口的处理流程固定三步：
#   ① 取参数 → ② 调 crud → ③ 组装响应
#
# 封装后的响应写法（固定套路）：
#   pydantic_obj = XxxSchema.model_validate(orm对象)
#   return success_response("提示信息", pydantic_obj)
# ============================================================

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from crud import users
from models.users import User
from schemas.users import UsersRequest, UserInfoResponse, UserAuthResponse, UserUpdateRequest, UserChangePasswordRequest
from utils.auth import get_current_user
from utils.response import success_response   # ← 通用成功响应外壳

from config.db_conf import get_db

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/register")
async def register(
        user_data: UsersRequest,                     # ← 步骤①：接收前端 JSON
        db: AsyncSession = Depends(get_db)
):
    # """
    # 注册接口
    # 流程：验证用户名是否存在 → 创建用户 → 生成 token → 返回认证信息
    # """

    # 步骤②：调 crud 层处理业务逻辑
    existing_user = await users.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已存在"
        )

    user = await users.create_user(db, user_data)
    token = await users.create_token(db, user.id)

    # 步骤③：组装响应（封装套路 ↓）
    # 第1步：ORM 对象 → Pydantic 对象
    user_info = UserInfoResponse.model_validate(user)
    #                         ^^^^^^^^^^^^^^
    #                         把数据库 user 对象转成 Pydantic 模型，
    #                         自动过滤掉 password 等不该返回的字段

    # 第2步：组装最终的 data 结构
    response = UserAuthResponse(token=token, userInfo=user_info)

    # 第3步：扔进统一外壳返回
    return success_response("用户注册成功", response)
    #      ^^^^^^^^^^^^^^^^
    #      外壳自动包 {"code":200, "message":"...", "data":...}

@router.post("/login")
async def login(
        user_data: UsersRequest,
        db: AsyncSession = Depends(get_db)
):
    user = await users.authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名或密码错误"
        )
    token = await users.create_token(db, user.id)
    response_date = UserAuthResponse(token=token, userInfo=UserInfoResponse.model_validate(user))
    return success_response("用户登录成功", response_date)

@router.get("/info")
async def get_user_info(user: User = Depends(get_current_user)):
   return success_response("获取用户信息成功", data = UserInfoResponse.model_validate(user))

# 修改用户信息：验证Token -> 更新（用户输入数据 put提交 -> 请求体参数 -> 定义Pydantic模型类） -> 响应结果
# 参数：用户输入的 + 验证Token的 + db（调用更新的方法）
@router.put("/update")
async def update_user_info(
        user_data: UserUpdateRequest,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    user = await users.update_user(db, user.username, user_data)
    return success_response(
        message="更新用户信息成功",
        data=UserInfoResponse.model_validate(user)
    )

@router.put("/password")
async def update_password(
        password_data: UserChangePasswordRequest,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    res_change_pwd = await users.change_password(
        db,
        user,
        password_data.old_password,
        password_data.new_password
    )

    if not res_change_pwd:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="修改密码失败，请检查旧密码"
        )

    return success_response(message="修改密码成功")
