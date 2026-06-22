<p align="center">
  <img src="./一饭为定.jpg" alt="一饭为定" width="500" />
</p>

<h1 align="center">一饭为定</h1>

<p align="center">
  <strong>智能菜单管理 · AI 饮食助手</strong>
</p>

<p align="center">
  <a href="http://8.156.73.125/" target="_blank">🌐 在线访问</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Flask-3.x-000000?style=flat&logo=flask&logoColor=white" alt="Flask" />
  <img src="https://img.shields.io/badge/Vue-3.x-4FC08D?style=flat&logo=vue.js&logoColor=white" alt="Vue" />
  <img src="https://img.shields.io/badge/Database-SQLite-003B57?style=flat&logo=sqlite&logoColor=white" alt="SQLite" />
  <img src="https://img.shields.io/badge/AI-OpenAI_Compatible-412991?style=flat&logo=openai&logoColor=white" alt="AI" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat" alt="License" />
</p>

---

## 📖 项目简介

**一饭为定**是一个集菜单管理、点菜记录与 AI 饮食辅助于一体的 Web 应用，帮助你告别"今天吃什么"的烦恼。

> 🏠 **在线地址**：[http://8.156.73.125/](http://8.156.73.125/)

### 项目组成

| 模块 | 路径 | 技术栈 | 说明 |
|------|------|--------|------|
| 🖥️ 前端 | `d:\yfwd\yfwd-web` | Vue 3 + Vue Router | 静态单页应用 |
| ⚙️ 后端 | `d:\yfwd\yfwd-api` | Flask + SQLite | REST API 服务 |

---

## 🎯 核心功能

### 👤 用户端

| 功能 | 说明 |
|------|------|
| 🔐 邮箱注册/登录 | QQ SMTP 发送验证码，JWT 登录态保持 |
| 🧩 人机验证 | 柱状图排序验证码，防止接口被刷 |
| 👤 个人资料 | 查看与修改昵称 |
| 📋 菜单管理 | 创建、查看、编辑、删除个人菜单 |
| 🍽️ 点菜记录 | 创建、查看、删除点菜记录 |
| 📊 首页统计 | 菜单数、点菜记录数、常用操作入口 |
| 📦 数据管理 | JSON 导入/导出/上传/下载 |
| 🤖 AI 助手 | 生成菜单、推荐菜品、自由对话 |

> **AI 行为说明**：AI 生成菜单后**不会自动保存**，需用户点击「保存」按钮确认后才写入数据库。

### 🛡️ 后台管理

| 功能 | 说明 |
|------|------|
| 🔑 管理员登录 | 独立的管理后台 |
| 👥 用户管理 | 查看、删除用户 |
| 📋 菜单管理 | 查看、删除任意菜单 |
| 🍽️ 订单管理 | 查看、删除任意点菜记录 |
| 📈 数据统计 | 用户数、菜单数、订单数、今日订单数 |

### 🔄 数据同步

| 功能 | 接口 |
|------|------|
| 导出菜单 | `GET /api/user/menus/export` |
| 导入菜单 | `POST /api/user/menus/import` |
| 导出记录 | `GET /api/user/orders/export` |
| 导入记录 | `POST /api/user/orders/import` |

- 支持多种 JSON 包装格式（数组、`menus`、`orders`、`data`、`items` 等）
- 菜单 UUID：`cd-yymmddhhmmssXXXXXX`
- 点菜记录 UUID：`dc-yymmddhhmmssXXXXXX`
- 编辑后 UUID 不变，导入时按 UUID 匹配 + 时间戳比较策略合并

---

## 📁 项目目录

```text
d:\yfwd
├── 📂 yfwd-web/               # 前端静态站点
│   ├── index.html              # 应用入口
│   ├── login.html              # 登录页
│   ├── register.html           # 注册页
│   ├── reset-password.html     # 重置密码页
│   ├── app.js                  # Vue Router 与主布局
│   ├── components.js           # 主要业务组件
│   ├── store.js                # API 地址、登录态、本地状态
│   ├── auth.js                 # 登录/注册页交互组件
│   ├── style.css               # 主样式
│   ├── auth.css                # 认证页样式
│   ├── privacy.html            # 隐私政策
│   ├── terms.html              # 服务条款
│   ├── 一饭为定.jpg            # 项目图标
│   └── API.md                  # API 接口文档
│
└── 📂 yfwd-api/                # Flask 后端服务
    ├── app.py                  # Flask 应用工厂与蓝图注册
    ├── config.py               # 配置与环境变量读取
    ├── models/
    │   └── database.py         # SQLite 表结构、迁移、数据访问
    ├── routes/
    │   ├── auth.py             # 注册、登录、验证码、人机验证、重置密码
    │   ├── user.py             # 用户菜单、点菜记录、导入导出
    │   ├── ai.py               # AI 对话、生成菜单、推荐菜品
    │   ├── admin.py            # 管理员登录、用户/菜单/订单管理
    │   ├── upload.py           # 兼容旧版上传接口
    │   └── static.py           # 后端静态管理页路由
    ├── utils/
    │   ├── auth.py             # JWT、密码哈希、邮箱验证码工具
    │   ├── decorators.py       # 登录与管理员鉴权装饰器
    │   └── ai_client.py        # OpenAI 兼容接口客户端
    ├── static/
    │   └── index.html          # 后端管理控制台页面
    ├── requirements.txt        # Python 依赖
    ├── gunicorn_conf.py        # Gunicorn 配置
    ├── wsgi.py                 # WSGI 入口
    ├── dining.db               # 默认 SQLite 数据库文件
    ├── README.md               # 项目说明
    └── LICENSE                 # 开源许可证
```

---

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| 🖥️ 前端 | Vue 3、Vue Router (Hash)、原生 ES Modules、Tailwind 风格布局 |
| ⚙️ 后端 | Python 3、Flask 3、Flask-CORS、SQLite |
| 🔐 认证 | PyJWT (HS256)、邮箱验证码 (QQ SMTP)、人机验证 |
| 🤖 AI | OpenAI 兼容 Chat Completions 格式 |
| 📦 部署 | Gunicorn / uWSGI、Nginx 反向代理 |

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- pip
- 可选：Gunicorn / uWSGI（生产部署）
- 可选：OpenAI 兼容 API Key
- 可选：QQ 邮箱 SMTP 授权码

### 1. 启动后端

```powershell
cd d:\yfwd\yfwd-api

# 创建虚拟环境
python -m venv venv
.\venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt

# 启动开发服务
python app.py
```

### 2. 部署前端

前端为纯静态项目，直接部署到任意静态站点目录。

---

## ⚙️ 环境变量

在 `yfwd-api/.env` 中配置：

```env
# Flask 基础
SECRET_KEY=change-me
FLASK_DEBUG=0
HOST=your-host
PORT=your-port
CORS_ORIGINS=*

# JWT
JWT_SECRET_KEY=change-me-too

# 数据库
DATABASE=d:\yfwd\yfwd-api\yourdatabase.db

# QQ SMTP 邮箱
QQ_EMAIL=your@qq.com
QQ_EMAIL_AUTH_CODE=your_qq_mail_auth_code
SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_MOCK=0

# AI 服务（OpenAI 兼容格式）
AI_ENABLED=1
AI_API_URL=https://api.openai.com/v1
AI_API_KEY=sk-your-api-key-here
AI_MODEL=gpt-3.5-turbo
AI_MAX_TOKENS=2000
AI_TEMPERATURE=0.7
```

> 💡 `SMTP_MOCK=1` 时验证码不会真实发送，接口返回 `mock_code`，适合本地调试。

---

## 📡 API 概览

### 认证与用户

| 方法 | 路径 | 鉴权 | 说明 |
|------|------|------|------|
| GET | `/api/auth/captcha` | — | 获取柱状图排序人机验证 |
| POST | `/api/auth/verify-captcha` | — | 仅校验人机验证 |
| POST | `/api/auth/send-code` | — | 发送邮箱验证码 |
| POST | `/api/auth/register` | — | 注册 |
| POST | `/api/auth/login` | — | 登录 |
| GET | `/api/auth/me` | JWT | 获取当前用户信息 |
| POST | `/api/auth/logout` | JWT | 退出登录 |
| PUT | `/api/auth/profile` | JWT | 修改昵称 |
| POST | `/api/auth/forgot-password` | — | 检查找回密码账号 |
| POST | `/api/auth/reset-password` | — | 重置密码 |
| GET | `/api/auth/smtp-check` | — | 检查 SMTP 配置 |
| GET | `/api/health` | — | 健康检查 |

### 用户菜单

| 方法 | 路径 | 鉴权 | 说明 |
|------|------|------|------|
| GET | `/api/user/info` | JWT | 获取当前用户信息 |
| GET | `/api/user/menus` | JWT | 获取用户菜单列表 |
| POST | `/api/user/menus` | JWT | 创建菜单 |
| GET | `/api/user/menus/<id>` | JWT | 获取菜单详情 |
| PUT | `/api/user/menus/<id>` | JWT | 更新菜单 |
| DELETE | `/api/user/menus/<id>` | JWT | 删除菜单 |
| GET | `/api/user/menus/export` | JWT | 导出菜单 JSON |
| POST | `/api/user/menus/import` | JWT | 导入菜单 JSON |

### 点菜记录

| 方法 | 路径 | 鉴权 | 说明 |
|------|------|------|------|
| GET | `/api/user/orders` | JWT | 获取点菜记录列表 |
| POST | `/api/user/orders` | JWT | 创建点菜记录 |
| DELETE | `/api/user/orders/<id>` | JWT | 删除点菜记录 |
| GET | `/api/user/orders/export` | JWT | 导出点菜记录 JSON |
| POST | `/api/user/orders/import` | JWT | 导入点菜记录 JSON |

### AI

| 方法 | 路径 | 鉴权 | 说明 |
|------|------|------|------|
| GET | `/api/ai/status` | — | 查看 AI 是否启用 |
| POST | `/api/ai/chat` | JWT | AI 自由对话 |
| POST | `/api/ai/create-menu` | JWT | 根据描述生成菜单，默认不保存 |
| POST | `/api/ai/recommend` | JWT | 根据偏好推荐菜品 |

### 管理员

| 方法 | 路径 | 鉴权 | 说明 |
|------|------|------|------|
| POST | `/api/admin/login` | — | 管理员登录 |
| GET | `/api/admin/users` | Admin | 获取用户列表 |
| DELETE | `/api/admin/users/<id>` | Admin | 删除用户 |
| GET | `/api/admin/menus` | Admin | 获取所有菜单 |
| DELETE | `/api/admin/menus/<id>` | Admin | 删除菜单 |
| GET | `/api/admin/orders` | Admin | 获取所有订单 |
| DELETE | `/api/admin/orders/<id>` | Admin | 删除订单 |
| GET | `/api/admin/stats` | Admin | 获取统计数据 |

> 完整 API 文档见 [yfwd-web/API.md](../yfwd-web/API.md)

---

## 📝 请求鉴权

用户接口需携带 JWT：

```http
Authorization: Bearer <token>
```

也兼容旧版 header：

```http
token: <token>
```

管理员接口需管理员 token（由 `/api/admin/login` 返回，含 `is_admin: true`）。

---

## 💾 数据格式示例

### 创建菜单

```http
POST /api/user/menus
Authorization: Bearer <token>
Content-Type: application/json
```

```json
{
  "name": "家常晚餐",
  "dishes": [
    { "name": "番茄炒蛋", "price": 18, "unit": "份" },
    { "name": "清炒时蔬", "price": 16, "unit": "份" }
  ]
}
```

### 创建点菜记录

```http
POST /api/user/orders
Authorization: Bearer <token>
Content-Type: application/json
```

```json
{
  "menu_id": 1,
  "meal_type": "晚餐",
  "selected_dishes": [
    { "name": "番茄炒蛋", "price": 18, "unit": "份", "quantity": 1 }
  ]
}
```

### AI 生成菜单

```http
POST /api/ai/create-menu
Authorization: Bearer <token>
Content-Type: application/json
```

```json
{
  "description": "帮我做一个 3 人份的清淡晚餐",
  "save": false
}
```

> 返回菜单内容后，前端需用户点击「保存这个菜单」，再调用 `/api/user/menus` 入库。

---

## 🗄️ 数据库表

| 表名 | 说明 |
|------|------|
| `users` | 用户账号、邮箱、密码哈希、昵称、头像 |
| `verification_codes` | 邮箱验证码、用途、过期时间 |
| `ip_rate_limit` | IP 维度发送和注册限流 |
| `email_rate_limit` | 邮箱维度发送限流 |
| `login_failures` | 登录失败次数与锁定 |
| `captcha` | 人机验证题目与答案 |
| `admins` | 管理员账号 |
| `menus` | 用户菜单 + 菜品 JSON + UUID |
| `user_orders` | 点菜记录 + 菜品 JSON + UUID |

数据库初始化与迁移由 [database.py](models/database.py) 自动完成，包括自动建表、添加缺失列、补充旧记录 UUID。

---

## 🔒 安全注意事项

- ✅ 生产环境**必须**更换 `SECRET_KEY` 和 `JWT_SECRET_KEY`
- ✅ 不要公开 `.env`、`dining.db`、邮箱授权码、AI API Key
- ✅ 建议关闭 `FLASK_DEBUG`
- ✅ 生产环境使用 HTTPS
- ✅ 管理员接口建议限制访问来源
- ✅ SQLite 适合小型应用，高并发建议迁移 MySQL / PostgreSQL

---

## 📄 许可证

本项目采用 [MIT License](LICENSE)。

Copyright (c) 2026 subNN"# yfwd" 
