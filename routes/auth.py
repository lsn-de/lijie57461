from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from utils.db import DatabaseManager
import logging

# 创建认证蓝图
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 从数据库获取用户信息
        user = DatabaseManager.execute_query(
            'SELECT users.*, roles.name as role_name FROM users JOIN roles ON users.role_id = roles.id WHERE users.username = ?',
            (username,),
            fetchone=True
        )
        
        # 验证用户名和密码
        if user and user['password'] == password:
            # 登录成功，设置会话
            session['logged_in'] = True
            session['username'] = username
            session['role'] = user['role_name']
            session['user_id'] = user['id']
            session['department'] = user['department']
            
            # 调试日志
            logging.debug(f"用户 {username} 登录，部门: {user['department']}")
            logging.debug(f"session['department']: {session['department']}")
            
            return redirect(url_for('index'))
        else:
            # 登录失败，重定向到登录页面
            return render_template('login.html', error='账号或密码错误')
    
    # GET请求，显示登录页面
    return render_template('login.html')


@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    """API登录端点（返回JSON格式）"""
    username = request.form.get('username')
    password = request.form.get('password')
    
    # 从数据库获取用户信息
    user = DatabaseManager.execute_query(
        'SELECT users.*, roles.name as role_name FROM users JOIN roles ON users.role_id = roles.id WHERE users.username = ?',
        (username,),
        fetchone=True
    )
    
    # 验证用户名和密码
    if user and user['password'] == password:
        # 登录成功，设置会话
        session['logged_in'] = True
        session['username'] = username
        session['role'] = user['role_name']
        session['user_id'] = user['id']
        session['department'] = user['department']
        
        # 调试日志
        logging.debug(f"API用户 {username} 登录，部门: {user['department']}")
        logging.debug(f"API session['department']: {session['department']}")

        # 返回JSON格式的成功信息
        return jsonify({
            'success': True,
            'message': '登录成功',
            'user': {
                'username': user['username'],
                'role': user['role_name']
            }
        })
    else:
        # 返回JSON格式的错误信息
        return jsonify({
            'success': False,
            'message': '账号或密码错误'
        }), 401


@auth_bp.route('/logout')
def logout():
    """登出"""
    session.clear()
    return redirect(url_for('login'))


@auth_bp.route('/api/logout', methods=['POST'])
def api_logout():
    """API登出端点"""
    session.clear()
    return jsonify({
        'success': True,
        'message': '登出成功'
    })
