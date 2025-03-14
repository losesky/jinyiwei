#!/bin/bash

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}锦衣卫外键更新脚本${NC}"

# 检查Python环境
if [ ! -d "venv" ]; then
    echo -e "${RED}错误: 未找到虚拟环境${NC}"
    echo -e "请先运行 setup.sh 创建虚拟环境"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

echo -e "${BLUE}正在更新外键...${NC}"

# 运行外键更新脚本
python -m app.db.update_foreign_keys

if [ $? -eq 0 ]; then
    echo -e "${GREEN}外键更新成功!${NC}"
else
    echo -e "${RED}外键更新失败!${NC}"
    exit 1
fi

echo -e "${BLUE}外键更新完成${NC}" 