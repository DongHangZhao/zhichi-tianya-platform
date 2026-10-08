'''
Author: your name
Date: 2026-01-20 22:40:07
LastEditTime: 2026-01-20 22:40:07
LastEditors: your name
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\find_routes.py
'''
import os
import re


def find_routes():
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        # 查找所有包含post_detail的行
                        if 'post_detail' in content:
                            print(f'Found post_detail in: {filepath}')
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if 'post_detail' in line.lower():
                                    print(f'  Line {i+1}: {line.strip()}')

                        # 查找路由定义
                        if '@app.route' in content:
                            print(f'Found route in: {filepath}')
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if '@app.route' in line:
                                    # 检查下几行是否有相关的函数定义
                                    func_line = ''
                                    for j in range(i, min(i+5, len(lines))):
                                        if lines[j].strip().startswith('def '):
                                            func_line = lines[j].strip()
                                            break
                                    print(
                                        f'  Route Line {i+1}: {line.strip()} -> {func_line}')
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")


if __name__ == "__main__":
    find_routes()
