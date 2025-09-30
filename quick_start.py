#!/usr/bin/env python3
"""
Cursor2API 超简单快速启动脚本
一键启动，无需配置
"""

import os
import sys
from pathlib import Path

def quick_start():
    """快速启动服务器"""
    print("\n🚀 Cursor2API 快速启动中...\n")
    
    # 自动创建 .env 文件（如果不存在）
    env_file = Path('.env')
    if not env_file.exists() and Path('.env.example').exists():
        import shutil
        shutil.copy('.env.example', env_file)
        print("✅ 已自动创建 .env 配置文件")
    
    # 加载环境变量
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
    
    # 快速启动服务器
    try:
        from api.index import handler
        from http.server import HTTPServer
        
        port = 8001
        host = '127.0.0.1'
        
        print(f"✅ 服务器已启动: http://{host}:{port}")
        print(f"📝 API 文档页面: http://{host}:{port}")
        print(f"🔑 API密钥配置: 请编辑 .env 文件设置 API_KEY")
        print(f"\n💡 快速测试:")
        print(f"   curl http://{host}:{port}/v1/models -H 'Authorization: Bearer YOUR_API_KEY'")
        print(f"\n⚠️  按 Ctrl+C 停止服务器\n")
        
        server = HTTPServer((host, port), handler)
        server.serve_forever()
        
    except KeyboardInterrupt:
        print("\n\n👋 服务器已停止")
    except ImportError as e:
        print(f"❌ 错误：{e}")
        print("请确保在项目根目录运行此脚本")
    except Exception as e:
        print(f"❌ 启动失败：{e}")

if __name__ == '__main__':
    quick_start()