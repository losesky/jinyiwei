#!/bin/bash

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo -e "${BLUE}锦衣卫前端环境设置脚本${NC}"
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

# 全局安装 CRACO
echo -e "${BLUE}全局安装 CRACO...${NC}"
npm install -g @craco/craco

if [ $? -ne 0 ]; then
    echo -e "${RED}CRACO 全局安装失败${NC}"
    echo -e "${YELLOW}尝试使用 sudo 安装...${NC}"
    sudo npm install -g @craco/craco
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}CRACO 全局安装失败${NC}"
        echo -e "${YELLOW}将使用 npx 运行 CRACO${NC}"
    else
        echo -e "${GREEN}CRACO 全局安装成功${NC}"
    fi
else
    echo -e "${GREEN}CRACO 全局安装成功${NC}"
fi

# 安装项目依赖
echo -e "${BLUE}安装项目依赖...${NC}"
cd "${SCRIPT_DIR}" && npm install

if [ $? -ne 0 ]; then
    echo -e "${RED}依赖安装失败${NC}"
    exit 1
fi

echo -e "${GREEN}依赖安装完成${NC}"

# 创建 .env.development.local 文件
echo -e "${BLUE}创建 .env.development.local 文件...${NC}"
cat > "${SCRIPT_DIR}/.env.development.local" << EOL
# 增加 Node.js 内存限制
NODE_OPTIONS=--max-old-space-size=4096

# 禁用源映射以减少内存使用
GENERATE_SOURCEMAP=false

# 减少 TypeScript 检查的并行度
TSC_COMPILE_ON_ERROR=true
FORK_TS_CHECKER_WEBPACK_PLUGIN_MEMORY_LIMIT=4096

# 禁用浏览器自动打开
BROWSER=none

# 设置开发服务器端口
PORT=3000
EOL

echo -e "${GREEN}环境设置完成${NC}"
echo -e "${BLUE}现在您可以运行以下命令启动前端:${NC}"
echo -e "${GREEN}./start.sh${NC} - 使用 CRACO 启动"
echo -e "${GREEN}./start-simple.sh${NC} - 使用原生 React Scripts 启动"
echo -e "${GREEN}npm run start${NC} - 使用 CRACO 启动"
echo -e "${GREEN}npm run start:simple${NC} - 使用原生 React Scripts 启动" 