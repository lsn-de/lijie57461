import logging
import os
from config.config import Config

# 配置日志
def setup_logging():
    """设置日志配置"""
    log_file = Config.get_log_file()
    
    # 配置日志，同时输出到文件和终端
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    print(f"日志文件位置: {log_file}")

def extract_database_from_bundle():
    """从打包的资源中提取数据库文件（仅在打包环境下执行）"""
    # 如果不是打包环境，直接返回False
    if not getattr(__import__('sys'), 'frozen', False):
        return False
    
    persist_dir = Config.get_persist_dir()
    db_path = Config.get_db_path()
    init_flag_path = os.path.join(persist_dir, 'init_done.flag')
    
    # 如果数据库文件不存在，从打包的资源中提取
    if not os.path.exists(db_path) or not os.path.exists(init_flag_path):
        print("首次运行，从打包资源中提取数据库文件...")
        resource_dir = Config.get_resource_dir()
        bundled_db_path = os.path.join(resource_dir, 'data', 'device_management.db')
        
        if os.path.exists(bundled_db_path):
            print(f"从 {bundled_db_path} 复制数据库文件到 {db_path}")
            import shutil
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
