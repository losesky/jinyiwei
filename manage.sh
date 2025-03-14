#!/bin/bash

# 锦衣卫项目管理脚本
# 用于简化常见操作如启动应用、运行迁移等

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 检查是否以root用户运行
check_root() {
    if [ "$(id -u)" -eq 0 ]; then
        echo -e "${YELLOW}警告: 当前以root用户运行脚本${NC}"
        echo -e "${YELLOW}这可能会导致权限问题，建议使用普通用户运行${NC}"
        echo -e "${YELLOW}继续执行...${NC}"
        
        # 检查是否有SUDO_USER环境变量（通过sudo运行）
        if [ -n "$SUDO_USER" ]; then
            echo -e "${BLUE}检测到通过sudo运行，原始用户: $SUDO_USER${NC}"
        fi
    fi
}

# 检查虚拟环境
check_venv() {
    if [ -z "$VIRTUAL_ENV" ]; then
        echo -e "${YELLOW}警告: 未检测到虚拟环境，尝试激活...${NC}"
        if [ -d "$SCRIPT_DIR/venv" ]; then
            # 保存当前PATH以便恢复
            OLD_PATH="$PATH"
            
            # 直接设置Python路径，避免依赖source激活
            export VIRTUAL_ENV="$SCRIPT_DIR/venv"
            export PATH="$VIRTUAL_ENV/bin:$PATH"
            
            echo -e "${GREEN}已设置虚拟环境路径${NC}"
            
            # 验证Python路径
            PYTHON_PATH=$(command -v python 2>/dev/null)
            if [ -z "$PYTHON_PATH" ]; then
                echo -e "${RED}错误: 虚拟环境路径已设置，但找不到Python命令${NC}"
                echo -e "${YELLOW}尝试直接使用绝对路径...${NC}"
                
                # 尝试直接使用绝对路径
                if [ -f "$VIRTUAL_ENV/bin/python" ]; then
                    PYTHON_PATH="$VIRTUAL_ENV/bin/python"
                    echo -e "${GREEN}找到Python: $PYTHON_PATH${NC}"
                    # 导出PYTHON变量供后续使用
                    export PYTHON="$PYTHON_PATH"
                else
                    echo -e "${RED}错误: 无法找到Python可执行文件${NC}"
                    # 恢复原始PATH
                    export PATH="$OLD_PATH"
                    unset VIRTUAL_ENV
                    exit 1
                fi
            else
                echo -e "${GREEN}使用Python: $PYTHON_PATH${NC}"
                # 导出PYTHON变量供后续使用
                export PYTHON="$PYTHON_PATH"
            fi
        else
            echo -e "${RED}错误: 未找到虚拟环境目录 'venv'${NC}"
            echo -e "请先创建并激活虚拟环境:"
            echo -e "python -m venv venv"
            echo -e "source venv/bin/activate"
            exit 1
        fi
    else
        # 验证Python路径
        PYTHON_PATH=$(command -v python 2>/dev/null)
        if [ -z "$PYTHON_PATH" ]; then
            echo -e "${YELLOW}警告: 虚拟环境已激活，但找不到Python命令，尝试直接使用绝对路径...${NC}"
            
            # 尝试直接使用绝对路径
            if [ -f "$VIRTUAL_ENV/bin/python" ]; then
                PYTHON_PATH="$VIRTUAL_ENV/bin/python"
                echo -e "${GREEN}找到Python: $PYTHON_PATH${NC}"
                # 导出PYTHON变量供后续使用
                export PYTHON="$PYTHON_PATH"
            else
                echo -e "${RED}错误: 无法找到Python可执行文件${NC}"
                exit 1
            fi
        else
            echo -e "${GREEN}使用Python: $PYTHON_PATH${NC}"
            # 导出PYTHON变量供后续使用
            export PYTHON="$PYTHON_PATH"
        fi
    fi
    
    # 显示Python版本
    echo -e "${BLUE}Python版本:${NC}"
    $PYTHON --version
}

# 检查环境变量文件
check_env() {
    if [ ! -f "$SCRIPT_DIR/.env" ]; then
        echo -e "${YELLOW}警告: 未找到.env文件${NC}"
        if [ -f "$SCRIPT_DIR/.env.example" ]; then
            echo -e "是否从.env.example创建.env文件? [y/N]"
            read -r response
            if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
                cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
                echo -e "${GREEN}已创建.env文件，请编辑配置信息${NC}"
            else
                echo -e "${RED}请手动创建.env文件${NC}"
                exit 1
            fi
        else
            echo -e "${RED}错误: 未找到.env.example文件${NC}"
            exit 1
        fi
    fi
}

# 显示帮助信息
show_help() {
    echo -e "${BLUE}锦衣卫项目管理脚本${NC}"
    echo -e "用法: ./manage.sh [命令] [选项]"
    echo -e ""
    echo -e "可用命令:"
    echo -e "  ${GREEN}run${NC}             启动API服务"
    echo -e "  ${GREEN}run-celery${NC}      启动API服务和Celery Worker"
    echo -e "  ${GREEN}run-all${NC}         启动API服务、Celery Worker和Beat"
    echo -e "  ${GREEN}celery-only${NC}     仅启动Celery Worker和Beat"
    echo -e "  ${GREEN}migrate${NC}         运行数据库迁移"
    echo -e "  ${GREEN}makemigrations${NC}  创建新的迁移文件"
    echo -e "  ${GREEN}test${NC}            运行测试"
    echo -e "  ${GREEN}lint${NC}            运行代码检查"
    echo -e "  ${GREEN}clean${NC}           清理临时文件和缓存"
    echo -e "  ${GREEN}install${NC}         安装依赖"
    echo -e "  ${GREEN}update${NC}          更新依赖"
    echo -e "  ${GREEN}help${NC}            显示此帮助信息"
    echo -e ""
    echo -e "常用选项:"
    echo -e "  ${GREEN}--celery-uid${NC} USERNAME  指定运行Celery的用户名或用户ID"
    echo -e "  ${GREEN}--port${NC} PORT            指定端口号"
    echo -e "  ${GREEN}--reload${NC}               启用热重载"
    echo -e ""
    echo -e "示例:"
    echo -e "  ./manage.sh run"
    echo -e "  ./manage.sh run-all --celery-uid username"
    echo -e "  ./manage.sh run --port 8080 --reload"
}

# 清理Celery进程
clean_celery() {
    echo -e "${BLUE}清理Celery进程...${NC}"
    pkill -f "celery -A app.workers.celery_app" || true
    echo -e "${GREEN}已清理Celery进程${NC}"
    
    # 删除可能损坏的调度文件
    if [ -f "$SCRIPT_DIR/data/celerybeat-schedule" ]; then
        rm -f "$SCRIPT_DIR/data/celerybeat-schedule"
        echo -e "${GREEN}已删除调度文件${NC}"
    fi
}

# 运行API服务
run_api() {
    echo -e "${BLUE}启动API服务...${NC}"
    cd "$SCRIPT_DIR" && $PYTHON run.py --auto-port "$@"
}

# 运行API服务和Celery Worker
run_celery() {
    echo -e "${BLUE}启动API服务和Celery Worker...${NC}"
    cd "$SCRIPT_DIR" && $PYTHON run.py --with-celery --auto-port "$@"
}

# 运行API服务、Celery Worker和Beat
run_all() {
    echo -e "${BLUE}启动API服务、Celery Worker和Beat...${NC}"
    
    # 清理已有的Celery进程
    clean_celery
    
    # 检查是否已经指定了--celery-uid参数
    if ! echo "$*" | grep -q -- "--celery-uid"; then
        # 如果是root用户，尝试使用当前登录用户运行Celery
        if [ "$(id -u)" -eq 0 ] && [ -n "$SUDO_USER" ]; then
            echo -e "${YELLOW}检测到root用户，将使用$SUDO_USER用户运行Celery${NC}"
            
            # 确保数据目录存在并设置正确的权限
            mkdir -p "$SCRIPT_DIR/data/nltk_data" "$SCRIPT_DIR/logs"
            chown -R "$SUDO_USER":"$SUDO_USER" "$SCRIPT_DIR/data" "$SCRIPT_DIR/logs"
            chmod -R 755 "$SCRIPT_DIR/data" "$SCRIPT_DIR/logs"
            
            # 确保NLTK数据目录对所有用户可写
            if [ -d "$SCRIPT_DIR/data/nltk_data" ]; then
                chmod -R 777 "$SCRIPT_DIR/data/nltk_data"
                echo -e "${GREEN}已设置NLTK数据目录权限${NC}"
            fi
            
            cd "$SCRIPT_DIR" && $PYTHON run.py --with-celery --with-beat --auto-port --celery-uid "$SUDO_USER" "$@"
        else
            # 确保数据目录存在
            mkdir -p "$SCRIPT_DIR/data/nltk_data" "$SCRIPT_DIR/logs"
            chmod -R 755 "$SCRIPT_DIR/data" "$SCRIPT_DIR/logs"
            
            # 确保NLTK数据目录对所有用户可写
            if [ -d "$SCRIPT_DIR/data/nltk_data" ]; then
                chmod -R 777 "$SCRIPT_DIR/data/nltk_data"
                echo -e "${GREEN}已设置NLTK数据目录权限${NC}"
            fi
            
            cd "$SCRIPT_DIR" && $PYTHON run.py --with-celery --with-beat --auto-port "$@"
        fi
    else
        # 确保数据目录存在
        mkdir -p "$SCRIPT_DIR/data/nltk_data" "$SCRIPT_DIR/logs"
        chmod -R 755 "$SCRIPT_DIR/data" "$SCRIPT_DIR/logs"
        
        # 确保NLTK数据目录对所有用户可写
        if [ -d "$SCRIPT_DIR/data/nltk_data" ]; then
            chmod -R 777 "$SCRIPT_DIR/data/nltk_data"
            echo -e "${GREEN}已设置NLTK数据目录权限${NC}"
        fi
        
        cd "$SCRIPT_DIR" && $PYTHON run.py --with-celery --with-beat --auto-port "$@"
    fi
}

# 仅运行Celery Worker和Beat
celery_only() {
    echo -e "${BLUE}仅启动Celery Worker和Beat...${NC}"
    
    # 清理已有的Celery进程
    clean_celery
    
    # 检查是否已经指定了--celery-uid参数
    if ! echo "$*" | grep -q -- "--celery-uid"; then
        # 如果是root用户，尝试使用当前登录用户运行Celery
        if [ "$(id -u)" -eq 0 ] && [ -n "$SUDO_USER" ]; then
            echo -e "${YELLOW}检测到root用户，将使用$SUDO_USER用户运行Celery${NC}"
            
            # 确保数据目录存在并设置正确的权限
            mkdir -p "$SCRIPT_DIR/data/nltk_data" "$SCRIPT_DIR/logs"
            chown -R "$SUDO_USER":"$SUDO_USER" "$SCRIPT_DIR/data" "$SCRIPT_DIR/logs"
            chmod -R 755 "$SCRIPT_DIR/data" "$SCRIPT_DIR/logs"
            
            # 确保NLTK数据目录对所有用户可写
            if [ -d "$SCRIPT_DIR/data/nltk_data" ]; then
                chmod -R 777 "$SCRIPT_DIR/data/nltk_data"
                echo -e "${GREEN}已设置NLTK数据目录权限${NC}"
            fi
            
            cd "$SCRIPT_DIR" && $PYTHON run.py --celery-only --celery-uid "$SUDO_USER" "$@"
        else
            # 确保数据目录存在
            mkdir -p "$SCRIPT_DIR/data/nltk_data" "$SCRIPT_DIR/logs"
            chmod -R 755 "$SCRIPT_DIR/data" "$SCRIPT_DIR/logs"
            
            # 确保NLTK数据目录对所有用户可写
            if [ -d "$SCRIPT_DIR/data/nltk_data" ]; then
                chmod -R 777 "$SCRIPT_DIR/data/nltk_data"
                echo -e "${GREEN}已设置NLTK数据目录权限${NC}"
            fi
            
            cd "$SCRIPT_DIR" && $PYTHON run.py --celery-only "$@"
        fi
    else
        # 确保数据目录存在
        mkdir -p "$SCRIPT_DIR/data/nltk_data" "$SCRIPT_DIR/logs"
        chmod -R 755 "$SCRIPT_DIR/data" "$SCRIPT_DIR/logs"
        
        # 确保NLTK数据目录对所有用户可写
        if [ -d "$SCRIPT_DIR/data/nltk_data" ]; then
            chmod -R 777 "$SCRIPT_DIR/data/nltk_data"
            echo -e "${GREEN}已设置NLTK数据目录权限${NC}"
        fi
        
        cd "$SCRIPT_DIR" && $PYTHON run.py --celery-only "$@"
    fi
}

# 运行数据库迁移
run_migrate() {
    echo -e "${BLUE}运行数据库迁移...${NC}"
    cd "$SCRIPT_DIR" && $PYTHON -m alembic upgrade head
}

# 创建新的迁移文件
make_migrations() {
    echo -e "${BLUE}创建新的迁移文件...${NC}"
    if [ -z "$1" ]; then
        echo -e "${YELLOW}请提供迁移消息${NC}"
        echo -e "示例: ./manage.sh makemigrations '添加用户表'"
        exit 1
    fi
    cd "$SCRIPT_DIR" && $PYTHON -m alembic revision --autogenerate -m "$1"
}

# 运行测试
run_tests() {
    echo -e "${BLUE}运行测试...${NC}"
    cd "$SCRIPT_DIR" && $PYTHON -m pytest "$@"
}

# 运行代码检查
run_lint() {
    echo -e "${BLUE}运行代码检查...${NC}"
    cd "$SCRIPT_DIR" && $PYTHON -m flake8 app tests
    cd "$SCRIPT_DIR" && $PYTHON -m mypy app
}

# 清理临时文件和缓存
clean() {
    echo -e "${BLUE}清理临时文件和缓存...${NC}"
    cd "$SCRIPT_DIR" && find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    cd "$SCRIPT_DIR" && find . -type f -name "*.pyc" -delete 2>/dev/null || true
    cd "$SCRIPT_DIR" && find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    cd "$SCRIPT_DIR" && find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
    echo -e "${GREEN}清理完成${NC}"
}

# 安装依赖
install_deps() {
    echo -e "${BLUE}安装依赖...${NC}"
    cd "$SCRIPT_DIR" && $PYTHON -m pip install -r requirements.txt
}

# 更新依赖
update_deps() {
    echo -e "${BLUE}更新依赖...${NC}"
    cd "$SCRIPT_DIR" && $PYTHON -m pip install --upgrade -r requirements.txt
}

# 主函数
main() {
    # 如果没有参数，显示帮助信息
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi

    # 检查是否以root用户运行
    check_root
    
    # 解析命令
    cmd="$1"
    shift
    
    # 显示当前用户和环境信息
    echo -e "${BLUE}当前用户: $(whoami)${NC}"
    echo -e "${BLUE}当前目录: $(pwd)${NC}"
    
    case "$cmd" in
        run)
            check_venv
            check_env
            run_api "$@"
            ;;
        run-celery)
            check_venv
            check_env
            run_celery "$@"
            ;;
        run-all)
            check_venv
            check_env
            run_all "$@"
            ;;
        celery-only)
            check_venv
            check_env
            celery_only "$@"
            ;;
        migrate)
            check_venv
            check_env
            run_migrate
            ;;
        makemigrations)
            check_venv
            check_env
            make_migrations "$1"
            ;;
        test)
            check_venv
            run_tests "$@"
            ;;
        lint)
            check_venv
            run_lint
            ;;
        clean)
            clean
            ;;
        install)
            check_venv
            install_deps
            ;;
        update)
            check_venv
            update_deps
            ;;
        help)
            show_help
            ;;
        *)
            echo -e "${RED}未知命令: $cmd${NC}"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@" 