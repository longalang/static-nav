from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.database import get_db
from app.schemas import LinkCreate, LinkUpdate, LinkResponse
from app.crud import (
    get_links, get_link, create_link, update_link, delete_link
)

router = APIRouter(prefix="/links", tags=["链接管理"])


@router.get("/", response_model=List[LinkResponse])
async def list_links(
    category_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """获取链接列表"""
    links = await get_links(db, category_id=category_id, is_active=is_active, skip=skip, limit=limit)
    return [LinkResponse.model_validate(link) for link in links]


@router.post("/", response_model=LinkResponse, status_code=status.HTTP_201_CREATED)
async def create_new_link(link_data: LinkCreate, db: AsyncSession = Depends(get_db)):
    """创建链接"""
    return await create_link(
        db,
        category_id=link_data.category_id,
        title=link_data.title,
        url=link_data.url,
        description=link_data.description,
        sort_order=link_data.sort_order,
        is_active=link_data.is_active
    )


@router.put("/{link_id}/status/", response_model=LinkResponse)
async def toggle_link_status(
    link_id: int,
    status_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """切换链接状态"""
    is_active = status_data.get('is_active')
    if is_active is None:
        raise HTTPException(status_code=400, detail="请提供is_active字段")
    
    link = await update_link(db, link_id, is_active=is_active)
    if not link:
        raise HTTPException(status_code=404, detail="链接不存在")
    return link


@router.get("/{link_id}", response_model=LinkResponse)
async def get_navigation_link(link_id: int, db: AsyncSession = Depends(get_db)):
    """获取单个链接"""
    link = await get_link(db, link_id)
    if not link:
        raise HTTPException(status_code=404, detail="链接不存在")
    return link


@router.put("/{link_id}", response_model=LinkResponse)
async def update_existing_link(
    link_id: int,
    link_data: LinkUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新链接"""
    update_data = link_data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="没有提供更新数据")
    
    link = await update_link(db, link_id, **update_data)
    if not link:
        raise HTTPException(status_code=404, detail="链接不存在")
    return link


@router.delete("/{link_id}")
async def delete_existing_link(link_id: int, db: AsyncSession = Depends(get_db)):
    """删除链接"""
    success = await delete_link(db, link_id)
    if not success:
        raise HTTPException(status_code=404, detail="链接不存在")
    return {"message": "删除成功"}
