from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.schemas import EngineCreate, EngineUpdate, EngineResponse
from app.crud import (
    get_engines, get_engine,
    create_engine, update_engine, delete_engine
)

router = APIRouter(prefix="/search-engines", tags=["搜索引擎管理"])


@router.get("/", response_model=List[EngineResponse])
async def list_engines(db: AsyncSession = Depends(get_db)):
    """获取所有启用的搜索引擎"""
    engines = await get_engines(db, active_only=True)
    return [EngineResponse.model_validate(engine) for engine in engines]


@router.get("/all", response_model=List[EngineResponse])
async def list_all_engines(db: AsyncSession = Depends(get_db)):
    """获取所有搜索引擎（包括禁用的）"""
    engines = await get_engines(db, active_only=False)
    return [EngineResponse.model_validate(engine) for engine in engines]


@router.get("/{engine_id}", response_model=EngineResponse)
async def get_search_engine(engine_id: int, db: AsyncSession = Depends(get_db)):
    """获取单个搜索引擎"""
    engine = await get_engine(db, engine_id)
    if not engine:
        raise HTTPException(status_code=404, detail="搜索引擎不存在")
    return engine


@router.post("/", response_model=EngineResponse, status_code=status.HTTP_201_CREATED)
async def create_new_engine(engine_data: EngineCreate, db: AsyncSession = Depends(get_db)):
    """创建搜索引擎"""
    return await create_engine(
        db,
        name=engine_data.name,
        search_url=engine_data.search_url,
        icon_svg=engine_data.icon_svg,
        is_active=engine_data.is_active,
        is_default=engine_data.is_default,
        sort_order=engine_data.sort_order
    )


@router.put("/{engine_id}/set-default", response_model=EngineResponse)
async def set_default_engine(
    engine_id: int,
    db: AsyncSession = Depends(get_db)
):
    """设置默认搜索引擎"""
    # 先取消所有引擎的默认状态
    from app.models import SearchEngine
    from sqlalchemy import update as sql_update
    
    await db.execute(
        sql_update(SearchEngine)
        .where(SearchEngine.is_default == True)
        .values(is_default=False)
    )
    
    # 设置当前引擎为默认
    engine = await update_engine(db, engine_id, is_default=True)
    if not engine:
        raise HTTPException(status_code=404, detail="搜索引擎不存在")
    
    await db.commit()
    return EngineResponse.model_validate(engine)


@router.put("/{engine_id}", response_model=EngineResponse)
async def update_existing_engine(
    engine_id: int,
    engine_data: EngineUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新搜索引擎"""
    update_data = engine_data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="没有提供更新数据")
    
    engine = await update_engine(db, engine_id, **update_data)
    if not engine:
        raise HTTPException(status_code=404, detail="搜索引擎不存在")
    return engine


@router.delete("/{engine_id}")
async def delete_existing_engine(engine_id: int, db: AsyncSession = Depends(get_db)):
    """删除搜索引擎"""
    success = await delete_engine(db, engine_id)
    if not success:
        raise HTTPException(status_code=404, detail="搜索引擎不存在")
    return {"message": "删除成功"}



