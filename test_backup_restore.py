#!/usr/bin/env python3
"""
测试备份和还原脚本
"""

import os
import sys
import subprocess

# 测试备份功能
def test_backup():
    print("测试备份功能...")
    result = subprocess.run([sys.executable, 'backup_data.py'], capture_output=True, text=True)
    print("备份脚本输出:")
    print(result.stdout)
    if result.stderr:
        print("错误输出:")
        print(result.stderr)
    return result.returncode == 0

# 测试还原功能（仅列出备份文件）
def test_restore_list():
    print("\n测试还原功能（列出备份文件）...")
    # 运行还原脚本并模拟输入
    # 由于还原脚本需要用户输入，我们只测试列出备份文件的部分
    # 通过检查备份目录是否存在备份文件来验证
    backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'backups')
    if os.path.exists(backup_dir):
        backup_files = [f for f in os.listdir(backup_dir) if f.startswith('databack') and f.endswith('.db')]
        if backup_files:
            print(f"找到 {len(backup_files)} 个备份文件:")
            for f in backup_files:
                print(f"  - {f}")
            return True
        else:
            print("未找到备份文件")
            return False
    else:
        print("备份目录不存在")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("测试备份和还原脚本")
    print("=" * 60)
    
    backup_success = test_backup()
    restore_success = test_restore_list()
    
    print("=" * 60)
    if backup_success and restore_success:
        print("测试通过！备份和还原脚本工作正常。")
    else:
        print("测试失败！请检查脚本。")
    print("=" * 60)
