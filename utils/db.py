import sqlite3
import logging
from config.config import Config

class DatabaseManager:
    """数据库管理器"""
    
    @staticmethod
    def get_db_connection():
        """获取数据库连接"""
        db_path = Config.get_db_path()
        logging.debug(f"连接数据库: {db_path}")
        
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            logging.debug("数据库连接成功")
            return conn
        except sqlite3.Error as e:
            logging.error(f"数据库连接失败: {str(e)}")
            raise
    
    @staticmethod
    def close_connection(conn):
        """关闭数据库连接"""
        if conn:
            try:
                conn.close()
                logging.debug("数据库连接已关闭")
            except sqlite3.Error as e:
                logging.error(f"关闭数据库连接失败: {str(e)}")
    
    @staticmethod
    def execute_query(query, params=(), fetchone=False, fetchall=False, return_cursor=False):
        """执行数据库查询"""
        conn = None
        try:
            conn = DatabaseManager.get_db_connection()
            cursor = conn.execute(query, params)
            
            if return_cursor:
                # 如果需要返回cursor，不提交事务，由调用方处理
                logging.debug("返回cursor")
                return cursor
            elif fetchone:
                result = cursor.fetchone()
                logging.debug(f"查询成功，获取单行结果: {result}")
            elif fetchall:
                result = cursor.fetchall()
                logging.debug(f"查询成功，获取多行结果，共{len(result)}条")
            else:
                result = None
                conn.commit()
                logging.debug("更新操作成功")
            
            return result
        except sqlite3.Error as e:
            logging.error(f"数据库操作失败: {str(e)}")
            logging.error(f"SQL查询: {query}")
            logging.error(f"参数: {params}")
            raise
        finally:
            if not return_cursor:
                DatabaseManager.close_connection(conn)
