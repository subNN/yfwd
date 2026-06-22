"""AI 对话接口 - 创建菜单 / 推荐菜品"""

from flask import Blueprint, request, jsonify
from utils.auth import Auth
from utils.ai_client import AIClient
from config import Config

ai_bp = Blueprint('ai', __name__)


def _get_user_from_token():
    """从请求中解析当前用户"""
    auth_header = request.headers.get('Authorization', '')
    token_header = request.headers.get('token', '')
    token = None
    if auth_header.startswith('Bearer '):
        token = auth_header[7:]
    elif auth_header:
        token = auth_header
    elif token_header:
        token = token_header

    if not token:
        return None

    payload = Auth.decode_token(token)
    if not payload:
        return None
    if payload.get('is_admin'):
        return None  # 管理员不能使用 AI 功能

    user = ai_bp.db.get_user_by_id(payload.get('user_id'))
    return user


def _get_user_menus_context(user_id):
    """获取用户已有菜单供 AI 参考"""
    try:
        menus = ai_bp.db.get_user_menus(user_id)
        if not menus:
            return ''
        summaries = []
        for m in menus[-5:]:  # 最近 5 个
            names = [d.get('name', '') for d in (m.get('dishes', []) or [])]
            summaries.append(f"菜单「{m.get('name','')}」: {', '.join(names)}")
        return '；'.join(summaries)
    except Exception:
        return ''


def ok(data=None, message=None, **extra):
    payload = {'success': True}
    if message:
        payload['message'] = message
    if isinstance(data, dict):
        payload.update(data)
    elif data is not None:
        payload['data'] = data
    payload.update(extra)
    return jsonify(payload)


def err(error, message, status=400):
    return jsonify({'success': False, 'error': error, 'message': message}), status


# ==============================
#  AI 健康检查
# ==============================

@ai_bp.route('/ai/status', methods=['GET'])
def ai_status():
    return ok(enabled=AIClient.is_enabled(), model=Config.AI_MODEL)


# ==============================
#  AI 通用对话
# ==============================

@ai_bp.route('/ai/chat', methods=['POST'])
def ai_chat():
    """AI 通用对话：可自然语言创建菜单、推荐菜品、闲聊"""
    if not AIClient.is_enabled():
        return err('AI_DISABLED', 'AI 服务未配置，请联系管理员')

    user = _get_user_from_token()
    if not user:
        return err('TOKEN_INVALID', '请先登录', 401)

    body = request.get_json(silent=True) or {}
    message = (body.get('message') or '').strip()

    if not message:
        return err('MESSAGE_REQUIRED', '请输入消息')

    context = _get_user_menus_context(user[0])

    result = AIClient.chat(message, context)
    if not result.get('success'):
        return err('AI_ERROR', result.get('error', 'AI 服务异常'), 500)

    if result.get('type') == 'action':
        action = result.get('data', {})
        if action.get('action') == 'create_menu':
            result['menu_id'] = None
            result['saved'] = False

    return jsonify(result)


# ==============================
#  AI 创建菜单
# ==============================

@ai_bp.route('/ai/create-menu', methods=['POST'])
def ai_create_menu():
    """根据描述生成菜单，默认不保存"""
    if not AIClient.is_enabled():
        return err('AI_DISABLED', 'AI 服务未配置')

    user = _get_user_from_token()
    if not user:
        return err('TOKEN_INVALID', '请先登录', 401)

    body = request.get_json(silent=True) or {}
    description = (body.get('description') or '').strip()
    auto_save = bool(body.get('save', False))

    if not description:
        return err('DESCRIPTION_REQUIRED', '请描述你想创建的菜单')

    context = _get_user_menus_context(user[0])

    result = AIClient.create_menu(description, context)
    if not result.get('success'):
        return err('AI_ERROR', result.get('error', 'AI 服务异常'), 500)

    menu = result.get('menu', {})
    text_intro = result.get('text_intro', '')
    raw_json = result.get('raw_json', '')
    menu_id = None

    if auto_save:
        try:
            menu_id = ai_bp.db.add_menu(
                user[0],
                menu.get('name', description[:20]),
                menu.get('dishes', [])
            )
            print(f'[AI] 创建菜单成功: id={menu_id}, user_id={user[0]}')
        except Exception as e:
            print(f'[AI] 保存菜单失败: {e}')
            return err('SAVE_FAILED', f'菜单已生成但保存失败: {e}', 500)

    return ok(menu=menu, menu_id=menu_id, saved=bool(menu_id),
               text_intro=text_intro, raw_json=raw_json)


# ==============================
#  AI 推荐菜品
# ==============================

@ai_bp.route('/ai/recommend', methods=['POST'])
def ai_recommend():
    """根据用户偏好推荐菜品"""
    if not AIClient.is_enabled():
        return err('AI_DISABLED', 'AI 服务未配置')

    user = _get_user_from_token()
    if not user:
        return err('TOKEN_INVALID', '请先登录', 401)

    body = request.get_json(silent=True) or {}
    preference = (body.get('preference') or body.get('query') or '').strip()
    exclude = (body.get('exclude') or '').strip()
    count = body.get('count', 5)

    if not preference:
        return err('PREFERENCE_REQUIRED', '请描述你的口味偏好')

    result = AIClient.recommend(preference, exclude, count)
    if not result.get('success'):
        return err('AI_ERROR', result.get('error', 'AI 服务异常'), 500)

    data = result.get('data', {})
    text_intro = result.get('text_intro', '')
    raw_json = result.get('raw_json', '')

    return ok(**data, text_intro=text_intro, raw_json=raw_json)