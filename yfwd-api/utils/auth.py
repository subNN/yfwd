import jwt
import hmac
import hashlib
import secrets
import smtplib
import socket
import ssl
import re
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from config import Config

class Auth:
    # ========== 密码哈希 ==========

    @staticmethod
    def hash_password(password: str) -> str:
        """PBKDF2-SHA256 哈希密码，格式: pbkdf2$salt$hex"""
        salt = secrets.token_hex(8)
        h = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f'pbkdf2${salt}${h.hex()}'

    @staticmethod
    def check_password(password: str, stored: str) -> bool:
        """验证密码"""
        try:
            if not stored or '$' not in stored:
                return False
            parts = stored.split('$')
            if len(parts) < 3:
                return False
            algo, salt, h = parts[0], parts[1], parts[2]
            return hmac.compare_digest(
                hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex(),
                h,
            )
        except Exception:
            return False

    # ========== 验证码哈希 ==========

    @staticmethod
    def hash_code(code: str) -> str:
        return hashlib.sha256((code + Config.CODE_SALT).encode()).hexdigest()

    # ========== 邮箱格式校验 ==========

    EMAIL_RE = re.compile(Config.EMAIL_REGEX)

    @classmethod
    def is_valid_email(cls, email: str) -> bool:
        return bool(email and cls.EMAIL_RE.match(email))

    # ========== JWT Token ==========

    @staticmethod
    def generate_token(user_id: int, email: str = '', remember: bool = False, is_admin: bool = False) -> str:
        """生成 JWT token，remember=True 时 30 天有效"""
        ttl = Config.JWT_TTL_REMEMBER if remember else Config.JWT_TTL_NORMAL
        now = datetime.utcnow()
        payload = {
            'user_id': user_id,
            'email': email,
            'is_admin': is_admin,
            'iat': now,
            'exp': now + timedelta(seconds=ttl),
        }
        token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM)
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        return token

    @staticmethod
    def decode_token(token: str):
        """解码 JWT token"""
        try:
            return jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception:
            return None

    # ========== QQ 邮箱 SMTP 发送 ==========

    @staticmethod
    def check_smtp_config() -> dict:
        """检查SMTP基础配置，不返回敏感授权码"""
        return {
            'smtp_host': Config.SMTP_HOST,
            'smtp_port': Config.SMTP_PORT,
            'smtp_mock': Config.SMTP_MOCK,
            'qq_email': Config.QQ_EMAIL,
            'auth_code_configured': bool(Config.QQ_EMAIL_AUTH_CODE),
            'auth_code_length': len(Config.QQ_EMAIL_AUTH_CODE or ''),
        }

    @staticmethod
    def test_smtp_login() -> (bool, str):
        """测试SMTP连接和登录，不发送邮件"""
        if Config.SMTP_MOCK:
            return True, '当前为SMTP_MOCK模式，不会发送真实邮件'
        if not Config.QQ_EMAIL or '@' not in Config.QQ_EMAIL:
            return False, 'QQ_EMAIL配置不正确，请填写完整QQ邮箱地址'
        if not Config.QQ_EMAIL_AUTH_CODE:
            return False, 'QQ_EMAIL_AUTH_CODE未配置，请填写QQ邮箱SMTP授权码，不是QQ登录密码'
        try:
            with smtplib.SMTP_SSL(Config.SMTP_HOST, Config.SMTP_PORT, timeout=20) as s:
                s.login(Config.QQ_EMAIL, Config.QQ_EMAIL_AUTH_CODE)
            return True, 'SMTP连接和登录成功'
        except smtplib.SMTPAuthenticationError as e:
            detail = f'QQ邮箱认证失败: {e.smtp_error.decode("utf-8", "ignore") if isinstance(e.smtp_error, bytes) else e.smtp_error}'
            print(f"[邮件] {detail}")
            return False, detail
        except (socket.timeout, TimeoutError):
            detail = f'SMTP连接超时，请检查云服务器安全组/防火墙是否允许访问{Config.SMTP_HOST}:{Config.SMTP_PORT}'
            print(f"[邮件] {detail}")
            return False, detail
        except (socket.gaierror, ConnectionRefusedError, OSError) as e:
            detail = f'SMTP网络连接失败，请检查DNS、服务器出网、防火墙和安全组: {e}'
            print(f"[邮件] {detail}")
            return False, detail
        except ssl.SSLError as e:
            detail = f'SMTP SSL握手失败，请确认SMTP_HOST和SMTP_PORT配置正确: {e}'
            print(f"[邮件] {detail}")
            return False, detail
        except smtplib.SMTPException as e:
            detail = f'SMTP协议错误: {e}'
            print(f"[邮件] {detail}")
            return False, detail
        except Exception as e:
            detail = f'SMTP测试失败: {type(e).__name__}: {e}'
            print(f"[邮件] {detail}")
            return False, detail

    @staticmethod
    def send_email(to_email: str, subject: str, body: str) -> (bool, str):
        """通过 QQ 邮箱 SMTP 发送邮件"""
        if not Config.QQ_EMAIL or '@' not in Config.QQ_EMAIL:
            return False, 'QQ_EMAIL配置不正确，请填写完整QQ邮箱地址'
        if not Config.QQ_EMAIL_AUTH_CODE:
            return False, 'QQ_EMAIL_AUTH_CODE未配置，请填写QQ邮箱SMTP授权码，不是QQ登录密码'

        try:
            msg = MIMEText(body, 'plain', 'utf-8')
            msg['Subject'] = subject
            msg['From'] = Config.QQ_EMAIL
            msg['To'] = to_email
            with smtplib.SMTP_SSL(Config.SMTP_HOST, Config.SMTP_PORT, timeout=20) as s:
                s.login(Config.QQ_EMAIL, Config.QQ_EMAIL_AUTH_CODE)
                s.sendmail(Config.QQ_EMAIL, [to_email], msg.as_string())
            return True, ''
        except smtplib.SMTPAuthenticationError as e:
            detail = f'QQ邮箱认证失败，请检查QQ_EMAIL是否为发件QQ邮箱、QQ_EMAIL_AUTH_CODE是否为SMTP授权码且POP3/SMTP服务已开启: {e.smtp_error.decode("utf-8", "ignore") if isinstance(e.smtp_error, bytes) else e.smtp_error}'
            print(f"[邮件] {detail}")
            return False, detail
        except smtplib.SMTPSenderRefused as e:
            detail = f'发件人被SMTP服务器拒绝，请确认QQ_EMAIL与授权码属于同一个QQ邮箱: {e}'
            print(f"[邮件] {detail}")
            return False, detail
        except smtplib.SMTPRecipientsRefused as e:
            detail = f'收件邮箱被SMTP服务器拒绝，请检查收件邮箱是否有效: {e}'
            print(f"[邮件] {detail}")
            return False, detail
        except smtplib.SMTPConnectError as e:
            detail = f'SMTP连接失败，请检查服务器是否能访问{Config.SMTP_HOST}:{Config.SMTP_PORT}: {e}'
            print(f"[邮件] {detail}")
            return False, detail
        except (socket.timeout, TimeoutError):
            detail = f'SMTP连接超时，请检查云服务器安全组/防火墙是否允许访问{Config.SMTP_HOST}:{Config.SMTP_PORT}'
            print(f"[邮件] {detail}")
            return False, detail
        except (socket.gaierror, ConnectionRefusedError, OSError) as e:
            detail = f'SMTP网络连接失败，请检查DNS、服务器出网、防火墙和安全组: {e}'
            print(f"[邮件] {detail}")
            return False, detail
        except ssl.SSLError as e:
            detail = f'SMTP SSL握手失败，请确认SMTP_HOST和SMTP_PORT配置正确: {e}'
            print(f"[邮件] {detail}")
            return False, detail
        except smtplib.SMTPException as e:
            detail = f'SMTP协议错误: {e}'
            print(f"[邮件] {detail}")
            return False, detail
        except Exception as e:
            detail = f'邮件发送失败: {type(e).__name__}: {e}'
            print(f"[邮件] {detail}")
            return False, detail

    @staticmethod
    def send_verification_code(email: str, code: str) -> (bool, str):
        """发送验证码邮件。返回 (是否成功, 错误信息)。Mock 模式下只打印验证码"""
        if Config.SMTP_MOCK:
            print(f'[邮件] MOCK 模式 - 不发送真实邮件')
            print(f'[邮件] 收件人: {email}')
            print(f'[邮件] 验证码: {code}')
            return True, ''
        body = (
            f'【一饭为定】您的注册验证码是：{code}\n'
            f'有效期 10 分钟，请勿泄露给他人。\n'
            f'如非本人操作，请忽略本邮件。'
        )
        ok, error = Auth.send_email(email, '【一饭为定】邮箱验证码', body)
        return ok, error