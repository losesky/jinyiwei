#!/bin/bash

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}锦衣卫数据库初始化脚本${NC}"

# 检查Python环境
if [ ! -d "venv" ]; then
    echo -e "${RED}错误: 未找到虚拟环境${NC}"
    echo -e "请先运行 setup.sh 创建虚拟环境"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

echo -e "${BLUE}正在初始化数据库...${NC}"

# 运行数据库初始化脚本
python -m app.db.init_db

if [ $? -eq 0 ]; then
    echo -e "${GREEN}数据库初始化成功!${NC}"
    echo -e "${YELLOW}超级管理员账号: admin${NC}"
    echo -e "${YELLOW}超级管理员密码: Admin123!${NC}"
else
    echo -e "${RED}数据库初始化失败!${NC}"
    exit 1
fi

echo -e "${BLUE}数据库初始化完成${NC}" 