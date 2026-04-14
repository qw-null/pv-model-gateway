# backend/api/auth_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional

from db.database import get_db
from db.users import User
from core.auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["认证"])


# ── Pydantic Schema ────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    password: str = Field(..., min_length=6, max_length=128)
    nickname: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str
    nickname: Optional[str]

class UserInfoResponse(BaseModel):
    id: int
    username: str
    nickname: Optional[str]
    role: str
    is_active: bool

class UpdateProfileRequest(BaseModel):
    nickname: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


# ── 登录接口 ───────────────────────────────────────────────────────────────
@router.post("/login", response_model=TokenResponse, summary="用户登录")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.username == form_data.username,
        User.is_active == True
    ).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    token = create_access_token(data={"sub": user.username})
    return TokenResponse(
        access_token=token,
        username=user.username,
        role=user.role,
        nickname=user.nickname,
    )


# ── 注册接口 ───────────────────────────────────────────────────────────────
@router.post("/register", summary="用户注册")
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")

    new_user = User(
        username=body.username,
        password=hash_password(body.password),
        nickname=body.nickname or body.username,
        role="user",
    )
    db.add(new_user)
    db.commit()
    return {"message": "注册成功"}


# ── 获取当前用户信息 ────────────────────────────────────────────────────────
@router.get("/me", response_model=UserInfoResponse, summary="获取当前用户信息")
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/profile", summary="更新昵称")
def update_profile(
    body: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_user.nickname = body.nickname
    db.commit()
    return {"message": "昵称修改成功"}


@router.put("/password", summary="修改密码")
def change_password(
    body: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(body.old_password, current_user.password):
        raise HTTPException(status_code=400, detail="原密码错误")
    current_user.password = hash_password(body.new_password)
    db.commit()
    return {"message": "密码修改成功"}
