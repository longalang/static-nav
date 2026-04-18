from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Category(Base):
    """导航分类表"""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, comment="分类名称")
    sort_order = Column(Integer, default=0, comment="排序字段")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关系
    links = relationship("NavigationLink", back_populates="category", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"


class NavigationLink(Base):
    """导航链接表"""
    __tablename__ = "navigation_links"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, comment="分类ID")
    title = Column(String(100), nullable=False, comment="链接标题")
    url = Column(String(500), nullable=False, comment="链接地址")
    description = Column(String(200), nullable=True, comment="描述信息")
    sort_order = Column(Integer, default=0, comment="排序")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关系
    category = relationship("Category", back_populates="links")
    
    def __repr__(self):
        return f"<NavigationLink(id={self.id}, title='{self.title}')>"


class SearchEngine(Base):
    """搜索引擎表"""
    __tablename__ = "search_engines"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, comment="引擎名称")
    search_url = Column(String(500), nullable=False, comment="搜索URL模板")
    icon_svg = Column(Text, nullable=True, comment="SVG图标内容")
    is_active = Column(Boolean, default=True, comment="是否启用")
    is_default = Column(Boolean, default=False, comment="是否默认")
    sort_order = Column(Integer, default=0, comment="排序")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    def __repr__(self):
        return f"<SearchEngine(id={self.id}, name='{self.name}')>"


class Setting(Base):
    """系统设置表"""
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(50), unique=True, nullable=False, comment="配置键")
    value = Column(Text, nullable=True, comment="配置值")
    description = Column(String(200), nullable=True, comment="描述")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    def __repr__(self):
        return f"<Setting(key='{self.key}')>"
