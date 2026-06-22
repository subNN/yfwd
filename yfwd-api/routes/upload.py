from flask import Blueprint, request, jsonify
from utils.decorators import login_required

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/menus', methods=['POST'])
@login_required
def upload_menus():
    """上传菜单"""
    try:
        user_id = request.user_id
        data = request.json
        
        if not data or 'menus' not in data:
            return jsonify({'error': '缺少菜单数据', 'code': 'MISSING_DATA'}), 400
        
        menus = data['menus']
        if not isinstance(menus, list):
            return jsonify({'error': '菜单数据格式错误', 'code': 'INVALID_FORMAT'}), 400
        
        uploaded_count = 0
        updated_count = 0
        
        for menu_data in menus:
            if not isinstance(menu_data, dict) or 'name' not in menu_data or 'dishes' not in menu_data:
                continue
            
            name = menu_data['name']
            dishes = menu_data['dishes']
            
            # 检查是否已存在同名菜单
            user_menus = upload_bp.db.get_user_menus(user_id)
            existing_menu = None
            for menu in user_menus:
                if menu['name'] == name:
                    existing_menu = menu
                    break
            
            if existing_menu:
                # 更新现有菜单
                upload_bp.db.update_menu(existing_menu['id'], name, dishes)
                updated_count += 1
            else:
                # 添加新菜单
                upload_bp.db.add_menu(user_id, name, dishes)
                uploaded_count += 1
        
        return jsonify({
            'success': True,
            'message': f'上传成功，新增 {uploaded_count} 个菜单，更新 {updated_count} 个菜单'
        })
    except Exception as e:
        print(f"[上传] 上传菜单错误: {e}")
        return jsonify({'error': f'上传失败: {str(e)}', 'code': 'UPLOAD_ERROR'}), 500

@upload_bp.route('/orders', methods=['POST'])
@login_required
def upload_orders():
    """上传订单/选菜历史"""
    try:
        user_id = request.user_id
        data = request.json
        
        if not data or 'orders' not in data:
            return jsonify({'error': '缺少订单数据', 'code': 'MISSING_DATA'}), 400
        
        orders = data['orders']
        if not isinstance(orders, list):
            return jsonify({'error': '订单数据格式错误', 'code': 'INVALID_FORMAT'}), 400
        
        uploaded_count = 0
        duplicate_count = 0
        
        for order_data in orders:
            if not isinstance(order_data, dict):
                continue
            
            # 处理两种数据格式：
            # 1. 小程序格式: { meal, dishes, time, totalPrice }
            # 2. 后端格式: { menu_id, meal_type, selected_dishes }
            
            if 'meal_type' in order_data:
                meal_type = order_data['meal_type']
                selected_dishes = order_data.get('selected_dishes', [])
                menu_id = order_data.get('menu_id')
                order_time = order_data.get('order_time')
            elif 'meal' in order_data:
                meal_type = order_data['meal']
                selected_dishes = order_data.get('dishes', [])
                menu_id = order_data.get('menu_id', 0)  # 小程序格式没有menu_id
                order_time = order_data.get('time')  # 小程序格式的时间字段是time
            else:
                continue
            
            # 确保 selected_dishes 是列表
            if not isinstance(selected_dishes, list):
                selected_dishes = []
            
            # 检查订单是否重复
            if upload_bp.db.is_order_duplicate(user_id, meal_type, selected_dishes):
                duplicate_count += 1
                continue
            
            # 添加新订单
            upload_bp.db.add_order(user_id, menu_id, meal_type, selected_dishes, order_time)
            uploaded_count += 1
        
        if uploaded_count == 0 and duplicate_count > 0:
            return jsonify({
                'success': True,
                'message': '所有订单均已存在，无需重复上传'
            })
        
        return jsonify({
            'success': True,
            'message': f'上传成功，新增 {uploaded_count} 个订单，{duplicate_count} 个订单已存在'
        })
    except Exception as e:
        print(f"[上传] 上传订单错误: {e}")
        return jsonify({'error': f'上传失败: {str(e)}', 'code': 'UPLOAD_ERROR'}), 500