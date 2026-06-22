from flask import Blueprint, request, jsonify
from utils.decorators import login_required

user_bp = Blueprint('user', __name__)


@user_bp.route('/info', methods=['GET'])
@login_required
def get_my_info():
    """获取当前用户信息"""
    try:
        user = user_bp.db.get_user_by_id(request.user_id)
        if not user:
            return jsonify({'error': '用户不存在', 'code': 'USER_NOT_FOUND'}), 404

        return jsonify({
            'success': True,
            'user': user_bp.db.user_to_dict(user)
        })
    except Exception as e:
        print(f"[用户] 获取信息错误: {e}")
        return jsonify({'error': f'获取用户信息失败: {str(e)}', 'code': 'GET_ERROR'}), 500


# ========== 菜单 - 批量导入导出（静态路由必须放在动态路由之前！） ==========

@user_bp.route('/menus/export', methods=['GET'])
@login_required
def export_my_menus():
    """导出当前用户的所有菜单数据（包含 uuid）"""
    try:
        menus = user_bp.db.get_user_menus(request.user_id)
        cleaned_menus = []
        for m in menus:
            menu_data = {
                'name': m.get('name', ''),
                'dishes': m.get('dishes', [])
            }
            if m.get('uuid'):
                menu_data['uuid'] = m.get('uuid')
            cleaned_menus.append(menu_data)

        return jsonify({
            'success': True,
            'menus': cleaned_menus,
            'total': len(cleaned_menus)
        })
    except Exception as e:
        print(f"[用户] 导出菜单错误: {e}")
        return jsonify({'error': f'导出失败: {str(e)}', 'code': 'EXPORT_ERROR'}), 500


@user_bp.route('/menus/import', methods=['POST'])
@login_required
def import_my_menus():
    """批量导入菜单数据 - 基于 uuid 的时间戳比较策略（merge 模式）"""
    try:
        body = request.get_json(silent=True) or {}
        if isinstance(body, list):
            data = body
        elif isinstance(body, dict):
            data = body.get('menus') or body.get('data') or body.get('items') or body
        else:
            data = body

        menus_to_import = []
        if isinstance(data, list):
            menus_to_import = data
        elif isinstance(data, dict):
            if 'menus' in data and isinstance(data['menus'], list):
                menus_to_import = data['menus']
            elif 'name' in data or 'dishes' in data:
                menus_to_import = [data]

        if not menus_to_import or not isinstance(menus_to_import, list) or len(menus_to_import) == 0:
            return jsonify({'error': '数据格式不正确，请提供菜单数组', 'code': 'INVALID_FORMAT'}), 400

        mode = 'merge'
        if isinstance(body, dict):
            mode = body.get('mode') or 'merge'

        if mode == 'replace':
            existing_menus = user_bp.db.get_user_menus(request.user_id)
            for m in existing_menus:
                if m.get('id'):
                    user_bp.db.delete_menu(m['id'])

        success_count = 0
        skip_count = 0
        imported_ids = []

        for item in menus_to_import:
            if not isinstance(item, dict):
                skip_count += 1
                continue

            name = (item.get('name') or item.get('title') or '').strip()
            dishes = item.get('dishes') or item.get('items') or item.get('foods') or []
            item_uuid = item.get('uuid') or item.get('id_str') or None

            if not name:
                skip_count += 1
                continue

            if not isinstance(dishes, list) or len(dishes) == 0:
                skip_count += 1
                continue

            cleaned_dishes = []
            for d in dishes:
                if not isinstance(d, dict) or not d.get('name'):
                    continue
                cleaned_dishes.append({
                    'name': str(d.get('name')).strip(),
                    'price': float(d.get('price') or 0),
                    'unit': str(d.get('unit') or '份'),
                })

            if not cleaned_dishes:
                skip_count += 1
                continue

            # uuid 策略：如果数据带有 uuid，先尝试通过 uuid 匹配现有记录并比较时间戳
            if item_uuid and isinstance(item_uuid, str) and item_uuid.startswith('cd-'):
                # 检查是否为有效 uuid
                parsed = user_bp.db._parse_uuid(item_uuid)
                if parsed is not None:
                    # 尝试通过 uuid 匹配并更新（时间戳策略）
                    match_result = user_bp.db._update_menu_by_uuid_match(
                        item_uuid, request.user_id, name, cleaned_dishes
                    )
                    if match_result == -1:
                        # 云端数据更新，跳过
                        skip_count += 1
                        continue
                    elif match_result is not None:
                        # 匹配并更新成功
                        success_count += 1
                        imported_ids.append(match_result)
                        continue

            # 无 uuid 或匹配失败，直接作为新菜单插入
            menu_id = user_bp.db.add_menu(request.user_id, name, cleaned_dishes, uuid=item_uuid)
            if menu_id:
                success_count += 1
                imported_ids.append(menu_id)
            else:
                skip_count += 1

        updated_menus = user_bp.db.get_user_menus(request.user_id)
        print(f"[用户] 导入菜单: user_id={request.user_id}, mode={mode}, 成功={success_count}, 跳过={skip_count}")
        return jsonify({
            'success': True,
            'imported_count': success_count,
            'skipped_count': skip_count,
            'total_count': len(updated_menus),
            'imported_ids': imported_ids,
            'menus': updated_menus,
            'message': f'成功导入 {success_count} 个菜单' + (f'，跳过 {skip_count} 个' if skip_count > 0 else '')
        })
    except Exception as e:
        print(f"[用户] 导入菜单错误: {e}")
        return jsonify({'error': f'导入失败: {str(e)}', 'code': 'IMPORT_ERROR'}), 500


# ========== 菜单 CRUD（动态路由放在静态路由之后！） ==========

@user_bp.route('/menus', methods=['GET'])
@login_required
def get_my_menus():
    """获取当前用户的菜单列表"""
    try:
        menus = user_bp.db.get_user_menus(request.user_id)
        return jsonify({
            'success': True,
            'menus': menus
        })
    except Exception as e:
        print(f"[用户] 获取菜单错误: {e}")
        return jsonify({'error': f'获取菜单失败: {str(e)}', 'code': 'GET_ERROR'}), 500


@user_bp.route('/menus', methods=['POST'])
@login_required
def create_menu():
    """新建菜单（手动保存）"""
    try:
        body = request.get_json(silent=True) or {}
        name = (body.get('name') or '').strip()
        dishes = body.get('dishes') or []

        if not name:
            return jsonify({'error': '请输入菜单名称', 'code': 'NAME_REQUIRED'}), 400
        if not isinstance(dishes, list) or len(dishes) == 0:
            return jsonify({'error': '请至少添加一个菜品', 'code': 'DISHES_EMPTY'}), 400

        cleaned_dishes = []
        for d in dishes:
            if not isinstance(d, dict) or not d.get('name'):
                continue
            cleaned_dishes.append({
                'name': str(d.get('name')).strip(),
                'price': float(d.get('price') or 0),
                'unit': str(d.get('unit') or '份'),
            })
        if not cleaned_dishes:
            return jsonify({'error': '菜品格式不正确', 'code': 'DISHES_INVALID'}), 400

        menu_id = user_bp.db.add_menu(request.user_id, name, cleaned_dishes)
        menu = user_bp.db.get_menu_by_id(menu_id, request.user_id)

        print(f"[用户] 新建菜单: user_id={request.user_id}, menu_id={menu_id}, name={name}")
        return jsonify({
            'success': True,
            'menu': menu,
            'message': '菜单已保存'
        })
    except Exception as e:
        print(f"[用户] 新建菜单错误: {e}")
        return jsonify({'error': f'保存失败: {str(e)}', 'code': 'SAVE_ERROR'}), 500


@user_bp.route('/menus/<int:menu_id>', methods=['GET'])
@login_required
def get_my_menu_detail(menu_id):
    """获取单个菜单详情"""
    try:
        menu = user_bp.db.get_menu_by_id(menu_id, request.user_id)
        if not menu:
            return jsonify({'error': '菜单不存在', 'code': 'NOT_FOUND'}), 404
        return jsonify({
            'success': True,
            'menu': menu
        })
    except Exception as e:
        print(f"[用户] 获取菜单详情错误: {e}")
        return jsonify({'error': f'获取菜单失败: {str(e)}', 'code': 'GET_ERROR'}), 500


@user_bp.route('/menus/<int:menu_id>', methods=['PUT'])
@login_required
def update_my_menu(menu_id):
    """更新菜单"""
    try:
        menu = user_bp.db.get_menu_by_id(menu_id, request.user_id)
        if not menu:
            return jsonify({'error': '菜单不存在', 'code': 'NOT_FOUND'}), 404

        body = request.get_json(silent=True) or {}
        name = (body.get('name') or '').strip() or menu['name']
        dishes = body.get('dishes') or menu['dishes']

        cleaned_dishes = []
        for d in dishes:
            if not isinstance(d, dict) or not d.get('name'):
                continue
            cleaned_dishes.append({
                'name': str(d.get('name')).strip(),
                'price': float(d.get('price') or 0),
                'unit': str(d.get('unit') or '份'),
            })

        user_bp.db.update_menu(menu_id, name, cleaned_dishes)
        updated = user_bp.db.get_menu_by_id(menu_id, request.user_id)

        print(f"[用户] 更新菜单: menu_id={menu_id}")
        return jsonify({
            'success': True,
            'menu': updated,
            'message': '菜单已更新'
        })
    except Exception as e:
        print(f"[用户] 更新菜单错误: {e}")
        return jsonify({'error': f'更新失败: {str(e)}', 'code': 'UPDATE_ERROR'}), 500


@user_bp.route('/menus/<int:menu_id>', methods=['DELETE'])
@login_required
def delete_my_menu(menu_id):
    """删除菜单"""
    try:
        menu = user_bp.db.get_menu_by_id(menu_id, request.user_id)
        if not menu:
            return jsonify({'error': '菜单不存在', 'code': 'NOT_FOUND'}), 404

        ok_del = user_bp.db.delete_menu(menu_id)
        if not ok_del:
            return jsonify({'error': '删除失败', 'code': 'DELETE_ERROR'}), 500

        print(f"[用户] 删除菜单: menu_id={menu_id}")
        return jsonify({
            'success': True,
            'message': '菜单已删除'
        })
    except Exception as e:
        print(f"[用户] 删除菜单错误: {e}")
        return jsonify({'error': f'删除失败: {str(e)}', 'code': 'DELETE_ERROR'}), 500


# ========== 点菜订单 - 批量导入导出（静态路由必须放在动态路由之前！） ==========

@user_bp.route('/orders/export', methods=['GET'])
@login_required
def export_my_orders():
    """导出当前用户的所有点菜记录"""
    try:
        orders = user_bp.db.get_user_orders(request.user_id)
        return jsonify({
            'success': True,
            'orders': orders,
            'total': len(orders)
        })
    except Exception as e:
        print(f"[用户] 导出订单错误: {e}")
        return jsonify({'error': f'导出失败: {str(e)}', 'code': 'EXPORT_ERROR'}), 500


@user_bp.route('/orders/import', methods=['POST'])
@login_required
def import_my_orders():
    """批量导入点菜记录 - 基于 uuid 的时间戳比较策略"""
    try:
        body = request.get_json(silent=True) or {}
        if isinstance(body, list):
            data = body
        elif isinstance(body, dict):
            data = body.get('orders') or body.get('data') or body.get('items') or body.get('history') or body
        else:
            data = body

        orders_to_import = []
        if isinstance(data, list):
            orders_to_import = data
        elif isinstance(data, dict) and 'orders' in data and isinstance(data['orders'], list):
            orders_to_import = data['orders']

        if not orders_to_import or not isinstance(orders_to_import, list) or len(orders_to_import) == 0:
            return jsonify({'error': '数据格式不正确，请提供订单数组', 'code': 'INVALID_FORMAT'}), 400

        success_count = 0
        skip_count = 0
        imported_ids = []

        from datetime import datetime
        for item in orders_to_import:
            if not isinstance(item, dict):
                skip_count += 1
                continue

            meal_type = (item.get('meal_type') or item.get('meal') or '').strip()
            selected_dishes = item.get('selected_dishes') or item.get('dishes') or item.get('items') or []
            order_time = item.get('order_time') or item.get('time') or item.get('created_at') or None
            item_uuid = item.get('uuid') or item.get('id_str') or None

            if not meal_type:
                skip_count += 1
                continue

            if not isinstance(selected_dishes, list) or len(selected_dishes) == 0:
                skip_count += 1
                continue

            cleaned_dishes = []
            for d in selected_dishes:
                if not isinstance(d, dict) or not d.get('name'):
                    continue
                cleaned_dishes.append({
                    'name': str(d.get('name')).strip(),
                    'price': float(d.get('price') or 0),
                    'unit': str(d.get('unit') or '份'),
                    'quantity': int(d.get('quantity') or 1),
                })

            if not cleaned_dishes:
                skip_count += 1
                continue

            # uuid 策略：如果数据带有 uuid，先尝试通过 uuid 匹配现有记录并比较时间戳
            if item_uuid and isinstance(item_uuid, str) and item_uuid.startswith('dc-'):
                parsed = user_bp.db._parse_uuid(item_uuid)
                if parsed is not None:
                    match_result = user_bp.db._update_order_by_uuid_match(
                        item_uuid, request.user_id, meal_type, cleaned_dishes, order_time
                    )
                    if match_result == -1:
                        skip_count += 1
                        continue
                    elif match_result is not None:
                        success_count += 1
                        imported_ids.append(match_result)
                        continue

            # 无 uuid 或匹配失败，直接作为新订单插入
            order_id = user_bp.db.add_order(
                request.user_id,
                None,
                meal_type,
                cleaned_dishes,
                order_time if order_time else datetime.now().isoformat(),
                uuid=item_uuid
            )
            if order_id:
                success_count += 1
                imported_ids.append(order_id)
            else:
                skip_count += 1

        updated_orders = user_bp.db.get_user_orders(request.user_id)
        print(f"[用户] 导入订单: user_id={request.user_id}, 成功={success_count}, 跳过={skip_count}")
        return jsonify({
            'success': True,
            'imported_count': success_count,
            'skipped_count': skip_count,
            'total_count': len(updated_orders),
            'imported_ids': imported_ids,
            'orders': updated_orders,
            'message': f'成功导入 {success_count} 条记录' + (f'，跳过 {skip_count} 条' if skip_count > 0 else '')
        })
    except Exception as e:
        print(f"[用户] 导入订单错误: {e}")
        return jsonify({'error': f'导入失败: {str(e)}', 'code': 'IMPORT_ERROR'}), 500


# ========== 点菜订单 CRUD（动态路由放在静态路由之后！） ==========

@user_bp.route('/orders', methods=['GET'])
@login_required
def get_my_orders():
    """获取当前用户的点菜记录"""
    try:
        orders = user_bp.db.get_user_orders(request.user_id)
        return jsonify({
            'success': True,
            'orders': orders
        })
    except Exception as e:
        print(f"[用户] 获取订单错误: {e}")
        return jsonify({'error': f'获取订单失败: {str(e)}', 'code': 'GET_ERROR'}), 500


@user_bp.route('/orders', methods=['POST'])
@login_required
def create_order():
    """提交点菜记录"""
    try:
        body = request.get_json(silent=True) or {}
        menu_id = body.get('menu_id')
        meal_type = (body.get('meal_type') or '').strip()
        selected_dishes = body.get('selected_dishes') or []

        if not meal_type:
            return jsonify({'error': '请选择餐别（早餐/午餐/晚餐等）', 'code': 'MEAL_TYPE_REQUIRED'}), 400
        if not isinstance(selected_dishes, list) or len(selected_dishes) == 0:
            return jsonify({'error': '请至少选择一个菜品', 'code': 'DISHES_EMPTY'}), 400

        if menu_id:
            menu = user_bp.db.get_menu_by_id(menu_id, request.user_id)
            if not menu:
                return jsonify({'error': '菜单不存在', 'code': 'MENU_NOT_FOUND'}), 404

        cleaned_dishes = []
        for d in selected_dishes:
            if not isinstance(d, dict) or not d.get('name'):
                continue
            cleaned_dishes.append({
                'name': str(d.get('name')).strip(),
                'price': float(d.get('price') or 0),
                'unit': str(d.get('unit') or '份'),
                'quantity': int(d.get('quantity') or 1),
            })
        if not cleaned_dishes:
            return jsonify({'error': '菜品格式不正确', 'code': 'DISHES_INVALID'}), 400

        from datetime import datetime
        order_time = datetime.now().isoformat()

        order_id = user_bp.db.add_order(
            request.user_id,
            menu_id,
            meal_type,
            cleaned_dishes,
            order_time
        )

        print(f"[用户] 提交点菜: user_id={request.user_id}, order_id={order_id}, meal_type={meal_type}, dishes={len(cleaned_dishes)}")
        return jsonify({
            'success': True,
            'order_id': order_id,
            'message': '点菜记录已保存'
        })
    except Exception as e:
        print(f"[用户] 提交点菜错误: {e}")
        return jsonify({'error': f'提交失败: {str(e)}', 'code': 'SAVE_ERROR'}), 500


@user_bp.route('/orders/<int:order_id>', methods=['DELETE'])
@login_required
def delete_my_order(order_id):
    """删除点菜记录"""
    try:
        ok_del = user_bp.db.delete_order(order_id, request.user_id)
        if not ok_del:
            return jsonify({'error': '记录不存在', 'code': 'NOT_FOUND'}), 404

        print(f"[用户] 删除点菜记录: order_id={order_id}")
        return jsonify({
            'success': True,
            'message': '记录已删除'
        })
    except Exception as e:
        print(f"[用户] 删除点菜记录错误: {e}")
        return jsonify({'error': f'删除失败: {str(e)}', 'code': 'DELETE_ERROR'}), 500
