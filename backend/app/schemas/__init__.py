from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ============ 分类相关 ============
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="分类名称")
    sort_order: int = Field(default=0, description="排序字段")
    is_active: bool = Field(default=True, description="是否启用")


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CategoryWithLinks(CategoryResponse):
    links: List['LinkResponse'] = []


# ============ 链接相关 ============
class LinkBase(BaseModel):
    category_id: int = Field(..., description="分类ID")
    title: str = Field(..., min_length=1, max_length=100, description="链接标题")
    url: str = Field(..., min_length=1, max_length=500, description="链接地址")
    description: Optional[str] = Field(None, max_length=200, description="描述信息")
    sort_order: int = Field(default=0, description="排序")
    is_active: bool = Field(default=True, description="是否启用")


class LinkCreate(LinkBase):
    pass


class LinkUpdate(BaseModel):
    category_id: Optional[int] = None
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    url: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=200)
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class LinkResponse(LinkBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============ 搜索引擎相关 ============
class EngineBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="引擎名称")
    search_url: str = Field(..., min_length=1, max_length=500, description="搜索URL模板")
    icon_svg: Optional[str] = Field(None, description="SVG图标内容")
    is_active: bool = Field(default=True, description="是否启用")
    is_default: bool = Field(default=False, description="是否默认")
    sort_order: int = Field(default=0, description="排序")


class EngineCreate(EngineBase):
    pass


class EngineUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    search_url: Optional[str] = Field(None, min_length=1, max_length=500)
    icon_svg: Optional[str] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    sort_order: Optional[int] = None


class EngineResponse(EngineBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============ 系统设置相关 ============
class SettingBase(BaseModel):
    key: str = Field(..., min_length=1, max_length=50, description="配置键")
    value: Optional[str] = Field(None, description="配置值")
    description: Optional[str] = Field(None, max_length=200, description="描述")


class SettingCreate(SettingBase):
    pass


class SettingUpdate(BaseModel):
    value: Optional[str] = None
    description: Optional[str] = Field(None, max_length=200)


class SettingResponse(SettingBase):
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============ 认证相关 ============
class LoginRequest(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AdminInfo(BaseModel):
    id: int
    username: str
    
    class Config:
        from_attributes = True


# 解决循环引用
CategoryWithLinks.model_rebuild()
