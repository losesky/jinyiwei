#!/bin/bash

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo -e "${BLUE}锦衣卫前端启动脚本${NC}"
echo -e "${BLUE}当前目录: ${SCRIPT_DIR}${NC}"

# 检查是否安装了 Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}错误: 未找到 Node.js${NC}"
    echo -e "请先安装 Node.js: https://nodejs.org/"
    exit 1
fi

# 显示 Node.js 版本
echo -e "${BLUE}Node.js 版本:${NC}"
node --version

# 检查是否安装了 npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}错误: 未找到 npm${NC}"
    echo -e "请先安装 npm"
    exit 1
fi

# 显示 npm 版本
echo -e "${BLUE}npm 版本:${NC}"
npm --version

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
    
    # 确保 @craco/craco 已正确安装
    if [ ! -d "${SCRIPT_DIR}/node_modules/@craco" ]; then
        echo -e "${YELLOW}未找到 CRACO，正在安装...${NC}"
        cd "${SCRIPT_DIR}" && npm install @craco/craco
        
        if [ $? -ne 0 ]; then
            echo -e "${RED}CRACO 安装失败${NC}"
            exit 1
        fi
        
        echo -e "${GREEN}CRACO 安装完成${NC}"
    fi
fi

# 启动开发服务器
echo -e "${BLUE}启动开发服务器...${NC}"
cd "${SCRIPT_DIR}" && npx craco start

# 捕获退出信号
trap 'echo -e "${YELLOW}正在关闭服务器...${NC}"; pkill -f "node.*craco"; echo -e "${GREEN}服务器已关闭${NC}"; exit 0' SIGINT SIGTERM

# 保持脚本运行
wait 