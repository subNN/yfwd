import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ========== 环境变量辅助函数 ==========

def _get_env(key, default=''):
    """读取环境变量，空值视为未设置，返回默认值"""
    val = os.environ.get(key, '')
    if val is None or val.strip() == '':
        return default
    return val.strip()


# ========== 内置 .env 加载逻辑（不依赖 python-dotenv） ==========
# 在 config.py 被 import 时自动执行，保证任何启动方式都能正确读取配置
_env_path = os.path.join(BASE_DIR, '.env')
if os.path.exists(_env_path):
    try:
        with open(_env_path, 'r', encoding='utf-8') as _f:
            for _line in _f:
                _line = _line.strip()
                if not _line or _line.startswith('#'):
                    continue
                if '=' in _line:
                    _key, _value = _line.split('=', 1)
                    _key = _key.strip()
                    _value = _value.strip().strip('"').strip("'")
                    if _key and _value:  # 只有值非空时才覆盖
                        os.environ[_key] = _value
        print(f"[配置] 已加载 .env: {_env_path}")
    except Exception as _e:
        print(f"[配置] .env 读取失败: {_e}")
else:
    print(f"[配置] 未找到 .env（{_env_path}），使用默认值")


class Config:
    # Flask 配置
    SECRET_KEY = _get_env('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = _get_env('FLASK_DEBUG', '0') == '1'
    HOST = _get_env('HOST', 'your-host')
    PORT = int(_get_env('PORT', 'your-port'))
    CORS_ORIGINS = _get_env('CORS_ORIGINS', '*')

    # JWT 配置
    JWT_SECRET_KEY = _get_env('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ALGORITHM = 'HS256'
    JWT_TTL_NORMAL = 7 * 24 * 3600      # 7 天
    JWT_TTL_REMEMBER = 30 * 24 * 3600   # 30 天

    # QQ 邮箱 SMTP 配置（服务器用于发送验证码，也可配置其他邮箱，只是以QQ邮箱为例）
    QQ_EMAIL = _get_env('QQ_EMAIL', 'your@qq.com')
    QQ_EMAIL_AUTH_CODE = _get_env('QQ_EMAIL_AUTH_CODE', 'ycwkunovrjbgdccj')
    SMTP_HOST = _get_env('SMTP_HOST', 'smtp.qq.com')
    SMTP_PORT = int(_get_env('SMTP_PORT', '465'))
    SMTP_MOCK = _get_env('SMTP_MOCK', '0') == '1'

    # 验证码配置
    CODE_TTL = 10 * 60              # 10 分钟有效期
    CODE_LEN = 6                    # 6 位数字
    CODE_SALT = 'yfwd-static-salt'  # 验证码哈希盐值
    RESEND_COOLDOWN = 60            # 重发冷却 1 分钟

    # 限流配置
    IP_DAILY_SEND_LIMIT = 10        # 同 IP 一天发送验证码上限
    IP_DAILY_REGISTER_LIMIT = 10    # 同 IP 一天注册上限
    EMAIL_DAILY_SEND_LIMIT = 3      # 同一邮箱一天发送验证码上限（防止刷邮件）

    # 密码配置
    PASSWORD_MIN_LENGTH = 6         # 密码最小长度
    LOGIN_MAX_FAIL = 5              # 连续失败次数上限
    LOGIN_LOCK_SECONDS = 300        # 锁定 5 分钟

    # 通用邮箱正则
    EMAIL_REGEX = r'^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$'

    # 人机验证配置
    CAPTCHA_TTL = 5 * 60           # 验证问答 5 分钟有效
    CAPTCHA_COUNT = 2              # 生成 2 个算数题

    # AI 服务配置（兼容 OpenAI 接口格式）
    AI_ENABLED = _get_env('AI_ENABLED', '1') == '1'
    AI_API_URL = _get_env('AI_API_URL', 'https://api.openai.com/v1').rstrip('/')
    AI_API_KEY = _get_env('AI_API_KEY', 'sk-your-api-key-here')
    AI_MODEL = _get_env('AI_MODEL', 'gpt-3.5-turbo')
    AI_MAX_TOKENS = int(_get_env('AI_MAX_TOKENS', '2000'))
    AI_TEMPERATURE = float(_get_env('AI_TEMPERATURE', '0.7'))

    # 数据库配置
    DATABASE = _get_env('DATABASE', os.path.join(BASE_DIR, 'dining.db'))
