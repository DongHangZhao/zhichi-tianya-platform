@echo off
REM Python Web项目部署脚本
REM 用于在Windows环境下启动Flask应用

echo 正在启动Python Web项目...
echo.

REM 切换到项目目录
cd /d "%~dp0"

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python。请确保已安装Python并添加到PATH环境变量。
    pause
    exit /b 1
)

REM 检查依赖是否已安装
pip list | findstr Flask >nul
if errorlevel 1 (
    echo 正在安装项目依赖...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo 错误: 依赖安装失败
        pause
        exit /b 1
    )
)

REM 启动Flask应用
echo.
echo 启动Python Web应用...
echo 请在浏览器中访问 http://localhost:5000
echo 按 Ctrl+C 停止服务
echo.
python app.py

pause