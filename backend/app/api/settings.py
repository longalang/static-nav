from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.schemas import SettingCreate, SettingUpdate, SettingResponse
from app.crud import (
    get_settings, get_setting, get_setting_value,
    create_or_update_setting
)

router = APIRouter(prefix="/settings", tags=["系统设置"])


@router.get("/", response_model=dict)
async def list_settings(db: AsyncSession = Depends(get_db)):
    """获取所有系统设置（字典格式）"""
    settings_list = await get_settings(db)
    # 转换为字典格式
    settings_dict = {s.key: s.value for s in settings_list}
    return settings_dict


@router.get("/{key}", response_model=SettingResponse)
async def get_system_setting(key: str, db: AsyncSession = Depends(get_db)):
    """获取单个系统设置"""
    setting = await get_setting(db, key)
    if not setting:
        raise HTTPException(status_code=404, detail="设置不存在")
    return setting


@router.put("/{key}", response_model=SettingResponse)
async def update_system_setting(
    key: str,
    setting_data: SettingUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新系统设置"""
    update_data = setting_data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="没有提供更新数据")
    
    # 获取现有设置的description
    existing = await get_setting(db, key)
    description = existing.description if existing else ""
    
    return await create_or_update_setting(
        db,
        key=key,
        value=update_data.get('value', ''),
        description=update_data.get('description', description)
    )


@router.post("/", response_model=SettingResponse)
async def create_or_update_setting_endpoint(
    setting_data: SettingCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建或更新系统设置"""
    return await create_or_update_setting(
        db,
        key=setting_data.key,
        value=setting_data.value or "",
        description=setting_data.description or ""
    )


@router.put("/", response_model=dict)
async def update_all_settings(
    settings_data: dict = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """批量更新所有系统设置"""
    from app.models import Setting
    from sqlalchemy import select
    from app.core.security import get_password_hash
    
    print(f"📝 收到批量设置更新请求: {list(settings_data.keys())}")
    
    # 检查是否需要更新管理员密码
    admin_password = settings_data.get('admin_password')
    if admin_password and admin_password.strip():
        # 如果提供了新密码，进行哈希加密
        settings_data['admin_password'] = get_password_hash(admin_password.strip())
        print(f"   🔐 管理员密码已加密")
    else:
        # 如果密码为空或空白，删除该字段，不更新密码
        settings_data.pop('admin_password', None)
    
    # 更新或创建设置项
    for key, value in settings_data.items():
        # 检查设置是否已存在
        result = await db.execute(
            select(Setting).where(Setting.key == key)
        )
        existing_setting = result.scalar_one_or_none()
        
        if existing_setting:
            # 更新现有设置
            existing_setting.value = str(value) if value is not None else ""
            print(f"   ✅ 更新: {key}")
        else:
            # 创建新设置
            new_setting = Setting(
                key=key,
                value=str(value) if value is not None else "",
                description=""
            )
            db.add(new_setting)
            print(f"   ✅ 创建: {key}")
    
    await db.commit()
    print("✅ 所有设置保存成功")
    
    return {"message": "设置保存成功"}
