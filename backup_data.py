#!/usr/bin/env python3
"""
数据备份脚本
用于备份所有数据，包括账户表，以便在其他机器上使用
"""

import os
import shutil
import datetime
import sqlite3

# 获取持久化目录的函数 - 统一使用项目目录下的data文件夹
def get_persist_dir():
    """获取持久化目录 - 统一使用项目目录下的data文件夹"""
    # 获取当前文件所在目录（EMS1.4/）
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 使用项目目录下的data文件夹
    persist_dir = os.path.join(current_dir, 'data')

    # 确保持久化目录存在
    os.makedirs(persist_dir, exist_ok=True)
    return persist_dir

# 数据库文件路径
DB_FILE = os.path.join(get_persist_dir(), 'device_management.db')
# 备份目录
BACKUP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'backups')

# 确保备份目录存在
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

def backup_database():
    """
    备份数据库文件
    """
    # 生成备份文件名（只包含年月日）
    timestamp = datetime.datetime.now().strftime('%Y%m%d')
    backup_file = os.path.join(BACKUP_DIR, f'databack{timestamp}.db')
    
    try:
        # 检查数据库文件是否存在
        if not os.path.exists(DB_FILE):
            print(f"错误: 数据库文件 {DB_FILE} 不存在")
            return False
        
        # 复制数据库文件到备份目录
        shutil.copy2(DB_FILE, backup_file)
        
        # 验证备份是否成功
        if os.path.exists(backup_file):
            # 检查备份文件中的表结构
            check_backup_integrity(backup_file)
            print(f"\n备份成功！")
            print(f"备份文件: {backup_file}")
            print(f"备份大小: {os.path.getsize(backup_file) / 1024:.2f} KB")
            
            # 清理旧备份（保留最近5个）
            cleanup_old_backups()
            
            return True
        else:
            print("错误: 备份文件创建失败")
            return False
            
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