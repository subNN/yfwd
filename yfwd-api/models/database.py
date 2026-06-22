import sqlite3
import json
import hashlib
import time
import re
import random
import string
from datetime import datetime

class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self._init_db()

    # ========== 初始化 ==========

    def _init_db(self):
        """初始化数据库表"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                conn.execute("PRAGMA encoding = 'UTF-8'")
                cursor = conn.cursor()

                # 用户表（email + password_hash 替代 openid）
                print("[数据库] 创建/迁移用户表...")
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        openid TEXT UNIQUE,
                        email TEXT UNIQUE,
                        password_hash TEXT,
                        nickname TEXT,
                        avatar_url TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login_at TIMESTAMP
                    )
                ''')
                self._migrate_database(conn, cursor)

                # 验证码表
                print("[数据库] 创建验证码表...")
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS verification_codes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT NOT NULL,
                        code_hash TEXT NOT NULL,
                        purpose TEXT NOT NULL DEFAULT 'register',
                        ip TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP NOT NULL,
                        used INTEGER DEFAULT 0
                    )
                ''')

                # IP 限流表
                print("[数据库] 创建 IP 限流表...")
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS ip_rate_limit (
                        ip TEXT NOT NULL,
                        date TEXT NOT NULL,
                        send_count INTEGER DEFAULT 0,
                        register_count INTEGER DEFAULT 0,
                        PRIMARY KEY (ip, date)
                    )
                ''')

                # 邮箱限流表
                print("[数据库] 创建邮箱限流表...")
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS email_rate_limit (
                        email TEXT NOT NULL,
                        date TEXT NOT NULL,
                        send_count INTEGER DEFAULT 0,
                        PRIMARY KEY (email, date)
                    )
                ''')

                # 登录失败记录表
                print("[数据库] 创建登录失败记录表...")
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS login_failures (
                        email TEXT NOT NULL PRIMARY KEY,
                        fail_count INTEGER DEFAULT 0,
                        lock_until REAL DEFAULT 0
                    )
                ''')

                # 人机验证表
                print("[数据库] 创建人机验证表...")
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS captcha (
                        id TEXT PRIMARY KEY,
                        answer TEXT NOT NULL,
                        question TEXT NOT NULL,
                        created_at REAL DEFAULT (julianday('now')),
                        used INTEGER DEFAULT 0
                    )
                ''')

                # 管理员表
                print("[数据库] 创建管理员表...")
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS admins (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # 菜单表
                print("[数据库] 创建菜单表...")
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS menus (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        name TEXT NOT NULL,
                        dishes TEXT NOT NULL,
                        uuid TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                ''')

                # 订单表
                print("[数据库] 创建订单表...")
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_orders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        menu_id INTEGER,
                        meal_type TEXT,
                        selected_dishes TEXT,
                        uuid TEXT,
                        order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id),
                        FOREIGN KEY (menu_id) REFERENCES menus(id)
                    )
                ''')

                # 为现有数据库迁移：添加 uuid 列并为旧记录补充 uuid
                # --- 菜单表迁移 ---
                try:
                    cursor.execute("PRAGMA table_info(menus)")
                    menu_cols = [col[1] for col in cursor.fetchall()]
                    if 'uuid' not in menu_cols:
                        # 旧数据库没有 uuid 列，添加它
                        print("[数据库] 迁移: menus 表添加 uuid 列...")
                        cursor.execute("ALTER TABLE menus ADD COLUMN uuid TEXT")
                    # 为 NULL 或空的 uuid 补充数据
                    cursor.execute("SELECT id FROM menus WHERE uuid IS NULL OR uuid = ''")
                    menu_rows = cursor.fetchall()
                    if menu_rows:
                        print(f"[数据库] 迁移: 为 {len(menu_rows)} 个菜单补充 uuid...")
                        for row in menu_rows:
                            new_uuid = self._generate_uuid('cd')
                            cursor.execute("UPDATE menus SET uuid = ? WHERE id = ?", (new_uuid, row[0]))
                except Exception as e:
                    print(f"[数据库] 菜单 uuid 迁移错误（可忽略）: {e}")

                # --- 订单表迁移 ---
                try:
                    cursor.execute("PRAGMA table_info(user_orders)")
                    order_cols = [col[1] for col in cursor.fetchall()]
                    if 'uuid' not in order_cols:
                        # 旧数据库没有 uuid 列，添加它
                        print("[数据库] 迁移: user_orders 表添加 uuid 列...")
                        cursor.execute("ALTER TABLE user_orders ADD COLUMN uuid TEXT")
                    # 为 NULL 或空的 uuid 补充数据
                    cursor.execute("SELECT id FROM user_orders WHERE uuid IS NULL OR uuid = ''")
                    order_rows = cursor.fetchall()
                    if order_rows:
                        print(f"[数据库] 迁移: 为 {len(order_rows)} 条订单补充 uuid...")
                        for row in order_rows:
                            new_uuid = self._generate_uuid('dc')
                            cursor.execute("UPDATE user_orders SET uuid = ? WHERE id = ?", (new_uuid, row[0]))
                except Exception as e:
                    print(f"[数据库] 订单 uuid 迁移错误（可忽略）: {e}")

                # 默认管理员
                cursor.execute("SELECT * FROM admins WHERE username = 'admin'")
                if not cursor.fetchone():
                    password_hash = hashlib.md5('admin123'.encode()).hexdigest()
                    cursor.execute(
                        "INSERT INTO admins (username, password_hash) VALUES (?, ?)",
                        ('admin', password_hash)
                    )

                conn.commit()
                print("[数据库] 初始化完成")
        except Exception as e:
            print(f"[数据库] 初始化错误: {e}")
            raise

    def _migrate_database(self, conn, cursor):
        """数据库迁移：添加缺失的列"""
        try:
            # --- users 表迁移 ---
            cursor.execute("PRAGMA table_info(users)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'email' not in columns:
                print("[数据库] 添加 email 列...")
                cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
            if 'password_hash' not in columns:
                print("[数据库] 添加 password_hash 列...")
                cursor.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
            if 'last_login_at' not in columns:
                print("[数据库] 添加 last_login_at 列...")
                cursor.execute("ALTER TABLE users ADD COLUMN last_login_at TIMESTAMP")
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email) WHERE email IS NOT NULL")

            # --- menus 表迁移：添加 uuid 列 ---
            try:
                cursor.execute("PRAGMA table_info(menus)")
                menu_cols = [col[1] for col in cursor.fetchall()]
                if 'uuid' not in menu_cols:
                    print("[数据库] 添加 menus.uuid 列...")
                    cursor.execute("ALTER TABLE menus ADD COLUMN uuid TEXT")
                # 补充 NULL 记录的 uuid
                cursor.execute("SELECT id FROM menus WHERE uuid IS NULL OR uuid = ''")
                menu_null_rows = cursor.fetchall()
                if menu_null_rows:
                    print(f"[数据库] 为 {len(menu_null_rows)} 个菜单补充 uuid...")
                    for row in menu_null_rows:
                        new_uuid = self._generate_uuid('cd')
                        cursor.execute("UPDATE menus SET uuid = ? WHERE id = ?", (new_uuid, row[0]))
            except Exception as e:
                print(f"[数据库] menus uuid 迁移错误（可忽略）: {e}")

            # --- user_orders 表迁移：添加 uuid 列 ---
            try:
                cursor.execute("PRAGMA table_info(user_orders)")
                order_cols = [col[1] for col in cursor.fetchall()]
                if 'uuid' not in order_cols:
                    print("[数据库] 添加 user_orders.uuid 列...")
                    cursor.execute("ALTER TABLE user_orders ADD COLUMN uuid TEXT")
                # 补充 NULL 记录的 uuid
                cursor.execute("SELECT id FROM user_orders WHERE uuid IS NULL OR uuid = ''")
                order_null_rows = cursor.fetchall()
                if order_null_rows:
                    print(f"[数据库] 为 {len(order_null_rows)} 条订单补充 uuid...")
                    for row in order_null_rows:
                        new_uuid = self._generate_uuid('dc')
                        cursor.execute("UPDATE user_orders SET uuid = ? WHERE id = ?", (new_uuid, row[0]))
            except Exception as e:
                print(f"[数据库] user_orders uuid 迁移错误（可忽略）: {e}")

            conn.commit()
        except Exception as e:
            print(f"[数据库] 迁移错误（可忽略）: {e}")

    # ========== UUID 工具方法 ==========

    def _generate_uuid(self, prefix, user_id=None):
        """生成 UUID: cd-{user_id}-yymmddhhmmssXXX（菜单）/ dc-{user_id}-yymmddhhmmssXXX（订单）
        - cd / dc: 类型前缀（菜单/点菜记录）
        - user_id: 用户 id，用于区分不同用户（可选，为兼容旧数据可省略）
        - yymmddhhmmss: 精确到秒的时间戳
        - XXX: 3 位随机字符（字母数字）
        """
        now = datetime.now()
        timestamp = now.strftime('%y%m%d%H%M%S')
        random_chars = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
        if user_id is not None:
            return f"{prefix}-{user_id}-{timestamp}{random_chars}"
        else:
            return f"{prefix}-{timestamp}{random_chars}"

    def _parse_uuid(self, uuid_str):
        """解析 UUID，返回 (prefix, user_id_or_None, timestamp_str, random_str, datetime_obj) 或 None
        支持两种格式：
        - 新格式：cd-123-yymmddhhmmssXXX （3 个以上连字符分段）
        - 旧格式：cd-yymmddhhmmssXXX （2 个连字符分段）
        """
        try:
            if not uuid_str or not isinstance(uuid_str, str) or len(uuid_str) < 18:
                return None
            parts = uuid_str.split('-')
            if len(parts) < 2:
                return None
            prefix = parts[0]
            if prefix not in ('cd', 'dc'):
                return None

            if len(parts) == 2:
                # 旧格式：cd-yymmddhhmmssXXX
                rest = parts[1]
                if len(rest) < 15:
                    return None
                timestamp_str = rest[:12]
                random_str = rest[12:]
                user_id_str = None
            else:
                # 新格式：cd-{user_id}-yymmddhhmmssXXX
                # 最后一段是时间戳+随机字符，中间的都是 user_id 部分
                last_part = parts[-1]
                user_id_parts = parts[1:-1]
                user_id_str = '-'.join(user_id_parts)
                if len(last_part) < 15:
                    return None
                timestamp_str = last_part[:12]
                random_str = last_part[12:]

            dt = datetime.strptime(timestamp_str, '%y%m%d%H%M%S')
            return (prefix, user_id_str, timestamp_str, random_str, dt)
        except Exception:
            return None

    def _extract_uuid_key(self, uuid_str):
        """从 UUID 提取匹配键：前缀+user_id+随机字符串（用于匹配相同记录）
        跨设备/同步时，相同的 (类型+用户+随机字符串) 意味着同一条记录的不同编辑版本
        """
        parsed = self._parse_uuid(uuid_str)
        if parsed is None:
            return None
        prefix, user_id_str, _, random_str, _ = parsed
        if user_id_str:
            return f"{prefix}-{user_id_str}-{random_str}"
        else:
            # 旧格式兼容
            return f"{prefix}-{random_str}"

    def _compare_uuid_timestamps(self, uuid_a, uuid_b):
        """比较两个 UUID 的时间戳，返回 1(a新) / -1(b新) / 0(相同)"""
        parsed_a = self._parse_uuid(uuid_a)
        parsed_b = self._parse_uuid(uuid_b)
        if parsed_a is None and parsed_b is None:
            return 0
        if parsed_a is None:
            return -1
        if parsed_b is None:
            return 1
        _, _, _, _, dt_a = parsed_a
        _, _, _, _, dt_b = parsed_b
        if dt_a > dt_b:
            return 1
        elif dt_a < dt_b:
            return -1
        return 0

    def _refresh_uuid_timestamp(self, old_uuid):
        """根据旧 UUID 刷新时间戳，保持前缀+user_id+随机字符串不变。
        若旧 UUID 无效，则生成全新的。
        """
        if not old_uuid:
            return self._generate_uuid('cd')
        parsed = self._parse_uuid(old_uuid)
        if parsed is None:
            return self._generate_uuid('cd')
        prefix, user_id_str, _, random_str, _ = parsed
        now = datetime.now()
        new_timestamp = now.strftime('%y%m%d%H%M%S')
        if user_id_str:
            return f"{prefix}-{user_id_str}-{new_timestamp}{random_str}"
        else:
            return f"{prefix}-{new_timestamp}{random_str}"

    # ========== 用户操作（邮箱 + 密码） ==========

    def get_user_by_email(self, email):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, openid, email, password_hash, nickname, avatar_url, created_at, last_login_at FROM users WHERE email = ?", (email.lower(),))
                return cursor.fetchone()
        except Exception as e:
            print(f"[数据库] get_user_by_email 错误: {e}")
            return None

    def get_user_by_id(self, user_id):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, openid, email, password_hash, nickname, avatar_url, created_at, last_login_at FROM users WHERE id = ?", (user_id,))
                return cursor.fetchone()
        except Exception as e:
            print(f"[数据库] get_user_by_id 错误: {e}")
            return None

    def register_user(self, email, password_hash, nickname=None):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                email = email.lower()
                nick = (nickname or '').strip() or email.split('@')[0]
                now = datetime.now().isoformat()
                cursor.execute(
                    "INSERT INTO users (openid, email, password_hash, nickname, created_at, last_login_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (f'email:{email}', email, password_hash, nick[:20], now, now)
                )
                conn.commit()
                user_id = cursor.lastrowid
                print(f"[数据库] 注册用户: id={user_id}, email={email}, nickname={nick[:20]}")
                return user_id
        except sqlite3.IntegrityError:
            return None  # 邮箱重复
        except Exception as e:
            print(f"[数据库] register_user 错误: {e}")
            raise

    def update_user_login(self, user_id):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET last_login_at = ? WHERE id = ?",
                    (datetime.now().isoformat(), user_id)
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"[数据库] update_user_login 错误: {e}")
            return False

    def update_user_nickname(self, user_id, nickname):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                new_nick = (nickname or '').strip()
                if not new_nick:
                    return False
                cursor.execute(
                    "UPDATE users SET nickname = ? WHERE id = ?",
                    (new_nick, user_id)
                )
                conn.commit()
                if cursor.rowcount > 0:
                    print(f"[数据库] 更新昵称: user_id={user_id}, nickname={new_nick[:20]}")
                    return True
                return False
        except Exception as e:
            print(f"[数据库] update_user_nickname 错误: {e}")
            return False

    def update_user_password(self, user_id, password_hash):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                if not password_hash:
                    return False
                cursor.execute(
                    "UPDATE users SET password_hash = ? WHERE id = ?",
                    (password_hash, user_id)
                )
                conn.commit()
                if cursor.rowcount > 0:
                    print(f"[数据库] 更新密码: user_id={user_id}")
                    return True
                return False
        except Exception as e:
            print(f"[数据库] update_user_password 错误: {e}")
            return False

    def user_to_dict(self, row):
        """将数据库行转为字典"""
        if not row:
            return None
        return {
            'id': row[0],
            'openid': row[1] if len(row) > 1 else '',
            'email': row[2] if len(row) > 2 else '',
            'nickname': row[4] if len(row) > 4 else '',
            'avatar_url': row[5] if len(row) > 5 else None,
            'created_at': row[6] if len(row) > 6 else '',
            'last_login_at': row[7] if len(row) > 7 else '',
        }

    def get_all_users(self):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, openid, email, password_hash, nickname, avatar_url, created_at, last_login_at FROM users ORDER BY created_at DESC"
                )
                users = []
                for row in cursor.fetchall():
                    users.append({
                        'id': row[0],
                        'openid': row[1] if len(row) > 1 else '',
                        'email': row[2] if len(row) > 2 else '',
                        'nickname': row[4] if len(row) > 4 else '',
                        'avatar_url': row[5] if len(row) > 5 else None,
                        'created_at': row[6] if len(row) > 6 else '',
                        'last_login_at': row[7] if len(row) > 7 else '',
                    })
                return users
        except Exception as e:
            print(f"[数据库] get_all_users 错误: {e}")
            return []

    def delete_user(self, user_id):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM user_orders WHERE user_id = ?", (user_id,))
                cursor.execute("DELETE FROM menus WHERE user_id = ?", (user_id,))
                cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"[数据库] delete_user 错误: {e}")
            return False

    # ========== 验证码 ==========

    def save_verification_code(self, email, code_hash, purpose, ip, expires_at):
        """保存验证码（覆盖旧码）"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                # 先删掉该邮箱旧未使用的 code
                cursor.execute(
                    "DELETE FROM verification_codes WHERE email = ? AND purpose = ? AND used = 0",
                    (email, purpose)
                )
                cursor.execute(
                    "INSERT INTO verification_codes (email, code_hash, purpose, ip, expires_at) VALUES (?, ?, ?, ?, ?)",
                    (email, code_hash, purpose, ip, expires_at)
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"[数据库] save_verification_code 错误: {e}")
            return False

    def get_verification_code(self, email, purpose='register'):
        """获取未过期未使用的验证码"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM verification_codes WHERE email = ? AND purpose = ? AND used = 0 AND expires_at > ? ORDER BY created_at DESC LIMIT 1",
                    (email, purpose, time.time())
                )
                return cursor.fetchone()
        except Exception as e:
            print(f"[数据库] get_verification_code 错误: {e}")
            return None

    def mark_code_used(self, code_id):
        """标记验证码已使用"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE verification_codes SET used = 1 WHERE id = ?", (code_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"[数据库] mark_code_used 错误: {e}")
            return False

    def get_last_code_send_time(self, email):
        """获取该邮箱最后一次发码时间（用于重发冷却）"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT created_at FROM verification_codes WHERE email = ? ORDER BY created_at DESC LIMIT 1",
                    (email,)
                )
                row = cursor.fetchone()
                if row:
                    return row[0]
                return None
        except Exception as e:
            print(f"[数据库] get_last_code_send_time 错误: {e}")
            return None

    # ========== IP 限流 ==========

    def _today(self):
        return datetime.now().strftime('%Y-%m-%d')

    def get_ip_rate_limit(self, ip, action):
        """获取 IP 当天某操作的次数"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT send_count, register_count FROM ip_rate_limit WHERE ip = ? AND date = ?",
                    (ip, self._today())
                )
                row = cursor.fetchone()
                if not row:
                    return 0
                return row[0] if action == 'send' else row[1]
        except Exception as e:
            print(f"[数据库] get_ip_rate_limit 错误: {e}")
            return 0

    def incr_ip_rate_limit(self, ip, action):
        """增加 IP 当天某操作的次数"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                today = self._today()
                cursor.execute("SELECT * FROM ip_rate_limit WHERE ip = ? AND date = ?", (ip, today))
                if cursor.fetchone():
                    if action == 'send':
                        cursor.execute("UPDATE ip_rate_limit SET send_count = send_count + 1 WHERE ip = ? AND date = ?", (ip, today))
                    else:
                        cursor.execute("UPDATE ip_rate_limit SET register_count = register_count + 1 WHERE ip = ? AND date = ?", (ip, today))
                else:
                    if action == 'send':
                        cursor.execute("INSERT INTO ip_rate_limit (ip, date, send_count, register_count) VALUES (?, ?, 1, 0)", (ip, today))
                    else:
                        cursor.execute("INSERT INTO ip_rate_limit (ip, date, send_count, register_count) VALUES (?, ?, 0, 1)", (ip, today))
                conn.commit()
                return True
        except Exception as e:
            print(f"[数据库] incr_ip_rate_limit 错误: {e}")
            return False

    def get_email_send_count(self, email):
        """获取邮箱当天发送次数"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT send_count FROM email_rate_limit WHERE email = ? AND date = ?",
                    (email, self._today())
                )
                row = cursor.fetchone()
                return row[0] if row else 0
        except Exception as e:
            print(f"[数据库] get_email_send_count 错误: {e}")
            return 0

    def incr_email_send_count(self, email):
        """增加邮箱当天发送次数"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                today = self._today()
                cursor.execute("SELECT * FROM email_rate_limit WHERE email = ? AND date = ?", (email, today))
                if cursor.fetchone():
                    cursor.execute("UPDATE email_rate_limit SET send_count = send_count + 1 WHERE email = ? AND date = ?", (email, today))
                else:
                    cursor.execute("INSERT INTO email_rate_limit (email, date, send_count) VALUES (?, ?, 1)", (email, today))
                conn.commit()
                return True
        except Exception as e:
            print(f"[数据库] incr_email_send_count 错误: {e}")
            return False

    # ========== 登录失败记录 ==========

    def get_login_failures(self, email):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT fail_count, lock_until FROM login_failures WHERE email = ?", (email,))
                return cursor.fetchone()
        except Exception as e:
            print(f"[数据库] get_login_failures 错误: {e}")
            return None

    def incr_login_failure(self, email, max_fail=5, lock_sec=300):
        """增加失败次数，达到上限时锁定"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM login_failures WHERE email = ?", (email,))
                row = cursor.fetchone()
                if row:
                    new_count = row[1] + 1
                    if new_count >= max_fail:
                        lock_until = time.time() + lock_sec
                        cursor.execute(
                            "UPDATE login_failures SET fail_count = ?, lock_until = ? WHERE email = ?",
                            (0, lock_until, email)
                        )
                    else:
                        cursor.execute("UPDATE login_failures SET fail_count = ? WHERE email = ?", (new_count, email))
                else:
                    cursor.execute("INSERT INTO login_failures (email, fail_count, lock_until) VALUES (?, 1, 0)", (email,))
                conn.commit()
                return True
        except Exception as e:
            print(f"[数据库] incr_login_failure 错误: {e}")
            return False

    def reset_login_failures(self, email):
        """登录成功后重置失败次数"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM login_failures WHERE email = ?", (email,))
                conn.commit()
                return True
        except Exception as e:
            print(f"[数据库] reset_login_failures 错误: {e}")
            return False

    # ========== 人机验证 ==========

    def save_captcha(self, captcha_id, answer, question):
        """保存验证问答"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                # 清理过期
                cursor.execute(
                    "DELETE FROM captcha WHERE (julianday('now') - created_at) * 86400 > ?",
                    (300,)
                )
                cursor.execute(
                    "INSERT INTO captcha (id, answer, question) VALUES (?, ?, ?)",
                    (captcha_id, answer, question)
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"[数据库] save_captcha 错误: {e}")
            return False

    def verify_captcha(self, captcha_id, user_answer, mark_used=True):
        """验证验证问答。mark_used=True 时通过后标记已用，mark_used=False 时只检查不消耗"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT answer, used, (julianday('now') - created_at) * 86400 FROM captcha WHERE id = ?",
                    (captcha_id,)
                )
                row = cursor.fetchone()
                if not row:
                    return False, '验证已过期，请刷新'
                answer, used, elapsed = row
                if used:
                    return False, '验证已使用'
                if elapsed > 300:
                    return False, '验证已过期，请刷新'
                if user_answer.strip() != answer:
                    return False, '答案错误'
                if mark_used:
                    cursor.execute("UPDATE captcha SET used = 1 WHERE id = ?", (captcha_id,))
                    conn.commit()
                return True, ''
        except Exception as e:
            print(f"[数据库] verify_captcha 错误: {e}")
            return False, f'验证失败: {e}'

    # ========== 菜单操作 ==========

    def add_menu(self, user_id, name, dishes, uuid=None):
        """新建菜单。若提供 uuid（带 cd- 前缀）则使用，否则自动生成（含用户标识）。"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                if not isinstance(dishes, list):
                    dishes = []
                dishes_json = json.dumps(dishes, ensure_ascii=False)
                if uuid and self._parse_uuid(uuid) is not None and uuid.startswith('cd-'):
                    menu_uuid = uuid
                else:
                    menu_uuid = self._generate_uuid('cd', user_id)
                cursor.execute(
                    "INSERT INTO menus (user_id, name, dishes, uuid, updated_at, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (user_id, name, dishes_json, menu_uuid, datetime.now().isoformat(), datetime.now().isoformat())
                )
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"[数据库] add_menu 错误: {e}")
            raise

    def update_menu(self, menu_id, name, dishes):
        """更新菜单内容，UUID 保持不变，仅更新内容和 updated_at"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                if not isinstance(dishes, list):
                    dishes = []
                dishes_json = json.dumps(dishes, ensure_ascii=False)
                cursor.execute(
                    "UPDATE menus SET name = ?, dishes = ?, updated_at = ? WHERE id = ?",
                    (name, dishes_json, datetime.now().isoformat(), menu_id)
                )
                conn.commit()
                return menu_id
        except Exception as e:
            print(f"[数据库] update_menu 错误: {e}")
            raise

    def get_menu_by_uuid(self, uuid_str, user_id=None):
        """根据 uuid 查询菜单。用于导入时检测是否存在相同记录。"""
        try:
            if not uuid_str:
                return None
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                if user_id:
                    cursor.execute("SELECT * FROM menus WHERE uuid = ? AND user_id = ?", (uuid_str, user_id))
                else:
                    cursor.execute("SELECT * FROM menus WHERE uuid = ?", (uuid_str,))
                row = cursor.fetchone()
                if not row:
                    return None
                try:
                    dishes = json.loads(row[3]) if row[3] else []
                except Exception:
                    dishes = []
                return {
                    'id': row[0], 'user_id': row[1], 'name': row[2],
                    'dishes': dishes, 'uuid': row[4] if len(row) > 4 else None,
                    'created_at': row[5] if len(row) > 5 else None,
                    'updated_at': row[6] if len(row) > 6 else None
                }
        except Exception as e:
            print(f"[数据库] get_menu_by_uuid 错误: {e}")
            return None

    def _update_menu_by_uuid_match(self, uuid_str, user_id, name, dishes):
        """基于 uuid 精确匹配更新菜单。UUID 完全匹配到就更新内容，UUID 保持不变。"""
        try:
            if not uuid_str:
                return None
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM menus WHERE user_id = ? AND uuid = ?", (user_id, uuid_str))
                row = cursor.fetchone()
                if not row:
                    return None
                if not isinstance(dishes, list):
                    dishes = []
                dishes_json = json.dumps(dishes, ensure_ascii=False)
                rid = row[0]
                cursor.execute(
                    "UPDATE menus SET name = ?, dishes = ?, updated_at = ? WHERE id = ?",
                    (name, dishes_json, datetime.now().isoformat(), rid)
                )
                conn.commit()
                return rid
        except Exception as e:
            print(f"[数据库] _update_menu_by_uuid_match 错误: {e}")
            return None

    def get_user_menus(self, user_id):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(menus)")
                cols = [col[1] for col in cursor.fetchall()]
                has_uuid = 'uuid' in cols

                if has_uuid:
                    cursor.execute("SELECT id, user_id, name, dishes, uuid, created_at, updated_at FROM menus WHERE user_id = ? ORDER BY updated_at DESC", (user_id,))
                else:
                    cursor.execute("SELECT id, user_id, name, dishes, created_at, updated_at FROM menus WHERE user_id = ? ORDER BY updated_at DESC", (user_id,))
                menus = []
                for row in cursor.fetchall():
                    try:
                        dishes = json.loads(row[3]) if row[3] else []
                    except Exception:
                        dishes = []
                    if has_uuid:
                        menu = {
                            'id': row[0],
                            'user_id': row[1],
                            'name': row[2],
                            'dishes': dishes,
                            'uuid': row[4],
                            'created_at': row[5],
                            'updated_at': row[6]
                        }
                    else:
                        menu = {
                            'id': row[0],
                            'user_id': row[1],
                            'name': row[2],
                            'dishes': dishes,
                            'uuid': None,
                            'created_at': row[4],
                            'updated_at': row[5]
                        }
                    menus.append(menu)
                return menus
        except Exception as e:
            print(f"[数据库] get_user_menus 错误: {e}")
            return []

    def get_menu_by_id(self, menu_id, user_id=None):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(menus)")
                cols = [col[1] for col in cursor.fetchall()]
                has_uuid = 'uuid' in cols

                # 明确指定列顺序，避免受 ALTER TABLE 列顺序影响
                if has_uuid:
                    if user_id:
                        cursor.execute("SELECT id, user_id, name, dishes, uuid, created_at, updated_at FROM menus WHERE id = ? AND user_id = ?", (menu_id, user_id))
                    else:
                        cursor.execute("SELECT id, user_id, name, dishes, uuid, created_at, updated_at FROM menus WHERE id = ?", (menu_id,))
                else:
                    if user_id:
                        cursor.execute("SELECT id, user_id, name, dishes, created_at, updated_at FROM menus WHERE id = ? AND user_id = ?", (menu_id, user_id))
                    else:
                        cursor.execute("SELECT id, user_id, name, dishes, created_at, updated_at FROM menus WHERE id = ?", (menu_id,))
                row = cursor.fetchone()
                if not row:
                    return None
                try:
                    dishes = json.loads(row[3]) if row[3] else []
                except Exception:
                    dishes = []
                if has_uuid:
                    return {
                        'id': row[0], 'user_id': row[1], 'name': row[2],
                        'dishes': dishes, 'uuid': row[4],
                        'created_at': row[5],
                        'updated_at': row[6]
                    }
                return {
                    'id': row[0], 'user_id': row[1], 'name': row[2],
                    'dishes': dishes, 'uuid': None,
                    'created_at': row[4], 'updated_at': row[5]
                }
        except Exception as e:
            print(f"[数据库] get_menu_by_id 错误: {e}")
            return None

    def get_all_menus(self):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(menus)")
                cols = [col[1] for col in cursor.fetchall()]
                has_uuid = 'uuid' in cols

                # 明确指定列顺序，避免受 ALTER TABLE 列顺序影响
                if has_uuid:
                    cursor.execute("SELECT id, user_id, name, dishes, uuid, created_at, updated_at FROM menus ORDER BY updated_at DESC")
                else:
                    cursor.execute("SELECT id, user_id, name, dishes, created_at, updated_at FROM menus ORDER BY updated_at DESC")
                menus = []
                for row in cursor.fetchall():
                    try:
                        dishes = json.loads(row[3]) if row[3] else []
                    except Exception:
                        dishes = []
                    if has_uuid:
                        menus.append({
                            'id': row[0], 'user_id': row[1], 'name': row[2],
                            'dishes': dishes, 'uuid': row[4],
                            'created_at': row[5], 'updated_at': row[6]
                        })
                    else:
                        menus.append({
                            'id': row[0], 'user_id': row[1], 'name': row[2],
                            'dishes': dishes, 'uuid': None,
                            'created_at': row[4], 'updated_at': row[5]
                        })
                return menus
        except Exception as e:
            print(f"[数据库] get_all_menus 错误: {e}")
            return []

    def delete_menu(self, menu_id):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM menus WHERE id = ?", (menu_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"[数据库] delete_menu 错误: {e}")
            return False

    # ========== 订单操作 ==========

    def add_order(self, user_id, menu_id, meal_type, selected_dishes, order_time=None, uuid=None):
        """新建订单。若提供 uuid（带 dc- 前缀）则使用，否则自动生成（含用户标识）。"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                if not isinstance(selected_dishes, list):
                    selected_dishes = []
                dishes_json = json.dumps(selected_dishes, ensure_ascii=False)
                if uuid and self._parse_uuid(uuid) is not None and uuid.startswith('dc-'):
                    order_uuid = uuid
                else:
                    order_uuid = self._generate_uuid('dc', user_id)
                actual_time = order_time if order_time else datetime.now().isoformat()
                cursor.execute(
                    "INSERT INTO user_orders (user_id, menu_id, meal_type, selected_dishes, uuid, order_time) VALUES (?, ?, ?, ?, ?, ?)",
                    (user_id, menu_id, meal_type, dishes_json, order_uuid, actual_time)
                )
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"[数据库] add_order 错误: {e}")
            raise

    def _update_order_by_uuid_match(self, uuid_str, user_id, meal_type, selected_dishes, order_time=None):
        """基于 uuid 匹配更新订单。找到相同 uuid（前缀+随机串相同）则更新内容和 uuid 时间戳。"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, uuid FROM user_orders WHERE user_id = ? AND uuid IS NOT NULL", (user_id,))
                rows = cursor.fetchall()
                input_key = self._extract_uuid_key(uuid_str)
                if not input_key:
                    return None
                for row in rows:
                    rid, existing_uuid = row
                    existing_key = self._extract_uuid_key(existing_uuid)
                    if existing_key == input_key:
                        cmp = self._compare_uuid_timestamps(uuid_str, existing_uuid)
                        if cmp >= 0:
                            if not isinstance(selected_dishes, list):
                                selected_dishes = []
                            dishes_json = json.dumps(selected_dishes, ensure_ascii=False)
                            new_uuid = self._refresh_uuid_timestamp(uuid_str)
                            actual_time = order_time if order_time else datetime.now().isoformat()
                            cursor.execute(
                                "UPDATE user_orders SET meal_type = ?, selected_dishes = ?, uuid = ?, order_time = ? WHERE id = ?",
                                (meal_type, dishes_json, new_uuid, actual_time, rid)
                            )
                            conn.commit()
                            return rid
                        else:
                            return -1  # 云端数据更新，跳过
                return None
        except Exception as e:
            print(f"[数据库] _update_order_by_uuid_match 错误: {e}")
            return None

    def get_user_orders(self, user_id):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(user_orders)")
                cols = [col[1] for col in cursor.fetchall()]
                has_uuid = 'uuid' in cols

                if has_uuid:
                    cursor.execute("SELECT uo.id, uo.user_id, uo.menu_id, uo.meal_type, uo.selected_dishes, uo.uuid, uo.order_time FROM user_orders uo WHERE user_id = ? ORDER BY uo.order_time DESC", (user_id,))
                else:
                    cursor.execute("SELECT id, user_id, menu_id, meal_type, selected_dishes, order_time FROM user_orders WHERE user_id = ? ORDER BY order_time DESC", (user_id,))
                orders = []
                for row in cursor.fetchall():
                    try:
                        dishes_col = row[4] if has_uuid else row[4]
                        selected_dishes = json.loads(dishes_col) if dishes_col else []
                    except Exception:
                        selected_dishes = []
                    if not isinstance(selected_dishes, list):
                        selected_dishes = []

                    total_amount = 0.0
                    for d in selected_dishes:
                        price = float(d.get('price') or 0)
                        qty = int(d.get('quantity') or 0)
                        total_amount += price * qty

                    menu_id = row[2]
                    menu_name = None
                    if menu_id:
                        try:
                            cursor.execute("SELECT name FROM menus WHERE id = ?", (menu_id,))
                            mr = cursor.fetchone()
                            if mr:
                                menu_name = mr[0]
                        except Exception:
                            pass

                    if has_uuid:
                        orders.append({
                            'id': row[0],
                            'user_id': row[1],
                            'menu_id': menu_id,
                            'menu_name': menu_name,
                            'meal_type': row[3],
                            'dishes': selected_dishes,
                            'selected_dishes': selected_dishes,
                            'uuid': row[5],
                            'order_time': row[6],
                            'total_amount': round(total_amount, 2)
                        })
                    else:
                        orders.append({
                            'id': row[0],
                            'user_id': row[1],
                            'menu_id': menu_id,
                            'menu_name': menu_name,
                            'meal_type': row[3],
                            'dishes': selected_dishes,
                            'selected_dishes': selected_dishes,
                            'uuid': None,
                            'order_time': row[5],
                            'total_amount': round(total_amount, 2)
                        })
                return orders
        except Exception as e:
            print(f"[数据库] get_user_orders 错误: {e}")
            return []

    def get_all_orders(self):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(user_orders)")
                cols = [col[1] for col in cursor.fetchall()]
                has_uuid = 'uuid' in cols

                if has_uuid:
                    cursor.execute('''
                        SELECT uo.id, uo.user_id, uo.menu_id, uo.meal_type, uo.selected_dishes, uo.uuid, uo.order_time, u.nickname, u.avatar_url
                        FROM user_orders uo
                        LEFT JOIN users u ON uo.user_id = u.id
                        ORDER BY uo.order_time DESC
                    ''')
                else:
                    cursor.execute('''
                        SELECT uo.id, uo.user_id, uo.menu_id, uo.meal_type, uo.selected_dishes, uo.order_time, u.nickname, u.avatar_url
                        FROM user_orders uo
                        LEFT JOIN users u ON uo.user_id = u.id
                        ORDER BY uo.order_time DESC
                    ''')
                orders = []
                for row in cursor.fetchall():
                    try:
                        dishes_str = row[4] if row[4] else ''
                        selected_dishes = json.loads(dishes_str) if dishes_str else []
                        if not isinstance(selected_dishes, list):
                            selected_dishes = []
                    except Exception:
                        selected_dishes = self._parse_dishes_string(dishes_str)
                    if has_uuid:
                        orders.append({
                            'id': row[0], 'user_id': row[1], 'menu_id': row[2],
                            'meal_type': row[3], 'selected_dishes': selected_dishes,
                            'uuid': row[5],
                            'order_time': row[6],
                            'nickname': row[7] if len(row) > 7 else None,
                            'avatar_url': row[8] if len(row) > 8 else None,
                        })
                    else:
                        orders.append({
                            'id': row[0], 'user_id': row[1], 'menu_id': row[2],
                            'meal_type': row[3], 'selected_dishes': selected_dishes,
                            'uuid': None,
                            'order_time': row[5],
                            'nickname': row[6] if len(row) > 6 else None,
                            'avatar_url': row[7] if len(row) > 7 else None,
                        })
                return orders
        except Exception as e:
            print(f"[数据库] get_all_orders 错误: {e}")
            return []

    def _parse_dishes_string(self, dishes_str):
        try:
            dishes = []
            cleaned = dishes_str.strip()
            if not cleaned:
                return []
            if '、' in cleaned:
                items = cleaned.split('、')
            elif ',' in cleaned:
                items = cleaned.split(',')
            else:
                items = [cleaned]
            for item in items:
                item = item.strip()
                if item:
                    dishes.append({'name': item, 'price': 0, 'quantity': 1})
            return dishes
        except Exception:
            return [{'name': dishes_str, 'price': 0, 'quantity': 1}]

    def is_order_duplicate(self, user_id, meal_type, selected_dishes):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                if not isinstance(selected_dishes, list):
                    selected_dishes = []
                dishes_json = json.dumps(selected_dishes, ensure_ascii=False)
                cursor.execute(
                    "SELECT * FROM user_orders WHERE user_id = ? AND meal_type = ? AND selected_dishes = ?",
                    (user_id, meal_type, dishes_json)
                )
                return cursor.fetchone() is not None
        except Exception as e:
            print(f"[数据库] is_order_duplicate 错误: {e}")
            return False

    def delete_order(self, order_id, user_id=None):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                if user_id is None:
                    cursor.execute("DELETE FROM user_orders WHERE id = ?", (order_id,))
                else:
                    cursor.execute("DELETE FROM user_orders WHERE id = ? AND user_id = ?", (order_id, user_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"[数据库] delete_order 错误: {e}")
            return False

    def get_stats(self):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM users")
                user_count = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM menus")
                menu_count = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM user_orders")
                order_count = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM user_orders WHERE date(order_time) = date('now', 'localtime')")
                today_order_count = cursor.fetchone()[0]
                return {
                    'user_count': user_count,
                    'menu_count': menu_count,
                    'order_count': order_count,
                    'today_order_count': today_order_count,
                }
        except Exception as e:
            print(f"[数据库] get_stats 错误: {e}")
            return {
                'user_count': 0,
                'menu_count': 0,
                'order_count': 0,
                'today_order_count': 0,
            }

    # ========== 管理员 ==========

    def verify_admin(self, username, password):
        """验证管理员凭据"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM admins WHERE username = ?", (username,))
                row = cursor.fetchone()
                if not row:
                    return False
                stored_hash = row[2]
                return stored_hash == hashlib.md5(password.encode()).hexdigest()
        except Exception as e:
            print(f"[数据库] verify_admin 错误: {e}")
            return False