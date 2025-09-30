
#!/usr/bin/env python3
"""
Cursor2API 本地快速启动脚本
支持多种启动模式和环境配置
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
import argparse
import socket
from typing import Optional

# ANSI 颜色代码
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_banner():
    """打印启动横幅"""
    banner = f"""
{Colors.OKCYAN}╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   {Colors.BOLD}🚀 Cursor2API - Advanced AI Models API Service{Colors.ENDC}{Colors.OKCYAN}            ║
║                                                               ║
║   Version: 3.0 | Models: 23 | Status: Production            ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝{Colors.ENDC}
    """
    print(banner)

def check_port(port: int) -> bool:
    """检查端口是否可用"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result != 0

def find_available_port(start_port: int = 8001, max_attempts: int = 10) -> Optional[int]:
    """查找可用端口"""
    for i in range(max_attempts):
        port = start_port + i
        if check_port(port):
            return port
    return None

def check_environment():
    """检查环境配置"""
    print(f"\n{Colors.OKBLUE}📋 正在检查环境配置...{Colors.ENDC}")
    
    # 检查 Python 版本
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 7:
        print(f"{Colors.OKGREEN}✅ Python 版本: {python_version.major}.{python_version.minor}.{python_version.micro}{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ Python 版本过低，需要 3.7 或以上版本{Colors.ENDC}")
        return False
    
    # 检查 .env 文件
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if not env_file.exists():
        print(f"{Colors.WARNING}⚠️  未找到 .env 文件{Colors.ENDC}")
        if env_example.exists():
            print(f"{Colors.OKBLUE}正在从 .env.example 创建 .env 文件...{Colors.ENDC}")
            try:
                # 复制 .env.example 到 .env
                import shutil
                shutil.copy(env_example, env_file)
                print(f"{Colors.OKGREEN}✅ 已创建 .env 文件，请编辑设置 API_KEY{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.FAIL}❌ 创建 .env 文件失败: {e}{Colors.ENDC}")
                return False
    else:
        print(f"{Colors.OKGREEN}✅ 找到 .env 文件{Colors.ENDC}")
    
    # 读取并检查 API_KEY
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.environ.get('API_KEY', '')
            if api_key and api_key != 'sk-default-key-please-change':
                print(f"{Colors.OKGREEN}✅ API_KEY 已配置{Colors.ENDC}")
            else:
                print(f"{Colors.WARNING}⚠️  API_KEY 未配置或使用默认值，请在 .env 文件中设置{Colors.ENDC}")
        except ImportError:
            print(f"{Colors.WARNING}⚠️  python-dotenv 未安装，将使用环境变量{Colors.ENDC}")
    
    return True

def check_dependencies():
    """检查并安装依赖"""
    print(f"\n{Colors.OKBLUE}📦 正在检查依赖...{Colors.ENDC}")
    
    requirements_file = Path('requirements.txt')
    if not requirements_file.exists():
        print(f"{Colors.FAIL}❌ 未找到 requirements.txt 文件{Colors.ENDC}")
        return False
    
    # 检查已安装的包
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'list', '--format=json'],
            capture_output=True,
            text=True,
            check=True
        )
        installed_packages = {pkg['name'].lower(): pkg['version'] 
                            for pkg in json.loads(result.stdout)}
        
        # 读取需求文件
        with open(requirements_file, 'r') as f:
            requirements = f.read().strip().split('\n')
        
        missing_packages = []
        for req in requirements:
            if req and not req.startswith('#'):
                # 解析包名（忽略版本号）
                pkg_name = req.split('>=')[0].split('==')[0].split('[')[0].strip().lower()
                if pkg_name not in installed_packages:
                    missing_packages.append(req)
        
        if missing_packages:
            print(f"{Colors.WARNING}⚠️  发现缺失的依赖包：{Colors.ENDC}")
            for pkg in missing_packages:
                print(f"    - {pkg}")
            
            response = input(f"\n{Colors.OKBLUE}是否安装缺失的依赖？(y/n): {Colors.ENDC}").strip().lower()
            if response == 'y':
                print(f"{Colors.OKBLUE}正在安装依赖...{Colors.ENDC}")
                try:
                    subprocess.run(
                        [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
                        check=True
                    )
                    print(f"{Colors.OKGREEN}✅ 依赖安装完成{Colors.ENDC}")
                except subprocess.CalledProcessError as e:
                    print(f"{Colors.FAIL}❌ 依赖安装失败: {e}{Colors.ENDC}")
                    return False
            else:
                print(f"{Colors.WARNING}⚠️  跳过依赖安装，某些功能可能无法正常工作{Colors.ENDC}")
        else:
            print(f"{Colors.OKGREEN}✅ 所有依赖已安装{Colors.ENDC}")
        
    except subprocess.CalledProcessError as e:
        print(f"{Colors.FAIL}❌ 检查依赖失败: {e}{Colors.ENDC}")
        return False
    
    return True

def start_dev_server(port: int = 8001, host: str = '127.0.0.1'):
    """启动开发服务器"""
    print(f"\n{Colors.OKBLUE}🚀 正在启动开发服务器...{Colors.ENDC}")
    
    # 检查端口是否可用
    if not check_port(port):
        print(f"{Colors.WARNING}⚠️  端口 {port} 已被占用{Colors.ENDC}")
        new_port = find_available_port(port + 1)
        if new_port:
            print(f"{Colors.OKGREEN}✅ 使用备用端口: {new_port}{Colors.ENDC}")
            port = new_port
        else:
            print(f"{Colors.FAIL}❌ 无法找到可用端口{Colors.ENDC}")
            return
    
    # 使用 Python 的 HTTP 服务器运行
    print(f"{Colors.OKGREEN}✅ 服务器启动在: http://{host}:{port}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}📝 API 端点:{Colors.ENDC}")
    print(f"    - 获取模型: GET http://{host}:{port}/v1/models")
    print(f"    - 聊天完成: POST http://{host}:{port}/v1/chat/completions")
    print(f"\n{Colors.WARNING}按 Ctrl+C 停止服务器{Colors.ENDC}\n")
    
    try:
        # 设置环境变量
        env = os.environ.copy()
        if Path('.env').exists():
            try:
                from dotenv import load_dotenv
                load_dotenv()
            except ImportError:
                pass
        
        # 启动服务器
        from api.index import handler
        from http.server import HTTPServer
        
        server = HTTPServer((host, port), handler)
        print(f"{Colors.OKGREEN}服务器正在运行...{Colors.ENDC}")
        server.serve_forever()
        
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}⚠️  服务器已停止{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}❌ 启动服务器失败: {e}{Colors.ENDC}")

def start_vercel_dev():
    """启动 Vercel 开发服务器"""
    print(f"\n{Colors.OKBLUE}🚀 正在启动 Vercel 开发服务器...{Colors.ENDC}")
    
    # 检查 vercel 是否已安装
    try:
        subprocess.run(['vercel', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"{Colors.WARNING}⚠️  Vercel CLI 未安装{Colors.ENDC}")
        print(f"{Colors.OKBLUE}请运行以下命令安装:{Colors.ENDC}")
        print(f"    npm i -g vercel")
        return
    
    print(f"{Colors.OKGREEN}✅ 正在启动 Vercel 开发环境...{Colors.ENDC}")
    print(f"{Colors.WARNING}按 Ctrl+C 停止服务器{Colors.ENDC}\n")
    
    try:
        subprocess.run(['vercel', 'dev'])
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}⚠️  服务器已停止{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}❌ 启动失败: {e}{Colors.ENDC}")

def run_tests():
    """运行测试"""
    print(f"\n{Colors.OKBLUE}🧪 正在运行测试...{Colors.ENDC}")
    
    test_files = [
        'test_all_models.py',
        'test_context_memory.py'
    ]
    
    for test_file in test_files:
        if Path(test_file).exists():
            print(f"\n{Colors.OKCYAN}运行 {test_file}...{Colors.ENDC}")
            try:
                subprocess.run([sys.executable, test_file], check=True)
                print(f"{Colors.OKGREEN}✅ {test_file} 测试通过{Colors.ENDC}")
            except subprocess.CalledProcessError:
                print(f"{Colors.FAIL}❌ {test_file} 测试失败{Colors.ENDC}")
        else:
            print(f"{Colors.WARNING}⚠️  {test_file} 不存在{Colors.ENDC}")

def main():
    """主函数"""
    parser = 
argparse.ArgumentParser(description='Cursor2API 本地启动脚本')
    parser.add_argument('mode', nargs='?', default='dev',
                       choices=['dev', 'vercel', 'test', 'install'],
                       help='启动模式: dev(本地开发), vercel(Vercel开发), test(运行测试), install(安装依赖)')
    parser.add_argument('-p', '--port', type=int, default=8001,
                       help='服务器端口 (默认: 8001)')
    parser.add_argument('-H', '--host', default='127.0.0.1',
                       help='服务器主机地址 (默认: 127.0.0.1)')
    parser.add_argument('--skip-checks', action='store_true',
                       help='跳过环境和依赖检查')
    
    args = parser.parse_args()
    
    # 打印横幅
    print_banner()
    
    # 环境和依赖检查
    if not args.skip_checks:
        if not check_environment():
            print(f"\n{Colors.FAIL}❌ 环境检查失败，请修复问题后重试{Colors.ENDC}")
            sys.exit(1)
        
        if args.mode != 'install':
            if not check_dependencies():
                print(f"\n{Colors.WARNING}⚠️  依赖检查未通过，某些功能可能无法正常工作{Colors.ENDC}")
    
    # 根据模式执行不同操作
    if args.mode == 'dev':
        start_dev_server(args.port, args.host)
    elif args.mode == 'vercel':
        start_vercel_dev()
    elif args.mode == 'test':
        run_tests()
    elif args.mode == 'install':
        print(f"\n{Colors.OKBLUE}📦 正在安装依赖...{Colors.ENDC}")
        try:
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
                check=True
            )
            print(f"{Colors.OKGREEN}✅ 依赖安装完成{Colors.ENDC}")
        except subprocess.CalledProcessError as e:
            print(f"{Colors.FAIL}❌ 依赖安装失败: {e}{Colors.ENDC}")
            sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}⚠️  程序被用户中断{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ 发生错误: {e}{Colors.ENDC}")
        sys.exit(1)