@echo off
REM Cursor2API 快速启动脚本 (Windows 批处理版本)
REM 使用方法: start.bat [dev|vercel|test|install]

setlocal EnableDelayedExpansion

REM 打印横幅
echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║                                                               ║
echo ║   🚀 Cursor2API - Advanced AI Models API Service            ║
echo ║                                                               ║
echo ║   Version: 3.0 ^| Models: 23 ^| Status: Production            ║
echo ║                                                               ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

REM 检查 Python
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Python 已安装
    set PYTHON_CMD=python
) else (
    where python3 >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo ✅ Python3 已安装
        set PYTHON_CMD=python3
    ) else (
        echo ❌ Python 未安装，请先安装 Python 3.7+
        pause
        exit /b 1
    )
)

REM 检查并创建 .env 文件
if not exist .env (
    echo ⚠️  未找到 .env 文件
    if exist .env.example (
        echo 正在从 .env.example 创建 .env 文件...
        copy .env.example .env >nul
        echo ✅ 已创建 .env 文件，请编辑设置 API_KEY
    )
) else (
    echo ✅ 找到 .env 文件
)

REM 获取命令参数
set MODE=%1
if "%MODE%"=="" set MODE=dev

REM 根据模式执行操作
if "%MODE%"=="dev" goto :start_dev
if "%MODE%"=="vercel" goto :start_vercel
if "%MODE%"=="test" goto :run_tests
if "%MODE%"=="install" goto :install_deps
goto :invalid_mode

:start_dev
echo.
echo 🚀 正在启动开发服务器...
echo ✅ 服务器将启动在: http://127.0.0.1:8001
echo 📝 API 端点:
echo     - 获取模型: GET http://127.0.0.1:8001/v1/models
echo     - 聊天完成: POST http://127.0.0.1:8001/v1/chat/completions
echo.
echo 按 Ctrl+C 停止服务器
echo.

REM 加载环境变量
if exist .env (
    for /f "tokens=*" %%a in (.env) do (
        set %%a
    )
)

REM 启动 Python 服务器
%PYTHON_CMD% quick_start.py
goto :end

:start_vercel
echo.
echo 🚀 正在启动 Vercel 开发服务器...

REM 检查 vercel 是否已安装
where vercel >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Vercel CLI 未安装
    echo 请运行以下命令安装:
    echo     npm i -g vercel
    pause
    exit /b 1
)

echo ✅ 正在启动 Vercel 开发环境...
echo 按 Ctrl+C 停止服务器
echo.
vercel dev
goto :end

:run_tests
echo.
echo 🧪 正在运行测试...
echo.

if exist test_all_models.py (
    echo 运行 test_all_models.py...
    %PYTHON_CMD% test_all_models.py
    echo.
)

if exist test_context_memory.py (
    echo 运行 test_context_memory.py...
    %PYTHON_CMD% test_context_memory.py
)
goto :end

:install_deps
echo.
echo 📦 正在安装依赖...
%PYTHON_CMD% -m pip install -r requirements.txt
if %ERRORLEVEL% EQU 0 (
    echo ✅ 依赖安装完成
) else (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)
goto :end

:invalid_mode
echo.
echo ❌ 无效的模式: %MODE%
echo.
echo 使用方法: start.bat [dev^|vercel^|test^|install]
echo   dev     - 启动本地开发服务器 (默认)
echo   vercel  - 启动 Vercel 开发环境
echo   test    - 运行测试
echo   install - 安装依赖
echo.
pause
exit /b 1

:end
echo.
echo 👋 程序已结束
pause