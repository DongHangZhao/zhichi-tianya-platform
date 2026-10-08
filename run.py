"""
Author: your name
Date: 2026-01-10 13:01:46
LastEditTime: 2026-01-10 13:01:46
LastEditors: your name
Description: In User Settings Edit
FilePath: e:\\办公练习\\Html\\Q文件\\python_web_project\\run.py
"""
#!/usr/bin/env python
"""
Python Web项目启动脚本
用于启动Flask应用
"""

import os
import sys
from app import app

def main():
    """主函数，启动Flask应用"""
    print("正在启动Python Web项目...")
    print("应用将在 http://localhost:5000 上运行")
    print("按 Ctrl+C 停止服务\n")
    
    try:
        # 启动Flask应用
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=True
        )
    except KeyboardInterrupt:
        print("\n\n服务已停止")
        sys.exit(0)
    except Exception as e:
        print(f"启动过程中发生错误: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()