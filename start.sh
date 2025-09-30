#!/bin/bash

# Cursor2API 快速启动脚本 (Bash 版本)
# 使用方法: ./start.sh [dev|vercel|test|install]

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# 打印横幅
print_banner() {
    echo -e "${CYAN}"
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║                                                               ║"
    echo "║   ${BOLD}🚀 Cursor2API - Advanced AI Models API Service${NC}${CYAN}            ║"
    echo "║                                                               ║"
    echo "║   Version: 3.0 | Models: 23 | Status: Production            ║"
    echo "║                                                               ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# 检查 Python
check_python() {
    if command -v python3 &> /dev/null; then
        echo -e "${GREEN}✅ Python3 已安装${NC}"
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        echo -e "${GREEN}✅ Python 已安装${NC}"
        PYTHON_CMD="python"
    else
        echo -e "${RED}❌ Python 未安装，请先安装 Python 3.7+${NC}"
        exit 1
    fi
}

# 检查并创建 .env 文件
check_env() {
    if [ ! -f .env ]; then
        echo -e "${YELLOW}⚠️  未找到 .env 文件${NC}"
        if [ -f .env.example ]; then
            echo -e "${BLUE}正在从 .env.example 创建 .env 文件...${NC}"
            cp .env.example .env
            echo -e "${GREEN}✅ 已创建 .env 文件，请编辑设置 API_KEY${NC}"
        fi
    else
        echo -e "${GREEN}✅ 找到 .env 文件${NC}"
    fi
}

# 安装依赖
install_deps() {
    echo -e "${BLUE}📦 正在安装依赖...${NC}"
    $PYTHON_CMD -m pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ 依赖安装完成${NC}"
    else
        echo -e "${RED}❌ 依赖安装失败${NC}"
        exit 1
    fi
}

# 启动开发服务器
start_dev() {
    echo -e "${BLUE}🚀 正在启动开发服务器...${NC}"
    echo -e "${GREEN}✅ 服务器将启动在: http://127.0.0.1:8001${NC}"
    echo -e "${CYAN}📝 API 端点:${NC}"
    echo "    - 获取模型: GET http://127.0.0.1:8001/v1/models"
    echo "    - 聊天完成: POST http://127.0.0.1:8001/v1/chat/completions"
    echo -e "\n${YELLOW}按 Ctrl+C 停止服务器${NC}\n"
    
    # 加载环境变量并启动服务器
    if [ -f .env ]; then
        export $(cat .env | grep -v '^#' | xargs)
    fi
    
    # 使用 Python 启动
    $PYTHON_CMD -c "
from api.index import handler
from http.server import HTTPServer
import os

port = int(os.environ.get('PORT', 8001))
host = '127.0.0.1'

server = HTTPServer((host, port), handler)
print(f'服务器正在 http://{host}:{port} 运行...')
server.serve_forever()
"
}

# 启动 Vercel 开发服务器
start_vercel() {
    echo -e "${BLUE}🚀 正在启动 Vercel 开发服务器...${NC}"
    
    # 检查 vercel 是否已安装
    if ! command -v vercel &> /dev/null; then
        echo -e "${YELLOW}⚠️  Vercel CLI 未安装${NC}"
        echo -e "${BLUE}请运行以下命令安装:${NC}"
        echo "    npm i -g vercel"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 正在启动 Vercel 开发环境...${NC}"
    echo -e "${YELLOW}按 Ctrl+C 停止服务器${NC}\n"
    vercel dev
}

# 运行测试
run_tests() {
    echo -e "${BLUE}🧪 正在运行测试...${NC}"
    
    if [ -f test_all_models.py ]; then
        echo -e "${CYAN}运行 test_all_models.py...${NC}"
        $PYTHON_CMD test_all_models.py
    fi
    
    if [ -f test_context_memory.py ]; then
        echo -e "${CYAN}运行 test_context_memory.py...${NC}"
        $PYTHON_CMD test_context_memory.py
    fi
}

# 主函数
main() {
    print_banner
    
    # 检查 Python
    check_python
    
    # 检查环境
    check_env
    
    # 获取命令参数
    MODE=${1:-dev}
    
    case $MODE in
        dev)
            start_dev
            ;;
        vercel)
            start_vercel
            ;;
        test)
            run_tests
            ;;
        install)
            install_deps
            ;;
        *)
            echo -e "${RED}无效的模式: $MODE${NC}"
            echo "使用方法: ./start.sh [dev|vercel|test|install]"
            echo "  dev     - 启动本地开发服务器 (默认)"
            echo "  vercel  - 启动 Vercel 开发环境"
            echo "  test    - 运行测试"
            echo "  install - 安装依赖"
            exit 1
            ;;
    esac
}

# 捕获 Ctrl+C
trap 'echo -e "\n${YELLOW}⚠️  服务器已停止${NC}"; exit 0' INT

# 运行主函数
main "$@"