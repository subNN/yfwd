from functools import wraps
from flask import request, jsonify
from utils.auth import Auth

# 装饰器
def login_required(f):
    """用户登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 获取token - 支持 Authorization 和 token 两种 header
        auth_header = request.headers.get('Authorization', '')
        token_header = request.headers.get('token', '')

        # 优先使用 Authorization header
        token = None
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
        elif auth_header.startswith('token='):
            token = auth_header[6:]
        elif auth_header:
            token = auth_header
        elif token_header:
            # 支持 token header
            token = token_header
        else:
            print(f"[认证] 缺少token, path={request.path}")
            return jsonify({'error': '请先登录', 'code': 'TOKEN_REQUIRED'}), 401

        # 验证token
        payload = Auth.decode_token(token)
        if not payload:
            return jsonify({'error': '登录已过期，请重新登录', 'code': 'TOKEN_INVALID'}), 401

        # 检查是否是管理员
        if payload.get('is_admin'):
            return jsonify({'error': '需要用户账号', 'code': 'ADMIN_NOT_ALLOWED'}), 403

        # 将用户ID传递给路由函数
        request.user_id = payload.get('user_id')
        request.is_admin = payload.get('is_admin', False)

        print(f"[认证] 用户访问: user_id={request.user_id}, path={request.path}")
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """管理员验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 获取token - 支持 Authorization 和 token 两种 header
        auth_header = request.headers.get('Authorization', '')
        token_header = request.headers.get('token', '')

        # 优先使用 Authorization header
        token = None
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
        elif auth_header.startswith('token='):
            token = auth_header[6:]
        elif auth_header:
            token = auth_header
        elif token_header:
            # 支持 token header
            token = token_header
        else:
            print(f"[认证] 缺少管理员token, path={request.path}")
            return jsonify({'error': '需要管理员权限', 'code': 'TOKEN_REQUIRED'}), 401

        # 验证token
        payload = Auth.decode_token(token)
        if not payload:
            return jsonify({'error': '登录已过期，请重新登录', 'code': 'TOKEN_INVALID'}), 401

        # 检查是否是管理员
        if not payload.get('is_admin'):
            return jsonify({'error': '需要管理员权限', 'code': 'ADMIN_REQUIRED'}), 403

        # 将管理员ID传递给路由函数
        request.user_id = payload.get('user_id')
        request.is_admin = True

        print(f"[认证] 管理员访问: user_id={request.user_id}, path={request.path}")
        return f(*args, **kwargs)
    return decorated_function