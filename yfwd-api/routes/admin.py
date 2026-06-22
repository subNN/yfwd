from flask import Blueprint, request, jsonify
from utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/login', methods=['POST'])
def admin_login():
    """管理员登录"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求格式错误', 'code': 'INVALID_DATA'}), 400

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': '用户名和密码必填', 'code': 'CREDENTIALS_REQUIRED'}), 400

        print(f"[管理员] 登录请求: username={username}")

        # 验证管理员账号
        if not admin_bp.db.verify_admin(username, password):
            print(f"[管理员] 登录失败: username={username}")
            return jsonify({'error': '凭据无效', 'code': 'INVALID_CREDENTIALS'}), 401

        # 生成管理员token
        from utils.auth import Auth
        token = Auth.generate_token(0, is_admin=True)

        print(f"[管理员] 登录成功: username={username}")

        return jsonify({
            'code': 0,
            'success': True,
            'token': token
        })

    except Exception as e:
        print(f"[管理员] 登录错误: {e}")
        return jsonify({'error': f'登录失败: {str(e)}', 'code': 'LOGIN_ERROR'}), 500

@admin_bp.route('/users', methods=['GET'])
@admin_required
def admin_get_users():
    """获取所有用户"""
    try:
        users = admin_bp.db.get_all_users()
        user_list = []
        for user in users:
            user_list.append({
                'id': user.get('id', user[0] if isinstance(user, (list, tuple)) else 0),
                'openid': user.get('openid', user[1] if isinstance(user, (list, tuple)) else ''),
                'nickname': user.get('nickname', user[2] if isinstance(user, (list, tuple)) else ''),
                'avatar_url': user.get('avatar_url', user[3] if isinstance(user, (list, tuple)) else ''),
                'created_at': user.get('created_at', user[4] if isinstance(user, (list, tuple)) else ''),
                'last_login_at': user.get('last_login_at', user[5] if isinstance(user, (list, tuple)) and len(user) > 5 else '')
            })

        return jsonify({
            'code': 0,
            'success': True,
            'data': user_list,
            'count': len(user_list)
        })
    except Exception as e:
        print(f"[管理员] 获取用户错误: {e}")
        return jsonify({'code': -1, 'message': f'获取用户失败: {str(e)}'}), 500

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def admin_delete_user(user_id):
    """删除用户"""
    try:
        admin_bp.db.delete_user(user_id)
        return jsonify({
            'code': 0,
            'success': True,
            'message': f'用户 {user_id} 已删除'
        })
    except Exception as e:
        print(f"[管理员] 删除用户错误: {e}")
        return jsonify({'code': -1, 'message': f'删除用户失败: {str(e)}'}), 500

@admin_bp.route('/menus', methods=['GET'])
@admin_required
def admin_get_menus():
    """获取所有菜单"""
    try:
        menus = admin_bp.db.get_all_menus()
        return jsonify({
            'code': 0,
            'success': True,
            'data': menus,
            'count': len(menus)
        })
    except Exception as e:
        print(f"[管理员] 获取菜单错误: {e}")
        return jsonify({'code': -1, 'message': f'获取菜单失败: {str(e)}'}), 500

@admin_bp.route('/menus/<int:menu_id>', methods=['DELETE'])
@admin_required
def admin_delete_menu(menu_id):
    """删除菜单"""
    try:
        if admin_bp.db.delete_menu(menu_id):
            return jsonify({
                'code': 0,
                'success': True,
                'message': f'菜单 {menu_id} 已删除'
            })
        else:
            return jsonify({'code': -1, 'message': '菜单不存在'}), 404
    except Exception as e:
        print(f"[管理员] 删除菜单错误: {e}")
        return jsonify({'code': -1, 'message': f'删除菜单失败: {str(e)}'}), 500

@admin_bp.route('/orders', methods=['GET'])
@admin_required
def admin_get_orders():
    """获取所有订单"""
    try:
        orders = admin_bp.db.get_all_orders()
        return jsonify({
            'code': 0,
            'success': True,
            'data': orders,
            'count': len(orders)
        })
    except Exception as e:
        print(f"[管理员] 获取订单错误: {e}")
        return jsonify({'code': -1, 'message': f'获取订单失败: {str(e)}'}), 500

@admin_bp.route('/orders/<int:order_id>', methods=['DELETE'])
@admin_required
def admin_delete_order(order_id):
    """删除订单"""
    try:
        if admin_bp.db.delete_order(order_id):
            return jsonify({
                'code': 0,
                'success': True,
                'message': f'订单 {order_id} 已删除'
            })
        else:
            return jsonify({'code': -1, 'message': '订单不存在'}), 404
    except Exception as e:
        print(f"[管理员] 删除订单错误: {e}")
        return jsonify({'code': -1, 'message': f'删除订单失败: {str(e)}'}), 500

@admin_bp.route('/stats', methods=['GET'])
@admin_required
def admin_get_stats():
    """获取统计数据"""
    try:
        stats = admin_bp.db.get_stats()
        return jsonify({
            'code': 0,
            'success': True,
            'data': {
                'userCount': stats['user_count'],
                'menuCount': stats['menu_count'],
                'orderCount': stats['order_count'],
                'todayOrderCount': stats['today_order_count']
            }
        })
    except Exception as e:
        print(f"[管理员] 获取统计错误: {e}")
        return jsonify({'code': -1, 'message': f'获取统计数据失败: {str(e)}'}), 500