@echo off
chcp 65001 >nul
echo ========================================
echo   开发文档导航系统 - 一键启动脚本
echo ========================================
echo.

:: 检查 Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

:: 检查 Node.js
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Node.js，请先安装 Node.js 16+
    pause
    exit /b 1
)

echo [1/4] 检查后端依赖...
cd backend
if not exist "nav" (
    echo   创建虚拟环境...
    python -m venv nav
)

echo   激活虚拟环境...
call nav\Scripts\activate.bat

echo   安装/更新依赖...
pip install -r requirements.txt -q
if %errorlevel% neq 0 (
    echo [错误] 后端依赖安装失败
    pause
    exit /b 1
)
echo   ✅ 后端依赖检查完成
cd ..

echo.
echo [2/4] 检查前端依赖...
cd frontend
if not exist "node_modules" (
    echo   安装前端依赖（首次运行可能需要几分钟）...
    call npm install
    if %errorlevel% neq 0 (
        echo [错误] 前端依赖安装失败
        pause
        exit /b 1
    )
) else (
    echo   前端依赖已存在
)
echo   ✅ 前端依赖检查完成
cd ..

echo.
echo [3/4] 检查数据库...
if not exist "backend\data\nav.db" (
    echo   数据库不存在，正在初始化...
    python 数据库初始化.py
    if %errorlevel% neq 0 (
        echo [警告] 数据库初始化可能有问题，但将继续启动
    )
) else (
    echo   数据库已存在
)
echo   ✅ 数据库检查完成

echo.
echo [4/4] 启动服务...
echo.
echo ========================================
echo   后端服务: http://localhost:8000
echo   前端服务: http://localhost:5173
echo   API文档:  http://localhost:8000/docs
echo ========================================
echo.
echo 按 Ctrl+C 停止所有服务
echo.

:: 启动后端（后台运行）
start "后端服务" cmd /k "cd backend && nav\Scripts\activate.bat && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

:: 等待后端启动
timeout /t 3 /nobreak >nul

:: 启动前端
start "前端服务" cmd /k "cd frontend && npm run dev"

echo.
echo ✅ 服务启动成功！
echo.
echo 浏览器将自动打开前端页面...
timeout /t 2 /nobreak >nul
start http://localhost:5173

pause
