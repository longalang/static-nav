from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List, Optional
from app.models import Category, NavigationLink, SearchEngine, Setting


# ============ 分类 CRUD ============
async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Category]:
    """获取所有分类"""
    result = await db.execute(
        select(Category).order_by(Category.sort_order).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def get_category_with_links(db: AsyncSession, category_id: int) -> Optional[Category]:
    """获取分类及其链接"""
    result = await db.execute(
        select(Category).where(Category.id == category_id)
    )
    return result.scalar_one_or_none()


async def get_all_categories_with_links(db: AsyncSession, active_only: bool = True) -> List[Category]:
    """获取所有分类及其链接"""
    query = select(Category).order_by(Category.sort_order)
    
    # 如果只需要启用的分类
    if active_only:
        query = query.where(Category.is_active == True)
    
    result = await db.execute(query)
    categories = result.scalars().all()
    
    # 加载每个分类的链接
    for category in categories:
        await db.refresh(category, ['links'])
        
        # 如果只需要启用的链接，过滤掉禁用的
        if active_only:
            category.links = [link for link in category.links if link.is_active]
    
    return categories


async def create_category(db: AsyncSession, name: str, sort_order: int = 0, is_active: bool = True) -> Category:
    """创建分类"""
    db_category = Category(name=name, sort_order=sort_order, is_active=is_active)
    db.add(db_category)
    await db.flush()
    await db.refresh(db_category)
    return db_category


async def update_category(db: AsyncSession, category_id: int, **kwargs) -> Optional[Category]:
    """更新分类"""
    stmt = update(Category).where(Category.id == category_id).values(**kwargs)
    await db.execute(stmt)
    await db.commit()
    return await get_category_with_links(db, category_id)


async def delete_category(db: AsyncSession, category_id: int) -> bool:
    """删除分类"""
    stmt = delete(Category).where(Category.id == category_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


# ============ 链接 CRUD ============
async def get_links(db: AsyncSession, category_id: Optional[int] = None, is_active: Optional[bool] = None, skip: int = 0, limit: int = 100) -> List[NavigationLink]:
    """获取链接列表"""
    query = select(NavigationLink).order_by(NavigationLink.sort_order).offset(skip).limit(limit)
    if category_id:
        query = query.where(NavigationLink.category_id == category_id)
    if is_active is not None:
        query = query.where(NavigationLink.is_active == is_active)
    
    result = await db.execute(query)
    return result.scalars().all()


async def get_link(db: AsyncSession, link_id: int) -> Optional[NavigationLink]:
    """获取单个链接"""
    result = await db.execute(
        select(NavigationLink).where(NavigationLink.id == link_id)
    )
    return result.scalar_one_or_none()


async def create_link(db: AsyncSession, **kwargs) -> NavigationLink:
    """创建链接"""
    db_link = NavigationLink(**kwargs)
    db.add(db_link)
    await db.flush()
    await db.refresh(db_link)
    return db_link


async def update_link(db: AsyncSession, link_id: int, **kwargs) -> Optional[NavigationLink]:
    """更新链接"""
    stmt = update(NavigationLink).where(NavigationLink.id == link_id).values(**kwargs)
    await db.execute(stmt)
    await db.commit()
    return await get_link(db, link_id)


async def delete_link(db: AsyncSession, link_id: int) -> bool:
    """删除链接"""
    stmt = delete(NavigationLink).where(NavigationLink.id == link_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


# ============ 搜索引擎 CRUD ============
async def get_engines(db: AsyncSession, active_only: bool = True) -> List[SearchEngine]:
    """获取搜索引擎列表"""
    query = select(SearchEngine).order_by(SearchEngine.sort_order)
    if active_only:
        query = query.where(SearchEngine.is_active == True)
    
    result = await db.execute(query)
    return result.scalars().all()


async def get_engine(db: AsyncSession, engine_id: int) -> Optional[SearchEngine]:
    """获取单个搜索引擎"""
    result = await db.execute(
        select(SearchEngine).where(SearchEngine.id == engine_id)
    )
    return result.scalar_one_or_none()


async def create_engine(db: AsyncSession, **kwargs) -> SearchEngine:
    """创建搜索引擎"""
    db_engine = SearchEngine(**kwargs)
    db.add(db_engine)
    await db.flush()
    await db.refresh(db_engine)
    return db_engine


async def update_engine(db: AsyncSession, engine_id: int, **kwargs) -> Optional[SearchEngine]:
    """更新搜索引擎"""
    stmt = update(SearchEngine).where(SearchEngine.id == engine_id).values(**kwargs)
    await db.execute(stmt)
    await db.commit()
    return await get_engine(db, engine_id)


async def delete_engine(db: AsyncSession, engine_id: int) -> bool:
    """删除搜索引擎"""
    stmt = delete(SearchEngine).where(SearchEngine.id == engine_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


# ============ 系统设置 CRUD ============
async def get_settings(db: AsyncSession) -> List[Setting]:
    """获取所有设置"""
    result = await db.execute(select(Setting))
    return result.scalars().all()


async def get_setting(db: AsyncSession, key: str) -> Optional[Setting]:
    """获取单个设置"""
    result = await db.execute(
        select(Setting).where(Setting.key == key)
    )
    return result.scalar_one_or_none()


async def get_setting_value(db: AsyncSession, key: str) -> Optional[str]:
    """获取设置值"""
    setting = await get_setting(db, key)
    return setting.value if setting else None


async def create_or_update_setting(db: AsyncSession, key: str, value: str, description: str = "") -> Setting:
    """创建或更新设置"""
    existing = await get_setting(db, key)
    if existing:
        stmt = update(Setting).where(Setting.key == key).values(value=value, description=description)
        await db.execute(stmt)
    else:
        existing = Setting(key=key, value=value, description=description)
        db.add(existing)
    
    await db.commit()
    await db.refresh(existing)
    return existing


# ============ 用户认证 CRUD ============
async def get_admin_username(db: AsyncSession) -> Optional[str]:
    """获取管理员用户名"""
    result = await db.execute(
        select(Setting).where(Setting.key == 'admin_username')
    )
    setting = result.scalar_one_or_none()
    return setting.value if setting else None


async def get_admin_password_hash(db: AsyncSession) -> Optional[str]:
    """获取管理员密码哈希"""
    result = await db.execute(
        select(Setting).where(Setting.key == 'admin_password')
    )
    setting = result.scalar_one_or_none()
    return setting.value if setting else None


async def set_admin_credentials(db: AsyncSession, username: str, password_hash: str) -> None:
    """设置管理员凭据"""
    # 更新或创建用户名
    await create_or_update_setting(db, 'admin_username', username, '管理员用户名')
    # 更新或创建密码
    await create_or_update_setting(db, 'admin_password', password_hash, '管理员密码哈希')


async def verify_admin_credentials(db: AsyncSession, username: str, password: str) -> bool:
    """验证管理员凭据"""
    from app.core.security import verify_password
    
    stored_username = await get_admin_username(db)
    stored_password_hash = await get_admin_password_hash(db)
    
    if not stored_username or not stored_password_hash:
        return False
    
    # 验证用户名和密码
    return username == stored_username and verify_password(password, stored_password_hash)
