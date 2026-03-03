import os
import sys

class Config:
    """应用配置类"""
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    JSON_AS_ASCII = False
    
    @staticmethod
    def get_persist_dir():
        """获取持久化目录 - 统一使用项目目录下的data文件夹"""
        # 获取当前文件所在目录（config/）
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 向上一级到EMS1.4目录，然后使用data文件夹
        persist_dir = os.path.join(os.path.dirname(current_dir), 'data')

        # 确保持久化目录存在
        os.makedirs(persist_dir, exist_ok=True)
        return persist_dir
    
    @staticmethod
    def get_resource_dir():
        """获取资源目录（打包后的资源目录）"""
        if getattr(sys, 'frozen', False):
            # 打包后的可执行文件
            return sys._MEIPASS
        else:
            # 未打包的脚本
            current_dir = os.path.dirname(os.path.abspath(__file__))
            return os.path.dirname(os.path.dirname(current_dir))
    
    @staticmethod
    def get_db_path():
        """获取数据库文件路径"""
        persist_dir = Config.get_persist_dir()
        return os.path.join(persist_dir, 'device_management.db')
    
    @staticmethod
    def get_log_file():
        """获取日志文件路径"""
        # 确定日志文件路径
        if getattr(sys, 'frozen', False):
            # 打包后的可执行文件
            executable_dir = os.path.dirname(sys.executable)
        else:
            # 未打包的脚本
            current_dir = os.path.dirname(os.path.abspath(__file__))
            executable_dir = os.path.dirname(os.path.dirname(current_dir))
        
        # 日志文件路径 - 直接放在可执行文件旁边
        return os.path.join(executable_dir, 'ems.log')
