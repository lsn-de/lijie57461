#!/usr/bin/env python3
"""
数据备份脚本
用于备份所有数据，包括账户表，以便在其他机器上使用
"""

import os
import shutil
import datetime
import sqlite3
import sys

# 获取资源目录（打包后的资源目录）
def get_resource_dir():
    if getattr(sys, 'frozen', False):
        # 打包后的可执行文件
        return sys._MEIPASS
    else:
        # 未打包的脚本
        return os.path.dirname(os.path.abspath(__file__))

# 获取持久化目录的函数 - 统一使用项目目录下的data文件夹
def get_persist_dir():
    """获取持久化目录 - 统一使用项目目录下的data文件夹"""
    if getattr(sys, 'frozen', False):
        # 打包后的可执行文件
        executable_dir = os.path.dirname(sys.executable)
    else:
        # 未打包的脚本
        executable_dir = os.path.dirname(os.path.abspath(__file__))
    # 使用项目目录下的data文件夹
    persist_dir = os.path.join(executable_dir, 'data')

    # 确保持久化目录存在
    os.makedirs(persist_dir, exist_ok=True)
    return persist_dir

# 数据库文件路径
DB_FILE = os.path.join(get_persist_dir(), 'device_management.db')
# 备份目录 - 使用data/backups作为备份目标
BACKUP_DIR = os.path.join(get_persist_dir(), 'backups')

# 确保备份目录存在
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

# 从打包的资源中提取数据库文件（仅在打包环境下执行）
def extract_database_from_bundle():
    # 如果不是打包环境，直接返回False
    if not getattr(sys, 'frozen', False):
        return False
    
    persist_dir = get_persist_dir()
    db_path = os.path.join(persist_dir, 'device_management.db')
    init_flag_path = os.path.join(persist_dir, 'init_done.flag')
    
    # 如果数据库文件不存在，从打包的资源中提取
    if not os.path.exists(db_path) or not os.path.exists(init_flag_path):
        print("首次运行，从打包资源中提取数据库文件...")
        resource_dir = get_resource_dir()
        bundled_db_path = os.path.join(resource_dir, 'data', 'device_management.db')
        
        if os.path.exists(bundled_db_path):
            print(f"从 {bundled_db_path} 复制数据库文件到 {db_path}")
            shutil.copy2(bundled_db_path, db_path)
            print("数据库文件提取成功")
            
            # 创建标志文件
            with open(init_flag_path, 'w') as f:
                f.write('初始化完成')
            print(f"创建初始化标志文件成功: {init_flag_path}")
        else:
            print(f"警告: 打包资源中未找到数据库文件: {bundled_db_path}")
            return False
    
    return True

def check_db_access():
    """
    检查数据库文件是否可访问（未被锁定）
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.close()
        return True
    except Exception as e:
        print(f"错误: 数据库文件被锁定或无法访问 - {str(e)}")
        return False

def backup_database():
    """
    备份数据库文件
    """
    # 生成备份文件名（包含年月日时分秒）
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(BACKUP_DIR, f'databack{timestamp}.db')
    
    try:
        # 在打包环境下，确保数据库文件存在
        extract_database_from_bundle()
        
        # 检查数据库文件是否存在
        if not os.path.exists(DB_FILE):
            print(f"错误: 数据库文件 {DB_FILE} 不存在")
            return False
        
        # 检查数据库文件是否可访问（未被锁定）
        if not check_db_access():
            return False
        
        # 复制数据库文件到备份目录
        try:
            shutil.copy2(DB_FILE, backup_file)
        except Exception as e:
            print(f"错误: 复制文件失败 - {str(e)}")
            return False
        
        # 验证备份是否成功
        if not os.path.exists(backup_file):
            print("错误: 备份文件创建失败")
            return False
        
        # 验证文件大小是否一致
        try:
            source_size = os.path.getsize(DB_FILE)
            backup_size = os.path.getsize(backup_file)
            
            if source_size != backup_size:
                print(f"错误: 备份文件大小与源文件不一致（源文件: {source_size} 字节，备份文件: {backup_size} 字节）")
                return False
        except Exception as e:
            print(f"错误: 验证文件大小失败 - {str(e)}")
            return False
        
        # 检查备份文件中的表结构
        if not check_backup_integrity(backup_file):
            print("警告: 备份文件完整性检查失败")
        
        print(f"\n备份成功！")
        print(f"备份文件路径: {backup_file}")
        print(f"备份目标路径: {BACKUP_DIR}")
        print(f"源数据库文件: {DB_FILE}")
        print(f"备份大小: {backup_size / 1024:.2f} KB")
        print(f"文件大小验证: 源文件与备份文件大小一致")
        
        # 清理旧备份（保留最近5个）
        try:
            cleanup_old_backups()
        except Exception as e:
            print(f"警告: 清理旧备份失败 - {str(e)}")
        
        return True
            
    except Exception as e:
        print(f"错误: 备份失败 - {str(e)}")
        return False

def check_backup_integrity(backup_file):
    """
    检查备份文件的完整性
    """
    try:
        conn = sqlite3.connect(backup_file)
        cursor = conn.cursor()
        
        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"\n备份文件包含 {len(tables)} 个表:")
        for table in tables:
            table_name = table[0]
            # 获取表中的记录数
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"  - {table_name}: {count} 条记录")
        
        conn.close()
        
    except Exception as e:
        print(f"警告: 检查备份完整性失败 - {str(e)}")

def cleanup_old_backups():
    """
    清理旧备份，保留最近5个
    """
    try:
        # 获取所有备份文件
        backup_files = [f for f in os.listdir(BACKUP_DIR) if f.startswith('databack') and f.endswith('.db')]
        
        # 按修改时间排序（最新的在前）
        backup_files.sort(key=lambda x: os.path.getmtime(os.path.join(BACKUP_DIR, x)), reverse=True)
        
        # 保留最近5个，删除其余的
        if len(backup_files) > 5:
            for file_to_delete in backup_files[5:]:
                file_path = os.path.join(BACKUP_DIR, file_to_delete)
                os.remove(file_path)
                print(f"清理旧备份: {file_to_delete}")
                
    except Exception as e:
        print(f"警告: 清理旧备份失败 - {str(e)}")

def main():
    """
    主函数
    """
    print("=" * 60)
    print("数据备份脚本")
    print("用于备份所有数据，包括账户表")
    print("=" * 60)
    
    # 执行备份
    success = backup_database()
    
    print("=" * 60)
    if success:
        print("备份完成！")
        print("您可以将备份文件复制到其他机器上使用。")
    else:
        print("备份失败，请检查错误信息。")
    print("=" * 60)

if __name__ == "__main__":
    main()