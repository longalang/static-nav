from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.schemas import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryWithLinks
from app.crud import (
    get_categories, get_all_categories_with_links, get_category_with_links,
    create_category, update_category, delete_category
)

router = APIRouter(prefix="/categories", tags=["分类管理"])


@router.get("/", response_model=List[CategoryWithLinks])
async def list_categories(db: AsyncSession = Depends(get_db)):
    """获取所有分类及其链接（包括禁用的）"""
    categories = await get_all_categories_with_links(db, active_only=False)
    return [CategoryWithLinks.model_validate(cat) for cat in categories]


@router.get("/simple", response_model=List[CategoryResponse])
async def list_categories_simple(db: AsyncSession = Depends(get_db)):
    """获取分类列表（不含链接）"""
    categories = await get_categories(db)
    return [CategoryResponse.model_validate(cat) for cat in categories]


@router.get("/{category_id}", response_model=CategoryWithLinks)
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)):
    """获取单个分类"""
    category = await get_category_with_links(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    return category


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_new_category(category_data: CategoryCreate, db: AsyncSession = Depends(get_db)):
    """创建分类"""
    return await create_category(
        db,
        name=category_data.name,
        sort_order=category_data.sort_order,
        is_active=category_data.is_active
    )


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_existing_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新分类"""
    update_data = category_data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="没有提供更新数据")
    
    category = await update_category(db, category_id, **update_data)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    return category


@router.delete("/{category_id}")
async def delete_existing_category(category_id: int, db: AsyncSession = Depends(get_db)):
    """删除分类"""
    success = await delete_category(db, category_id)
    if not success:
        raise HTTPException(status_code=404, detail="分类不存在")
    return {"message": "删除成功"}


@router.put("/{category_id}/status/", response_model=CategoryResponse)
async def toggle_category_status(
    category_id: int,
    status_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """切换分类状态"""
    is_active = status_data.get('is_active')
    if is_active is None:
        raise HTTPException(status_code=400, detail="请提供is_active字段")
    
    from app.crud import update_category
    category = await update_category(db, category_id, is_active=is_active)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    return category
