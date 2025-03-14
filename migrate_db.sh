#!/bin/bash

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}锦衣卫数据库迁移脚本${NC}"

# 检查Python环境
if [ ! -d "venv" ]; then
    echo -e "${RED}错误: 未找到虚拟环境${NC}"
    echo -e "请先运行 setup.sh 创建虚拟环境"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

echo -e "${BLUE}正在迁移数据库...${NC}"

# 运行数据库迁移脚本
python -m app.db.migrate

if [ $? -eq 0 ]; then
    echo -e "${GREEN}数据库迁移成功!${NC}"
else
    echo -e "${RED}数据库迁移失败!${NC}"
    exit 1
fi

echo -e "${BLUE}数据库迁移完成${NC}" 