#!/usr/bin/env python3
"""
数据恢复脚本
用于从备份文件恢复数据到新机器
"""

import os
import shutil
import sqlite3
import sys
import datetime

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

def list_backups():
    """
    列出所有可用的备份文件
    """
    try:
        # 确保备份目录存在
        if not os.path.exists(BACKUP_DIR):
            print(f"错误: 备份目录 {BACKUP_DIR} 不存在")
            return []
        
        # 获取所有备份文件
        backup_files = [f for f in os.listdir(BACKUP_DIR) if f.startswith('databack') and f.endswith('.db')]
        
        # 按修改时间排序（最新的在前）
        backup_files.sort(key=lambda x: os.path.getmtime(os.path.join(BACKUP_DIR, x)), reverse=True)
        
        if backup_files:
            print("可用的备份文件:")
            print("-" * 60)
            for i, backup_file in enumerate(backup_files, 1):
                file_path = os.path.join(BACKUP_DIR, backup_file)
                file_size = os.path.getsize(file_path) / 1024
                mod_time = os.path.getmtime(file_path)
                mod_time_str = datetime.datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
                print(f"{i}. {backup_file}")
                print(f"   大小: {file_size:.2f} KB")
                print(f"   修改时间: {mod_time_str}")
                print("-" * 60)
        else:
            print("没有找到备份文件")
        
        return backup_files
        
    except Exception as e:
        print(f"错误: 列出备份文件失败 - {str(e)}")
        return []

def restore_from_backup(backup_file):
    """
    从指定的备份文件恢复数据
    """
    backup_path = os.path.join(BACKUP_DIR, backup_file)
    
    try:
        # 检查备份文件是否存在
        if not os.path.exists(backup_path):
            print(f"错误: 备份文件 {backup_file} 不存在")
            return False
        
        # 检查备份文件的完整性
        if not check_backup_integrity(backup_path):
            print("错误: 备份文件损坏")
            return False
        
        # 确保数据目录存在
        os.makedirs('data', exist_ok=True)
        
        # 备份当前数据库（如果存在）
        if os.path.exists(DB_FILE):
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            current_backup = os.path.join(BACKUP_DIR, f'current_{timestamp}.db')
            shutil.copy2(DB_FILE, current_backup)
            print(f"已备份当前数据库到: {current_backup}")
        
        # 恢复备份
        shutil.copy2(backup_path, DB_FILE)
        
        # 验证恢复是否成功
        if os.path.exists(DB_FILE):
            print("\n恢复成功！")
            print(f"从备份文件: {backup_file}")
            print(f"恢复到: {DB_FILE}")
            
            # 检查恢复后的数据
            check_backup_integrity(DB_FILE)
            
            return True
        else:
            print("错误: 恢复失败")
            return False
            
    except Exception as e:
        print(f"错误: 恢复失败 - {str(e)}")
        return False

def check_backup_integrity(db_file):
    """
    检查备份文件的完整性
    """
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"\n数据库包含 {len(tables)} 个表:")
        for table in tables:
            table_name = table[0]
            # 获取表中的记录数
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"  - {table_name}: {count} 条记录")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"警告: 检查数据库完整性失败 - {str(e)}")
        return False

def main():
    """
    主函数
    """
    import datetime
    
    print("=" * 60)
    print("数据恢复脚本")
    print("用于从备份文件恢复数据")
    print("=" * 60)
    
    # 列出可用的备份文件
    backup_files = list_backups()
    
    if not backup_files:
        print("没有可用的备份文件，无法恢复数据。")
        return
    
    # 选择备份文件
    while True:
        try:
            choice = input("请输入要恢复的备份文件编号 (1-{}): ".format(len(backup_files)))
            choice = int(choice)
            if 1 <= choice <= len(backup_files):
                selected_backup = backup_files[choice - 1]
                break
            else:
                print("输入无效，请输入有效的编号。")
        except ValueError:
            print("输入无效，请输入数字。")
    
    # 确认恢复操作
    print(f"\n您选择恢复: {selected_backup}")
    confirm = input("确认要恢复吗？这将覆盖当前数据库 (y/n): ")
    
    if confirm.lower() == 'y':
        # 执行恢复
        success = restore_from_backup(selected_backup)
        
        print("=" * 60)
        if success:
            print("恢复完成！")
            print("您可以重启应用程序以使用恢复的数据。")
        else:
            print("恢复失败，请检查错误信息。")
        print("=" * 60)
    else:
        print("恢复操作已取消。")

if __name__ == "__main__":
    main()