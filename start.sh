#!/bin/bash

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  开发文档导航系统 - 一键启动脚本${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查 Python
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
fi

if [ -z "$PYTHON_CMD" ]; then
    echo -e "${RED}[错误] 未找到 Python3，请先安装 Python 3.8+${NC}"
    exit 1
fi

# 检查 Node.js
NODE_CMD=""
if command -v node &> /dev/null; then
    NODE_CMD="node"
elif command -v nodejs &> /dev/null; then
    NODE_CMD="nodejs"
fi

if [ -z "$NODE_CMD" ]; then
    echo -e "${RED}[错误] 未找到 Node.js，请先安装 Node.js 16+${NC}"
    exit 1
fi

echo -e "${YELLOW}[1/4] 检查后端依赖...${NC}"
cd backend || exit 1

if [ ! -d "nav" ]; then
    echo -e "  ${BLUE}创建虚拟环境...${NC}"
    $PYTHON_CMD -m venv nav
fi

echo -e "  ${BLUE}激活虚拟环境...${NC}"
source nav/bin/activate

echo -e "  ${BLUE}安装/更新依赖...${NC}"
# 使用虚拟环境中的 pip，避免系统级限制
nav/bin/pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}[错误] 后端依赖安装失败${NC}"
    exit 1
fi
echo -e "  ${GREEN}✅ 后端依赖检查完成${NC}"
cd ..

echo ""
echo -e "${YELLOW}[2/4] 检查前端依赖...${NC}"
cd frontend || exit 1

if [ ! -d "node_modules" ]; then
    echo -e "  ${BLUE}安装前端依赖（首次运行可能需要几分钟）...${NC}"
    npm install
    if [ $? -ne 0 ]; then
        echo -e "${RED}[错误] 前端依赖安装失败${NC}"
        exit 1
    fi
else
    echo -e "  ${BLUE}前端依赖已存在${NC}"
fi
echo -e "  ${GREEN}✅ 前端依赖检查完成${NC}"
cd ..

echo ""
echo -e "${YELLOW}[3/4] 检查数据库...${NC}"
if [ ! -f "backend/data/nav.db" ]; then
    echo -e "  ${BLUE}数据库不存在，正在初始化...${NC}"
    $PYTHON_CMD 数据库初始化.py
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}[警告] 数据库初始化可能有问题，但将继续启动${NC}"
    fi
else
    echo -e "  ${BLUE}数据库已存在${NC}"
fi
echo -e "  ${GREEN}✅ 数据库检查完成${NC}"

echo ""
echo -e "${YELLOW}[4/4] 启动服务...${NC}"
echo ""
echo -e "${YELLOW}按 Ctrl+C 停止所有服务${NC}"
echo ""

# 清理函数
cleanup() {
    echo ""
    echo -e "${YELLOW}正在停止服务...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    wait $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}✅ 服务已停止${NC}"
    exit 0
}

# 注册清理函数
trap cleanup INT TERM
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  后端服务: http://localhost:8000${NC}"
echo -e "${BLUE}  前端服务: http://localhost:5173${NC}"
echo -e "${BLUE}  API文档:  http://localhost:8000/docs${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 启动后端
cd backend
# 使用虚拟环境中的 Python 直接运行，避免 source 命令兼容性问题
source nav/bin/activate
nav/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# 等待后端启动
sleep 3

# 等待进程
wait $BACKEND_PID $FRONTEND_PID
