from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
from app.core.database import get_db
from app.schemas import CategoryWithLinks, EngineResponse
from app.crud import get_all_categories_with_links, get_engines, get_settings

router = APIRouter(tags=["首页数据"])


@router.get("/home/data")
async def get_home_data(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """获取首页所需的全部数据"""
    # 获取所有启用的分类及链接
    categories = await get_all_categories_with_links(db, active_only=True)
    
    # 转换为Pydantic模型
    categories_data = [CategoryWithLinks.model_validate(cat) for cat in categories]
    
    # 获取所有启用的搜索引擎
    engines = await get_engines(db, active_only=True)
    
    # 转换为Pydantic模型
    engines_data = [EngineResponse.model_validate(engine) for engine in engines]
    
    # 获取系统设置
    settings_list = await get_settings(db)
    settings_dict = {s.key: s.value for s in settings_list}
    
    return {
        "categories": categories_data,
        "engines": engines_data,
        "settings": settings_dict
    }
