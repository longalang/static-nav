from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
import shutil
import os
from datetime import datetime
from pathlib import Path

router = APIRouter(prefix="/upload", tags=["文件上传"])

# 前端public目录路径（相对于项目根目录）
FRONTEND_PUBLIC_DIR = Path(__file__).parent.parent.parent.parent / "frontend" / "public"


def backup_file(file_path: Path) -> bool:
    """
    备份文件，在文件名后添加_bak_yyyy-MM-dd后缀
    :param file_path: 原文件路径
    :return: 是否备份成功
    """
    if not file_path.exists():
        return False
    
    # 生成备份文件名
    date_str = datetime.now().strftime("%Y-%m-%d")
    stem = file_path.stem
    suffix = file_path.suffix
    backup_name = f"{stem}_bak_{date_str}{suffix}"
    backup_path = file_path.parent / backup_name
    
    # 如果今天的备份已存在，添加时间戳避免覆盖
    if backup_path.exists():
        time_str = datetime.now().strftime("%H%M%S")
        backup_name = f"{stem}_bak_{date_str}_{time_str}{suffix}"
        backup_path = file_path.parent / backup_name
    
    try:
        shutil.copy2(file_path, backup_path)
        print(f"✅ 文件备份成功: {backup_path.name}")
        return True
    except Exception as e:
        print(f"❌ 文件备份失败: {str(e)}")
        return False


@router.post("/favicon")
async def upload_favicon(file: UploadFile = File(...)):
    """上传favicon.ico文件"""
    try:
        # 验证文件类型
        if not file.filename.lower().endswith('.ico'):
            raise HTTPException(status_code=400, detail="只支持.ico格式的favicon文件")
        
        # 确保目录存在
        FRONTEND_PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
        
        favicon_path = FRONTEND_PUBLIC_DIR / "favicon.ico"
        
        # 备份原文件
        if favicon_path.exists():
            backup_file(favicon_path)
        
        # 保存新文件
        with open(favicon_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return JSONResponse(
            content={
                "message": "favicon上传成功",
                "filename": "favicon.ico",
                "path": "/favicon.ico"
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.post("/logo")
async def upload_logo(file: UploadFile = File(...)):
    """上传logo文件（支持png、jpg、jpeg、gif、svg）"""
    try:
        # 验证文件类型
        allowed_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.svg']
        if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
            raise HTTPException(
                status_code=400, 
                detail=f"只支持以下格式: {', '.join(allowed_extensions)}"
            )
        
        # 确保目录存在
        FRONTEND_PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
        
        # 获取文件扩展名
        file_ext = Path(file.filename).suffix.lower()
        logo_path = FRONTEND_PUBLIC_DIR / f"logo{file_ext}"
        
        # 备份原文件（查找所有logo.*文件）
        for existing_logo in FRONTEND_PUBLIC_DIR.glob("logo.*"):
            if existing_logo.is_file():
                backup_file(existing_logo)
        
        # 保存新文件
        with open(logo_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return JSONResponse(
            content={
                "message": "logo上传成功",
                "filename": logo_path.name,
                "path": f"/{logo_path.name}"
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.get("/files")
async def list_uploaded_files():
    """列出已上传的文件"""
    try:
        files = []
        if FRONTEND_PUBLIC_DIR.exists():
            for file_path in FRONTEND_PUBLIC_DIR.iterdir():
                if file_path.is_file() and file_path.name.startswith(('favicon', 'logo')):
                    stat = file_path.stat()
                    files.append({
                        "name": file_path.name,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                        "is_backup": "_bak_" in file_path.name
                    })
        
        # 按名称排序，主文件在前，备份文件在后
        files.sort(key=lambda x: (x["is_backup"], x["name"]))
        
        return {"files": files}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文件列表失败: {str(e)}")


@router.delete("/backup/{filename}")
async def delete_backup(filename: str):
    """删除备份文件（只能删除包含_bak_的文件）"""
    try:
        # 安全检查：只能删除备份文件
        if "_bak_" not in filename:
            raise HTTPException(status_code=400, detail="只能删除备份文件")
        
        file_path = FRONTEND_PUBLIC_DIR / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="文件不存在")
        
        # 删除文件
        file_path.unlink()
        
        return {"message": f"备份文件 {filename} 已删除"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
