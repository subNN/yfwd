import time
import random
import re
import uuid
from flask import Blueprint, request, jsonify
from utils.auth import Auth
from config import Config

auth_bp = Blueprint('auth', __name__)


def _get_client_ip():
    fwd = request.headers.get('X-Forwarded-For', '')
    if fwd:
        return fwd.split(',')[0].strip()
    return request.remote_addr or '0.0.0.0'


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


# ========== 人机验证 ==========

@auth_bp.route('/auth/captcha', methods=['GET'])
def get_captcha():
    """获取柱状图排序验证码，返回 captcha_id + 柱子高度数组"""
    captcha_id = uuid.uuid4().hex[:12]

    bar_count = 6
    heights = random.sample(range(25, 101), bar_count)
    bars = []
    for i, h in enumerate(heights):
        bars.append({'id': f'b{i + 1}', 'height': h})

    sorted_bars = sorted(bars, key=lambda b: b['height'], reverse=True)
    answer_text = ','.join([b['id'] for b in sorted_bars])
    question_text = '请按从高到低的顺序排列柱状图'

    db = auth_bp.db
    db.save_captcha(captcha_id, answer_text, question_text)

    return ok(
        captcha_id=captcha_id,
        question=question_text,
        bars=bars,
        direction='desc',
        time_limit=20,
        expire_in=Config.CAPTCHA_TTL
    )


# ========== 验证人机验证（不发送邮件） ==========

@auth_bp.route('/auth/verify-captcha', methods=['POST'])
def verify_captcha_only():
    """仅验证人机验证是否通过（不消耗验证码），用户拖动完成后调用"""
    body = request.get_json(silent=True) or {}
    captcha_id = (body.get('captcha_id') or '').strip()
    captcha_answer = (body.get('captcha_answer') or '').strip()

    if not captcha_id or not captcha_answer:
        return err('CAPTCHA_MISSING', '验证码参数缺失')

    db = auth_bp.db
    # mark_used=False：只检查不消耗，后续 send-code 会真正消耗
    captcha_ok, captcha_err = db.verify_captcha(captcha_id, captcha_answer, mark_used=False)
    if not captcha_ok:
        return err('CAPTCHA_FAILED', captcha_err)

    return ok(message='人机验证通过')


# ========== 发送验证码 ==========

@auth_bp.route('/auth/send-code', methods=['POST'])
def send_code():
    body = request.get_json(silent=True) or {}
    email = (body.get('email') or '').strip().lower()
    purpose = body.get('purpose', 'register')
    captcha_id = (body.get('captcha_id') or '').strip()
    captcha_answer = (body.get('captcha_answer') or '').strip()

    if not email:
        return err('EMAIL_REQUIRED', '请输入邮箱')
    if not Auth.is_valid_email(email):
        return err('EMAIL_INVALID', '邮箱格式不正确（支持任意邮箱）')

    ip = _get_client_ip()

    # 人机验证
    db = auth_bp.db
    if not captcha_id or not captcha_answer:
        return err('CAPTCHA_REQUIRED', '请完成人机验证')
    captcha_ok, captcha_err = db.verify_captcha(captcha_id, captcha_answer)
    if not captcha_ok:
        return err('CAPTCHA_FAILED', captcha_err)

    # 注册场景：检查邮箱是否已注册
    if purpose == 'register':
        existing = db.get_user_by_email(email)
        if existing:
            return err('EMAIL_REGISTERED', '该邮箱已注册，请直接登录', 409)

    # IP 维度限流
    ip_send_count = db.get_ip_rate_limit(ip, 'send')
    if ip_send_count >= Config.IP_DAILY_SEND_LIMIT:
        return err('RATE_LIMIT_IP', f'今日该 IP 发送次数已达上限（{Config.IP_DAILY_SEND_LIMIT} 次）', 429)

    # 邮箱维度限流
    email_send_count = db.get_email_send_count(email)
    if email_send_count >= Config.EMAIL_DAILY_SEND_LIMIT:
        return err('RATE_LIMIT_EMAIL', '该邮箱发送次数过多，请 10 分钟后再试', 429)

    # 重发冷却
    last_send = db.get_last_code_send_time(email)
    if last_send:
        try:
            last_ts = time.mktime(time.strptime(last_send.split('.')[0], '%Y-%m-%d %H:%M:%S'))
        except Exception:
            last_ts = 0
        elapsed = time.time() - last_ts
        if elapsed < Config.RESEND_COOLDOWN:
            wait = int(Config.RESEND_COOLDOWN - elapsed) + 1
            return err('RATE_LIMIT_RESEND', f'发送过于频繁，请 {wait} 秒后再试', 429)

    # 生成验证码
    code = ''.join(random.choices('0123456789', k=Config.CODE_LEN))

    # 发送邮件
    sent, send_err = Auth.send_verification_code(email, code)
    if not sent:
        return err('MAIL_SEND_FAIL', send_err or '邮件发送失败，请稍后重试', 500)

    # 存库
    code_hash = Auth.hash_code(code)
    expires_at = time.time() + Config.CODE_TTL
    db.save_verification_code(email, code_hash, purpose, ip, expires_at)
    db.incr_ip_rate_limit(ip, 'send')
    db.incr_email_send_count(email)

    print(f'[认证] 验证码已发送: email={email}, ip={ip}')
    response = {'cooldown': Config.RESEND_COOLDOWN, 'expire_in': Config.CODE_TTL}
    if Config.SMTP_MOCK:
        response['mock_code'] = code
    return ok(message='验证码已发送', **response)


# ========== 注册 ==========

@auth_bp.route('/auth/register', methods=['POST'])
def register():
    body = request.get_json(silent=True) or {}
    email = (body.get('email') or '').strip().lower()
    code = (body.get('code') or '').strip()
    password = body.get('password') or ''
    nickname = (body.get('nickname') or '').strip() or email.split('@')[0]

    if not Auth.is_valid_email(email):
        return err('EMAIL_INVALID', '邮箱格式不正确')
    if not code:
        return err('CODE_REQUIRED', '请输入验证码')
    if not re.fullmatch(r'\d{4,8}', code):
        return err('CODE_FORMAT', '验证码格式不正确')
    if len(password) < Config.PASSWORD_MIN_LENGTH:
        return err('PASSWORD_TOO_SHORT', f'密码至少 {Config.PASSWORD_MIN_LENGTH} 位')

    db = auth_bp.db

    # 邮箱是否已注册
    if db.get_user_by_email(email):
        return err('EMAIL_REGISTERED', '该邮箱已注册，请直接登录', 409)

    # 验证码校验
    code_record = db.get_verification_code(email)
    if not code_record:
        return err('CODE_WRONG', '验证码错误或已过期，请重新获取')
    if code_record[7] > 0:  # used 字段
        return err('CODE_WRONG', '验证码错误或已过期，请重新获取')
    if code_record[6] < time.time():  # expires_at 字段 (REAL/float)
        return err('CODE_EXPIRED', '验证码已过期，请重新获取')
    if code_record[2] != Auth.hash_code(code):  # code_hash 字段
        return err('CODE_WRONG', '验证码错误')

    # IP 注册限流
    ip = _get_client_ip()
    ip_reg_count = db.get_ip_rate_limit(ip, 'register')
    if ip_reg_count >= Config.IP_DAILY_REGISTER_LIMIT:
        return err('RATE_LIMIT_IP', f'今日该 IP 注册次数已达上限（{Config.IP_DAILY_REGISTER_LIMIT} 次）', 429)

    # 标记验证码已用
    db.mark_code_used(code_record[0])

    # 创建用户
    password_hash = Auth.hash_password(password)
    user_id = db.register_user(email, password_hash, nickname)
    if not user_id:
        return err('SERVER_ERROR', '注册失败，请稍后重试', 500)

    db.incr_ip_rate_limit(ip, 'register')
    token = Auth.generate_token(user_id, email)
    user = db.get_user_by_id(user_id)

    print(f'[认证] 注册成功: id={user_id}, email={email}')
    return ok(token=token, user=db.user_to_dict(user))


# ========== 登录 ==========

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    body = request.get_json(silent=True) or {}
    email = (body.get('email') or '').strip().lower()
    password = body.get('password') or ''
    remember = bool(body.get('remember'))

    if not Auth.is_valid_email(email):
        return err('EMAIL_INVALID', '邮箱格式不正确')
    if not password:
        return err('PASSWORD_REQUIRED', '请输入密码')

    db = auth_bp.db

    # 查找用户
    user = db.get_user_by_email(email)
    if not user:
        return err('USER_NOT_FOUND', '该邮箱未注册', 401)

    # 检查是否被锁定
    fail_record = db.get_login_failures(email)
    if fail_record and fail_record[1] > time.time():
        remaining = int(fail_record[1] - time.time())
        return err('USER_LOCKED', f'账号因多次密码错误被锁定，请 {remaining} 秒后再试', 423)

    # 验证密码
    password_hash = user[3] if len(user) > 3 else ''
    if not Auth.check_password(password, password_hash):
        db.incr_login_failure(email, Config.LOGIN_MAX_FAIL, Config.LOGIN_LOCK_SECONDS)
        return err('PASSWORD_WRONG', '邮箱或密码错误', 401)

    # 登录成功
    db.reset_login_failures(email)
    db.update_user_login(user[0])
    token = Auth.generate_token(user[0], email, remember)

    print(f'[认证] 登录成功: id={user[0]}, email={email}')
    return ok(token=token, user=db.user_to_dict(user))


# ========== 获取当前用户 ==========

@auth_bp.route('/auth/me', methods=['GET'])
def me():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return err('TOKEN_MISSING', '未登录', 401)
    token = auth_header[7:]

    payload = Auth.decode_token(token)
    if not payload:
        return err('TOKEN_INVALID', 'token 无效或已过期', 401)

    user = auth_bp.db.get_user_by_id(payload.get('user_id'))
    if not user:
        return err('TOKEN_INVALID', '用户不存在', 401)

    return ok(user=auth_bp.db.user_to_dict(user))


# ========== 退出登录 ==========

@auth_bp.route('/auth/logout', methods=['POST'])
def logout():
    return ok(message='已退出')


# ========== 更新用户资料 ==========

@auth_bp.route('/auth/profile', methods=['PUT'])
def update_profile():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return err('TOKEN_MISSING', '未登录', 401)
    token = auth_header[7:]

    payload = Auth.decode_token(token)
    if not payload:
        return err('TOKEN_INVALID', 'token 无效或已过期', 401)

    user_id = payload.get('user_id')
    user = auth_bp.db.get_user_by_id(user_id)
    if not user:
        return err('TOKEN_INVALID', '用户不存在', 401)

    body = request.get_json(silent=True) or {}
    nickname = (body.get('nickname') or '').strip()

    if not nickname:
        return err('NICKNAME_EMPTY', '昵称不能为空', 400)

    if len(nickname) > 20:
        return err('NICKNAME_TOO_LONG', '昵称不能超过 20 个字符', 400)

    success = auth_bp.db.update_user_nickname(user_id, nickname)
    if not success:
        return err('UPDATE_FAILED', '更新失败，请稍后重试', 500)

    updated_user = auth_bp.db.get_user_by_id(user_id)
    return ok(user=auth_bp.db.user_to_dict(updated_user), message='昵称已更新')


# ========== 忘记密码：检查用户 ==========

@auth_bp.route('/auth/forgot-password', methods=['POST'])
def forgot_password():
    body = request.get_json(silent=True) or {}
    email = (body.get('email') or '').strip().lower()

    if not email:
        return err('EMAIL_REQUIRED', '请输入邮箱')
    if not Auth.is_valid_email(email):
        return err('EMAIL_INVALID', '邮箱格式不正确（支持任意邮箱）')

    db = auth_bp.db
    user = db.get_user_by_email(email)
    if not user:
        return err('USER_NOT_FOUND', '当前用户不存在', 404)

    print(f'[认证] 忘记密码请求: email={email}')
    return ok(message='用户存在', email=email)


# ========== 重置密码 ==========

@auth_bp.route('/auth/reset-password', methods=['POST'])
def reset_password():
    body = request.get_json(silent=True) or {}
    email = (body.get('email') or '').strip().lower()
    code = (body.get('code') or '').strip()
    new_password = (body.get('password') or '')

    if not email:
        return err('EMAIL_REQUIRED', '请输入邮箱')
    if not Auth.is_valid_email(email):
        return err('EMAIL_INVALID', '邮箱格式不正确')
    if not code:
        return err('CODE_REQUIRED', '请输入验证码')
    if not re.fullmatch(r'\d{4,8}', code):
        return err('CODE_FORMAT', '验证码格式不正确')
    if not new_password:
        return err('PASSWORD_REQUIRED', '请输入新密码')
    if len(new_password) < Config.PASSWORD_MIN_LENGTH:
        return err('PASSWORD_TOO_SHORT', f'密码至少 {Config.PASSWORD_MIN_LENGTH} 位')

    db = auth_bp.db
    user = db.get_user_by_email(email)
    if not user:
        return err('USER_NOT_FOUND', '当前用户不存在', 404)

    # 验证码校验（同时支持 'reset' 和 'reset-password' 两种 purpose）
    code_record = db.get_verification_code(email, 'reset-password')
    if not code_record:
        code_record = db.get_verification_code(email, 'reset')
    if not code_record:
        return err('CODE_WRONG', '验证码错误或已过期，请重新获取')
    if code_record[7] > 0:
        return err('CODE_WRONG', '验证码错误或已过期，请重新获取')
    if code_record[6] < time.time():
        return err('CODE_EXPIRED', '验证码已过期，请重新获取')
    if code_record[2] != Auth.hash_code(code):
        return err('CODE_WRONG', '验证码错误')

    # 标记验证码已用
    db.mark_code_used(code_record[0])

    # 更新密码
    new_password_hash = Auth.hash_password(new_password)
    success = db.update_user_password(user[0], new_password_hash)
    if not success:
        return err('UPDATE_FAIL', '密码更新失败，请稍后重试', 500)

    print(f'[认证] 密码重置成功: email={email}')
    return ok(message='密码重置成功')


# ========== 健康检查 ==========

@auth_bp.route('/health', methods=['GET'])
def health_check():
    from datetime import datetime
    return jsonify({
        'status': 'ok',
        'message': '服务运行中',
        'timestamp': datetime.now().isoformat()
    })


@auth_bp.route('/auth/smtp-check', methods=['GET'])
def smtp_check():
    config = Auth.check_smtp_config()
    success, message = Auth.test_smtp_login()
    return jsonify({
        'success': success,
        'message': message,
        'config': config,
    }), 200 if success else 500