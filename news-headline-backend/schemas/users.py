# ============================================================
# 用户相关 Schema（请求体 & 响应体）
# ============================================================
# 思路：用 Pydantic 模型定义每个接口"请求长什么样"和"响应长什么样"。
#
# 三类模型分工：
#   - 请求模型：前端发过来的数据（UsersRequest）
#   - 基础模型：可复用的字段集合（UserInfoBase）
#   - 响应模型：最终返回给前端的 data 结构（UserInfoResponse / UserAuthResponse）
#
# model_config 说明：
#   from_attributes=True  → 让 model_validate(orm对象) 能从 ORM 属性中取值
#   populate_by_name=True → 同时支持字段名和 alias 别名赋值
# ============================================================

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


# ==================== 请求模型 ====================

class UsersRequest(BaseModel):
    """注册/登录时前端传过来的数据"""
    username: str
    password: str


# ==================== 基础模型（可复用字段） ====================

class UserInfoBase(BaseModel):
    """
    用户信息中可选的公共字段。
    多个响应模型如果都要用到 nickname/avatar/gender/bio，
    可以继承这个类，避免重复定义。
    """
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")


# ==================== 响应模型 ====================

class UserInfoResponse(UserInfoBase):
    """
    返回给前端的用户基本信息。
    继承 UserInfoBase → 自动拥有 nickname/avatar/gender/bio。
    额外加了 id 和 username（必返回字段）。
    """
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)
    #                        ^^^^^^^^^^^^^^^^^^^^^^
    #                        关键配置：让 model_validate(user_orm对象) 能工作


class UserAuthResponse(BaseModel):
    """
    认证成功后返回的 data 结构。
    外壳是 success_response → data 就是这个模型。

    最终 JSON 形态：
    {
        "code": 200,
        "message": "用户注册成功",
        "data": {
            "token": "xxx-xxx-xxx",
            "userInfo": {
                "id": 1,
                "username": "test",
                ...
            }
        }
    }
    """
    token: str
    user_info: UserInfoResponse = Field(..., alias="userInfo")
    #                                ^^^           ^^^^^^^^^^
    #                              必填字段      前端用的驼峰命名

    model_config = ConfigDict(
        populate_by_name=True,   # 允许用 "user_info" 或 "userInfo" 赋值
        from_attributes=True     # 允许从 ORM 对象取值
    )

# 更新用户信息的模型类
class UserUpdateRequest(BaseModel):
    nickname: str = None
    avatar: str = None
    gender: str = None
    bio: str = None
    phone: str = None

class UserChangePasswordRequest(BaseModel):
    old_password: str = Field(..., alias="oldPassword", description="旧密码")
    new_password: str = Field(..., min_length=6 ,alias="newPassword", description="新密码")
