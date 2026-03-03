from functools import wraps
from flask import session, redirect, url_for, jsonify, request


def login_required(f):
    """登录检查装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            # 检查是否是API请求
            if request.path.startswith('/api/'):
                # API请求返回JSON格式的错误信息
                return jsonify({'error': '未登录，请先登录'}), 401
            else:
                # 非API请求重定向到登录页面
                return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """管理员权限检查装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            # 检查是否是API请求
            if request.path.startswith('/api/'):
                # API请求返回JSON格式的错误信息
                return jsonify({'error': '未登录，请先登录'}), 401
            else:
                # 非API请求重定向到登录页面
                return redirect(url_for('login'))
        if session.get('role') != 'admin':
            # 检查是否是API请求
            if request.path.startswith('/api/'):
                # API请求返回JSON格式的错误信息
                return jsonify({'error': '权限不足，需要管理员权限'}), 403
            else:
                # 非API请求返回错误页面或重定向
                from flask import render_template
                return render_template('error.html', message='权限不足，需要管理员权限'), 403
        return f(*args, **kwargs)
    return decorated_function
