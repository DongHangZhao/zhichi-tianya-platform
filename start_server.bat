@echo off
chcp 65001 >nul
echo.
echo ================================
echo    咫尺天涯社交平台启动器
echo ================================
echo.

REM 检查Python是否已安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请确保Python已安装并添加到PATH环境变量中。
    pause
    exit /b 1
)

echo 正在启动咫尺天涯社交平台...
echo.

REM 设置环境变量
set FLASK_APP=app.py
set FLASK_ENV=development

REM 启动Flask应用
python run.py

echo.
echo 应用已关闭。
pause