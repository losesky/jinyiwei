#!/bin/bash

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo -e "${BLUE}锦衣卫前端简化启动脚本${NC}"
echo -e "${BLUE}当前目录: ${SCRIPT_DIR}${NC}"

# 清理可能存在的进程
echo -e "${BLUE}清理可能存在的 React 开发服务器进程...${NC}"
pkill -f "node.*react-scripts" || true
pkill -f "node.*craco" || true
echo -e "${GREEN}清理完成${NC}"

# 检查是否需要安装依赖
if [ ! -d "${SCRIPT_DIR}/node_modules" ]; then
    echo -e "${YELLOW}未找到 node_modules 目录，正在安装依赖...${NC}"
    cd "${SCRIPT_DIR}" && npm install
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}依赖安装失败${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}依赖安装完成${NC}"
else
    echo -e "${GREEN}依赖已安装${NC}"
fi

# 设置环境变量以减少内存使用
export NODE_OPTIONS="--max-old-space-size=4096"
export GENERATE_SOURCEMAP=false
export BROWSER=none
export PORT=3000

# 启动开发服务器（直接使用 react-scripts）
echo -e "${BLUE}启动开发服务器...${NC}"
cd "${SCRIPT_DIR}" && npx react-scripts start

# 捕获退出信号
trap 'echo -e "${YELLOW}正在关闭服务器...${NC}"; pkill -f "node.*react-scripts"; echo -e "${GREEN}服务器已关闭${NC}"; exit 0' SIGINT SIGTERM

# 保持脚本运行
wait 