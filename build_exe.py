#!/usr/bin/env python3
"""
EMS1.4 打包脚本
用于将Flask应用打包成可执行文件
支持Windows和Linux平台
"""

import PyInstaller.__main__
import os
import platform
import sys
import shutil

def build_exe():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 检测当前平台
        current_platform = platform.system()
        print(f"当前平台: {current_platform}")
        
        # 版本号
        version = "1.4.0"
        
        # 清理旧的构建目录
        build_dir = os.path.join(current_dir, 'build')
        dist_dir = os.path.join(current_dir, 'dist')
        
        if os.path.exists(build_dir):
            print(f"清理旧的构建目录: {build_dir}")
            shutil.rmtree(build_dir)
        
        if os.path.exists(dist_dir):
            print(f"清理旧的输出目录: {dist_dir}")
            shutil.rmtree(dist_dir)
        
        # 根据平台设置不同的参数
        if current_platform == 'Linux':
            pyinstaller_args = [
                'app.py',
                f'--name=ems-{version}',
                '--onefile',
                '--add-data=templates:templates',  # Linux使用冒号分隔
                '--add-data=static:static',
                '--add-data=data:data',
                '--add-data=init_db.py:.',
                '--add-data=backup_data.py:.',
                '--add-data=restore_data.py:.',
                '--add-data=物理机模板.xlsx:.',
                '--add-data=虚拟机模板.xlsx:.',
                '--add-data=部门模板.xlsx:.',
                # 显式包含所有必要的依赖
                '--hidden-import=flask',
                '--hidden-import=flask.cli',
                '--hidden-import=flask.templating',
                '--hidden-import=flask.wrappers',
                '--hidden-import=flask.globals',
                '--hidden-import=flask.signals',
                '--hidden-import=jinja2',
                '--hidden-import=jinja2.ext',
                '--hidden-import=werkzeug',
                '--hidden-import=werkzeug.urls',
                '--hidden-import=werkzeug.routing',
                '--hidden-import=werkzeug.exceptions',
                '--hidden-import=itsdangerous',
                '--hidden-import=markupsafe',
                '--hidden-import=sqlite3',
                '--hidden-import=openpyxl',
                '--hidden-import=openpyxl.cell',
                '--hidden-import=openpyxl.workbook',
                '--hidden-import=openpyxl.worksheet',
                '--hidden-import=paramiko',
                '--hidden-import=paramiko.ssh_exception',
                '--hidden-import=paramiko.util',
                '--hidden-import=paramiko.transport',
                '--hidden-import=paramiko.client',
                '--hidden-import=paramiko.auth_handler',
                '--hidden-import=paramiko.channel',
                '--hidden-import=pandas',
                '--hidden-import=pandas.core',
                '--hidden-import=plotly',
                '--hidden-import=plotly.graph_objects',
                '--hidden-import=dash',
                '--hidden-import=dash_html_components',
                '--hidden-import=dash_core_components',
                '--clean',
                '--noconfirm',
                '--log-level=INFO',
            ]
        else:
            # Windows平台参数
            pyinstaller_args = [
                'app.py',
                f'--name=EMS-{version}',
                '--onefile',
                '--windowed',
                '--add-data=templates;templates',  # Windows使用分号分隔
                '--add-data=static;static',
                '--add-data=data;data',
                '--add-data=init_db.py;.',
                '--add-data=backup_data.py;.',
                '--add-data=restore_data.py;.',
                '--add-data=物理机模板.xlsx;.',
                '--add-data=虚拟机模板.xlsx;.',
                '--add-data=部门模板.xlsx;.',
                # 显式包含所有必要的依赖
                '--hidden-import=flask',
                '--hidden-import=flask.cli',
                '--hidden-import=flask.templating',
                '--hidden-import=flask.wrappers',
                '--hidden-import=flask.globals',
                '--hidden-import=flask.signals',
                '--hidden-import=jinja2',
                '--hidden-import=jinja2.ext',
                '--hidden-import=werkzeug',
                '--hidden-import=werkzeug.urls',
                '--hidden-import=werkzeug.routing',
                '--hidden-import=werkzeug.exceptions',
                '--hidden-import=itsdangerous',
                '--hidden-import=markupsafe',
                '--hidden-import=sqlite3',
                '--hidden-import=openpyxl',
                '--hidden-import=openpyxl.cell',
                '--hidden-import=openpyxl.workbook',
                '--hidden-import=openpyxl.worksheet',
                '--hidden-import=paramiko',
                '--hidden-import=paramiko.ssh_exception',
                '--hidden-import=paramiko.util',
                '--hidden-import=paramiko.transport',
                '--hidden-import=paramiko.client',
                '--hidden-import=paramiko.auth_handler',
                '--hidden-import=paramiko.channel',
                '--hidden-import=pandas',
                '--hidden-import=pandas.core',
                '--hidden-import=plotly',
                '--hidden-import=plotly.graph_objects',
                '--hidden-import=dash',
                '--hidden-import=dash_html_components',
                '--hidden-import=dash_core_components',
                '--clean',
                '--noconfirm',
                '--log-level=INFO',
            ]
        
        print(f"开始打包Flask应用 v{version}...")
        print(f"使用参数: {pyinstaller_args}")
        
        # 执行打包
        PyInstaller.__main__.run(pyinstaller_args)
        
        # 打包完成后的处理
        if current_platform == 'Linux':
            output_file = os.path.join(current_dir, 'dist', f'ems-{version}')
            if os.path.exists(output_file):
                print(f"打包成功！可执行文件路径: {output_file}")
                print("\n使用方法:")
                print(f"1. 给可执行文件添加执行权限: chmod +x ems-{version}")
                print(f"2. 运行应用: ./ems-{version}")
                print("3. 访问地址: http://localhost:5000")
                print("\n数据备份和恢复:")
                print("1. 备份数据: python backup_data.py")
                print("2. 恢复数据: python restore_data.py")
            else:
                print("警告: 未找到打包后的可执行文件")
        else:
            output_file = os.path.join(current_dir, 'dist', f'EMS-{version}.exe')
            if os.path.exists(output_file):
                print(f"打包成功！可执行文件路径: {output_file}")
                print("\n使用方法:")
                print(f"1. 运行应用: {output_file}")
                print("2. 访问地址: http://localhost:5000")
                print("\n数据备份和恢复:")
                print("1. 备份数据: python backup_data.py")
                print("2. 恢复数据: python restore_data.py")
            else:
                print("警告: 未找到打包后的可执行文件")
                
        print("\n打包完成！")
        
    except Exception as e:
        print(f"打包过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    build_exe()