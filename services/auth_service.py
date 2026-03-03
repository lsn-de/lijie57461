from utils.db import DatabaseManager


class AuthService:
    """认证服务"""
    
    @staticmethod
    def authenticate(username, password):
        """验证用户身份"""
        user = DatabaseManager.execute_query(
            'SELECT users.*, roles.name as role_name FROM users JOIN roles ON users.role_id = roles.id WHERE users.username = ?',
            (username,),
            fetchone=True
        )
        
        if user and user['password'] == password:
            return {
                'id': user['id'],
                'username': user['username'],
                'role': user['role_name'],
                'department': user.get('department')
            }
        return None
    
    @staticmethod
    def get_user_by_id(user_id):
        """根据用户ID获取用户信息"""
        user = DatabaseManager.execute_query(
            'SELECT users.*, roles.name as role_name FROM users JOIN roles ON users.role_id = roles.id WHERE users.id = ?',
            (user_id,),
            fetchone=True
        )
        
        if user:
            return {
                'id': user['id'],
                'username': user['username'],
                'role': user['role_name'],
                'department': user.get('department')
            }
        return None
