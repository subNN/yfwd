# 一饭为定 · API 接口文档

> **Base URL**：`http://8.156.73.125:5000`（默认，可在登录页脚"后端接口设置"中修改）
> **编码**：UTF-8，请求与响应均为 `application/json`
> **鉴权方式**：除注册/登录/发送验证码/验证码/健康检查外，其余接口需在 `Authorization: Bearer <token>` 中携带 JWT

---

## 目录

- [公共约定](#公共约定)
- [1. 认证模块 `POST|GET /api/auth/*`](#1-认证模块-postget-apiauth)
  - [1.1 获取验证码拼图 `GET /api/auth/captcha`](#11-获取验证码拼图-get-apiauthcaptcha)
  - [1.2 验证人机验证 `POST /api/auth/verify-captcha`](#12-验证人机验证-post-apiauthverify-captcha)
  - [1.3 发送邮箱验证码 `POST /api/auth/send-code`](#13-发送邮箱验证码-post-apiauthsend-code)
  - [1.4 注册 `POST /api/auth/register`](#14-注册-post-apiauthregister)
  - [1.5 登录 `POST /api/auth/login`](#15-登录-post-apiauthlogin)
  - [1.6 获取当前用户 `GET /api/auth/me`](#16-获取当前用户-get-apiauthme)
  - [1.7 退出登录 `POST /api/auth/logout`](#17-退出登录-post-apiauthlogout)
  - [1.8 更新用户资料 `PUT /api/auth/profile`](#18-更新用户资料-put-apiauthprofile)
  - [1.9 忘记密码（检查用户）`POST /api/auth/forgot-password`](#19-忘记密码检查用户-post-apiauthforgot-password)
  - [1.10 重置密码 `POST /api/auth/reset-password`](#110-重置密码-post-apiauthreset-password)
- [2. 用户模块 `GET|POST|PUT|DELETE /api/user/*`](#2-用户模块-getpostputdelete-apiuser)
  - [2.1 获取用户信息 `GET /api/user/info`](#21-获取用户信息-get-apiuserinfo)
  - [2.2 菜单 CRUD](#22-菜单-crud)
    - [获取菜单列表 `GET /api/user/menus`](#221-获取菜单列表-get-apiusermenus)
    - [创建菜单 `POST /api/user/menus`](#222-创建菜单-post-apiusermenus)
    - [获取菜单详情 `GET /api/user/menus/<menu_id>`](#223-获取菜单详情-get-apiusermenusmenu_id)
    - [更新菜单 `PUT /api/user/menus/<menu_id>`](#224-更新菜单-put-apiusermenusmenu_id)
    - [删除菜单 `DELETE /api/user/menus/<menu_id>`](#225-删除菜单-delete-apiusermenusmenu_id)
  - [2.3 菜单导入导出](#23-菜单导入导出)
    - [导出菜单 `GET /api/user/menus/export`](#231-导出菜单-get-apiusermenusexport)
    - [导入菜单 `POST /api/user/menus/import`](#232-导入菜单-post-apiusermenusimport)
  - [2.4 点菜记录 CRUD](#24-点菜记录-crud)
    - [获取点菜记录 `GET /api/user/orders`](#241-获取点菜记录-get-apiuserorders)
    - [提交点菜记录 `POST /api/user/orders`](#242-提交点菜记录-post-apiuserorders)
    - [删除点菜记录 `DELETE /api/user/orders/<order_id>`](#243-删除点菜记录-delete-apiuserordersorder_id)
  - [2.5 点菜记录导入导出](#25-点菜记录导入导出)
    - [导出点菜记录 `GET /api/user/orders/export`](#251-导出点菜记录-get-apiuserordersexport)
    - [导入点菜记录 `POST /api/user/orders/import`](#252-导入点菜记录-post-apiuserordersimport)
- [3. AI 模块 `GET|POST /api/ai/*`](#3-ai-模块-getpost-apiai)
  - [3.1 AI 服务状态 `GET /api/ai/status`](#31-ai-服务状态-get-apiaistatus)
  - [3.2 AI 通用对话 `POST /api/ai/chat`](#32-ai-通用对话-post-apiaichat)
  - [3.3 AI 创建菜单 `POST /api/ai/create-menu`](#33-ai-创建菜单-post-apiaicreate-menu)
  - [3.4 AI 推荐菜品 `POST /api/ai/recommend`](#34-ai-推荐菜品-post-apiairecommend)
- [4. 上传模块 `POST /api/upload/*`](#4-上传模块-post-apiupload)
  - [4.1 上传菜单 `POST /api/upload/menus`](#41-上传菜单-post-apiuploadmenus)
  - [4.2 上传点菜记录 `POST /api/upload/orders`](#42-上传点菜记录-post-apiuploadorders)
- [5. 管理员模块 `GET|POST|DELETE /api/admin/*`](#5-管理员模块-getpostdelete-apiadmin)
  - [5.1 管理员登录 `POST /api/admin/login`](#51-管理员登录-post-apiadminlogin)
  - [5.2 获取所有用户 `GET /api/admin/users`](#52-获取所有用户-get-apiadminusers)
  - [5.3 删除用户 `DELETE /api/admin/users/<user_id>`](#53-删除用户-delete-apiadminusersuser_id)
  - [5.4 获取所有菜单 `GET /api/admin/menus`](#54-获取所有菜单-get-apiadminmenus)
  - [5.5 删除菜单 `DELETE /api/admin/menus/<menu_id>`](#55-删除菜单-delete-apiadminmenusmenu_id)
  - [5.6 获取所有订单 `GET /api/admin/orders`](#56-获取所有订单-get-apiadminorders)
  - [5.7 删除订单 `DELETE /api/admin/orders/<order_id>`](#57-删除订单-delete-apiadminordersorder_id)
  - [5.8 获取统计数据 `GET /api/admin/stats`](#58-获取统计数据-get-apiadminstats)
- [6. 公共接口](#6-公共接口)
  - [6.1 健康检查 `GET /api/health`](#61-健康检查-get-apihealth)
  - [6.2 SMTP 检查 `GET /api/auth/smtp-check`](#62-smtp-检查-get-apiauthsmtp-check)
- [数据模型](#数据模型)
- [错误码汇总](#错误码汇总)

---

## 公共约定

### 通用响应格式

成功：

```json
{
  "success": true,
  "message": "操作描述",    // 可选
  "data": { ... },         // 业务数据
  "key": "value"           // 额外字段可直接平铺
}
```

失败：

```json
{
  "success": false,
  "error": "ERROR_CODE",
  "message": "中文错误描述"
}
```

> 注意：admin 模块部分接口返回 `{"code": 0, "success": true, ...}`，失败时 `{"code": -1, "message": "..."}`。

### JWT 鉴权

- 算法：HS256
- 有效期：默认 7 天；勾选"30 天内自动登录"则为 30 天
- Payload：`{"user_id": 数字, "email": "邮箱", "iat": 时间戳, "exp": 过期时间戳}`
- 请求头 `Authorization: Bearer <token>`，也支持 `token` header
- 管理员 token 包含 `"is_admin": true`

### 邮箱格式

> **发送方**：QQ 邮箱 SMTP 发送
> **接收方**：用户填写的任意合法邮箱（QQ、Gmail、163、企业邮箱等）

---

## 1. 认证模块 `POST|GET /api/auth/*`

### 鉴权说明

`/api/auth/captcha`、`/api/auth/verify-captcha`、`/api/auth/send-code`、`/api/auth/register`、`/api/auth/login`、`/api/auth/forgot-password`、`/api/auth/reset-password` 无需 JWT。

`/api/auth/me`、`/api/auth/logout`、`/api/auth/profile` 需要 JWT。

---

### 1.1 获取验证码拼图 `GET /api/auth/captcha`

获取柱状图排序人机验证码，用于发送验证码前的校验。

#### Request

```
GET /api/auth/captcha
```

无需请求体。

#### Response 200

```json
{
  "success": true,
  "captcha_id": "a1b2c3d4e5f6",
  "question": "请按从高到低的顺序排列柱状图",
  "bars": [
    { "id": "b1", "height": 78 },
    { "id": "b2", "height": 45 },
    { "id": "b3", "height": 92 },
    { "id": "b4", "height": 63 },
    { "id": "b5", "height": 35 },
    { "id": "b6", "height": 81 }
  ],
  "direction": "desc",
  "time_limit": 20,
  "expire_in": 300
}
```

---

### 1.2 验证人机验证 `POST /api/auth/verify-captcha`

仅验证人机验证是否通过（不消耗验证码），用户完成拖动排序后调用。

#### Request

```json
{
  "captcha_id": "a1b2c3d4e5f6",
  "captcha_answer": "b3,b6,b1,b4,b2,b5"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `captcha_id` | string | 是 | `GET /api/auth/captcha` 返回的 captcha_id |
| `captcha_answer` | string | 是 | 用户拖出的排序结果，按 `direction` 顺序，以 `,` 分隔柱状图 ID |

#### Response 200

```json
{
  "success": true,
  "message": "人机验证通过"
}
```

#### 错误码

| HTTP | error | message |
|------|-------|---------|
| 400 | `CAPTCHA_MISSING` | 验证码参数缺失 |
| 400 | `CAPTCHA_FAILED` | 验证码错误或已过期 |

---

### 1.3 发送邮箱验证码 `POST /api/auth/send-code`

向用户邮箱发送 6 位数字验证码。**需要先完成人机验证（调用 `/api/auth/verify-captcha`）。**

#### 业务规则

- IP 一天最多发送 10 次
- 同一邮箱 10 分钟内最多发送 3 次
- 同一邮箱 1 分钟内只能发送 1 次
- 新发送的验证码会覆盖未过期的旧验证码
- 验证码有效期 10 分钟

#### Request

```json
{
  "email": "user@example.com",
  "purpose": "register",
  "captcha_id": "a1b2c3d4e5f6",
  "captcha_answer": "b3,b6,b1,b4,b2,b5"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `email` | string | 是 | 用户邮箱（任意合法邮箱） |
| `purpose` | string | 否 | 默认为 `register`；重置密码时可传 `reset-password` 或 `reset` |
| `captcha_id` | string | 是 | 人机验证 captcha_id |
| `captcha_answer` | string | 是 | 人机验证答案 |

#### Response 200

```json
{
  "success": true,
  "message": "验证码已发送",
  "cooldown": 60,
  "expire_in": 600
}
```

> 如果 SMTP 未配置（Mock 模式），还会返回 `mock_code` 字段。

#### 错误码

| HTTP | error | message |
|------|-------|---------|
| 400 | `EMAIL_REQUIRED` | 请输入邮箱 |
| 400 | `EMAIL_INVALID` | 邮箱格式不正确（支持任意邮箱） |
| 400 | `CAPTCHA_REQUIRED` | 请完成人机验证 |
| 400 | `CAPTCHA_FAILED` | 验证码错误或已过期 |
| 409 | `EMAIL_REGISTERED` | 该邮箱已注册，请直接登录 |
| 429 | `RATE_LIMIT_RESEND` | 发送过于频繁，请 n 秒后再试 |
| 429 | `RATE_LIMIT_IP` | 今日该 IP 发送次数已达上限 |
| 429 | `RATE_LIMIT_EMAIL` | 该邮箱发送次数过多，请 10 分钟后再试 |
| 500 | `MAIL_SEND_FAIL` | 邮件发送失败，请稍后重试 |

---

### 1.4 注册 `POST /api/auth/register`

完成邮箱 + 验证码 + 密码注册，成功后直接返回 JWT。

#### Request

```json
{
  "email": "user@example.com",
  "code": "482931",
  "password": "mypassword",
  "nickname": "小明"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `email` | string | 是 | 用户邮箱 |
| `code` | string | 是 | 6 位数字验证码（4-8 位均可） |
| `password` | string | 是 | 至少 6 位 |
| `nickname` | string | 否 | 1-20 字，不传则取邮箱前缀 |

#### Response 200

```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 10001,
    "email": "user@example.com",
    "nickname": "小明",
    "avatar": null,
    "created_at": "2026-06-22 12:00:00"
  }
}
```

#### 错误码

| HTTP | error | message |
|------|-------|---------|
| 400 | `EMAIL_INVALID` | 邮箱格式不正确 |
| 400 | `CODE_REQUIRED` | 请输入验证码 |
| 400 | `CODE_FORMAT` | 验证码格式不正确 |
| 400 | `PASSWORD_TOO_SHORT` | 密码至少 6 位 |
| 400 | `CODE_WRONG` | 验证码错误或已过期，请重新获取 |
| 400 | `CODE_EXPIRED` | 验证码已过期，请重新获取 |
| 409 | `EMAIL_REGISTERED` | 该邮箱已注册，请直接登录 |
| 429 | `RATE_LIMIT_IP` | 今日该 IP 注册次数已达上限 |
| 500 | `SERVER_ERROR` | 注册失败，请稍后重试 |

---

### 1.5 登录 `POST /api/auth/login`

使用邮箱 + 密码登录。

#### Request

```json
{
  "email": "user@example.com",
  "password": "mypassword",
  "remember": true
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `email` | string | 是 | 用户邮箱 |
| `password` | string | 是 | 密码 |
| `remember` | boolean | 否 | 是否 30 天内自动登录（默认 false，7 天） |

#### Response 200

```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 10001,
    "email": "user@example.com",
    "nickname": "小明",
    "avatar": null
  }
}
```

#### 错误码

| HTTP | error | message |
|------|-------|---------|
| 400 | `EMAIL_INVALID` | 邮箱格式不正确 |
| 400 | `PASSWORD_REQUIRED` | 请输入密码 |
| 401 | `USER_NOT_FOUND` | 该邮箱未注册 |
| 401 | `PASSWORD_WRONG` | 邮箱或密码错误 |
| 423 | `USER_LOCKED` | 账号因多次密码错误被锁定，请 n 秒后再试 |

> 同一邮箱连续 5 次密码错误后锁定 5 分钟。

---

### 1.6 获取当前用户 `GET /api/auth/me`

校验 token 并返回当前登录用户信息。

#### Request

```
GET /api/auth/me
Authorization: Bearer <token>
```

#### Response 200

```json
{
  "success": true,
  "user": {
    "id": 10001,
    "email": "user@example.com",
    "nickname": "小明",
    "avatar": null
  }
}
```

#### 错误码

| HTTP | error | message |
|------|-------|---------|
| 401 | `TOKEN_MISSING` | 未登录 |
| 401 | `TOKEN_INVALID` | token 无效或已过期 |

---

### 1.7 退出登录 `POST /api/auth/logout`

服务器端不做 token 吊销，仅返回确认；客户端需自行清除 token。

#### Request

```
POST /api/auth/logout
Authorization: Bearer <token>
```

#### Response 200

```json
{
  "success": true,
  "message": "已退出"
}
```

---

### 1.8 更新用户资料 `PUT /api/auth/profile`

更新当前用户的昵称。

#### Request

```
PUT /api/auth/profile
Authorization: Bearer <token>
```

```json
{
  "nickname": "新昵称"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `nickname` | string | 是 | 新昵称，不超过 20 字符 |

#### Response 200

```json
{
  "success": true,
  "user": {
    "id": 10001,
    "email": "user@example.com",
    "nickname": "新昵称",
    "avatar": null
  },
  "message": "昵称已更新"
}
```

#### 错误码

| HTTP | error | message |
|------|-------|---------|
| 400 | `NICKNAME_EMPTY` | 昵称不能为空 |
| 400 | `NICKNAME_TOO_LONG` | 昵称不能超过 20 个字符 |
| 401 | `TOKEN_MISSING` | 未登录 |
| 401 | `TOKEN_INVALID` | token 无效 |

---

### 1.9 忘记密码（检查用户）`POST /api/auth/forgot-password`

检查邮箱对应的用户是否存在，存在后才能进入重置密码流程。

#### Request

```json
{
  "email": "user@example.com"
}
```

#### Response 200

```json
{
  "success": true,
  "message": "用户存在",
  "email": "user@example.com"
}
```

#### 错误码

| HTTP | error | message |
|------|-------|---------|
| 400 | `EMAIL_REQUIRED` | 请输入邮箱 |
| 400 | `EMAIL_INVALID` | 邮箱格式不正确 |
| 404 | `USER_NOT_FOUND` | 当前用户不存在 |

---

### 1.10 重置密码 `POST /api/auth/reset-password`

使用验证码重置密码。需先用 `POST /api/auth/send-code` 发送 `purpose` 为 `reset-password` 的验证码。

#### Request

```json
{
  "email": "user@example.com",
  "code": "482931",
  "password": "newpassword"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `email` | string | 是 | 用户邮箱 |
| `code` | string | 是 | 6 位验证码 |
| `password` | string | 是 | 新密码，至少 6 位 |

#### Response 200

```json
{
  "success": true,
  "message": "密码重置成功"
}
```

#### 错误码

| HTTP | error | message |
|------|-------|---------|
| 400 | `EMAIL_REQUIRED` | 请输入邮箱 |
| 400 | `EMAIL_INVALID` | 邮箱格式不正确 |
| 400 | `CODE_REQUIRED` | 请输入验证码 |
| 400 | `CODE_FORMAT` | 验证码格式不正确 |
| 400 | `PASSWORD_REQUIRED` | 请输入新密码 |
| 400 | `PASSWORD_TOO_SHORT` | 密码至少 6 位 |
| 400 | `CODE_WRONG` | 验证码错误或已过期 |
| 400 | `CODE_EXPIRED` | 验证码已过期，请重新获取 |
| 404 | `USER_NOT_FOUND` | 当前用户不存在 |

---

## 2. 用户模块 `GET|POST|PUT|DELETE /api/user/*`

> **所有接口均需 JWT**（`Authorization: Bearer <token>`）。

---

### 2.1 获取用户信息 `GET /api/user/info`

与 `/api/auth/me` 功能相同，获取当前登录用户信息。

#### Response 200

```json
{
  "success": true,
  "user": {
    "id": 10001,
    "email": "user@example.com",
    "nickname": "小明",
    "avatar": null
  }
}
```

---

### 2.2 菜单 CRUD

#### 2.2.1 获取菜单列表 `GET /api/user/menus`

获取当前用户的所有菜单。

#### Response 200

```json
{
  "success": true,
  "menus": [
    {
      "id": 1,
      "name": "家常菜单",
      "uuid": "cd-260622120000a1b2",
      "dishes": [
        { "name": "番茄炒蛋", "price": 15.0, "unit": "份" },
        { "name": "清炒时蔬", "price": 12.0, "unit": "份" }
      ],
      "created_at": "2026-06-22 12:00:00",
      "updated_at": "2026-06-22 12:00:00"
    }
  ]
}
```

---

#### 2.2.2 创建菜单 `POST /api/user/menus`

手动创建菜单，会自动生成 UUID（格式：`cd-yymmddhhmmssxxxxxx`）。

#### Request

```json
{
  "name": "家常菜单",
  "dishes": [
    { "name": "番茄炒蛋", "price": 15.0, "unit": "份" },
    { "name": "清炒时蔬", "price": 12.0, "unit": "份" }
  ]
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 菜单名称 |
| `dishes` | array | 是 | 菜品数组，每个菜品含 `name`、`price`、`unit`（可选，默认"份"） |

#### Response 200

```json
{
  "success": true,
  "menu": {
    "id": 1,
    "name": "家常菜单",
    "uuid": "cd-260622120000a1b2",
    "dishes": [...],
    "created_at": "2026-06-22 12:00:00"
  },
  "message": "菜单已保存"
}
```

---

#### 2.2.3 获取菜单详情 `GET /api/user/menus/<menu_id>`

#### Response 200

```json
{
  "success": true,
  "menu": {
    "id": 1,
    "name": "家常菜单",
    "uuid": "cd-260622120000a1b2",
    "dishes": [...],
    "created_at": "2026-06-22 12:00:00",
    "updated_at": "2026-06-22 12:00:00"
  }
}
```

---

#### 2.2.4 更新菜单 `PUT /api/user/menus/<menu_id>`

编辑已有菜单。UUID 不会变更，只更新时间和内容。

#### Request

```json
{
  "name": "新菜单名",
  "dishes": [...]
}
```

#### Response 200

```json
{
  "success": true,
  "menu": { ... },
  "message": "菜单已更新"
}
```

---

#### 2.2.5 删除菜单 `DELETE /api/user/menus/<menu_id>`

#### Response 200

```json
{
  "success": true,
  "message": "菜单已删除"
}
```

---

### 2.3 菜单导入导出

#### 2.3.1 导出菜单 `GET /api/user/menus/export`

导出当前用户所有菜单（含 UUID）。

#### Response 200

```json
{
  "success": true,
  "menus": [
    {
      "name": "家常菜单",
      "uuid": "cd-260622120000a1b2",
      "dishes": [
        { "name": "番茄炒蛋", "price": 15.0, "unit": "份" }
      ]
    }
  ],
  "total": 1
}
```

---

#### 2.3.2 导入菜单 `POST /api/user/menus/import`

批量导入菜单。支持两种模式：

- **merge**（默认）：基于 UUID 和时间戳策略合并 —— 如果 UUID 匹配，比较时间戳，较新的覆盖较旧的。
- **replace**：清除现有菜单，用导入数据完全替换。

#### Request

```json
{
  "mode": "merge",
  "menus": [
    {
      "name": "家常菜单",
      "uuid": "cd-260622120000a1b2",
      "dishes": [
        { "name": "番茄炒蛋", "price": 15.0, "unit": "份" }
      ]
    }
  ]
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `mode` | string | 否 | `"merge"` 或 `"replace"`，默认 `"merge"` |
| `menus` | array | 是 | 菜单数组 |

> 也支持直接传数组 `[{...}, {...}]`，或 `{"name": "xxx", "dishes": [...]}` 单条。

#### Response 200

```json
{
  "success": true,
  "imported_count": 1,
  "skipped_count": 0,
  "total_count": 1,
  "imported_ids": [1],
  "menus": [...],
  "message": "成功导入 1 个菜单"
}
```

---

### 2.4 点菜记录 CRUD

#### 2.4.1 获取点菜记录 `GET /api/user/orders`

获取当前用户的所有点菜记录。

#### Response 200

```json
{
  "success": true,
  "orders": [
    {
      "id": 1,
      "uuid": "dc-260622120000a1b2",
      "meal_type": "午餐",
      "selected_dishes": [
        { "name": "番茄炒蛋", "price": 15.0, "unit": "份", "quantity": 2 }
      ],
      "order_date": "2026-06-22",
      "order_time": "2026-06-22T12:00:00"
    }
  ]
}
```

---

#### 2.4.2 提交点菜记录 `POST /api/user/orders`

提交一条点菜记录，会自动生成 UUID（格式：`dc-yymmddhhmmssxxxxxx`）。

#### Request

```json
{
  "menu_id": 1,
  "meal_type": "午餐",
  "selected_dishes": [
    { "name": "番茄炒蛋", "price": 15.0, "unit": "份", "quantity": 2 }
  ]
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `menu_id` | int | 否 | 关联的菜单 ID |
| `meal_type` | string | 是 | 餐别（如"早餐""午餐""晚餐"） |
| `selected_dishes` | array | 是 | 选中的菜品，每个含 `name`、`price`、`unit`、`quantity` |

#### Response 200

```json
{
  "success": true,
  "order_id": 1,
  "message": "点菜记录已保存"
}
```

---

#### 2.4.3 删除点菜记录 `DELETE /api/user/orders/<order_id>`

只能删除自己的记录。

#### Response 200

```json
{
  "success": true,
  "message": "记录已删除"
}
```

---

### 2.5 点菜记录导入导出

#### 2.5.1 导出点菜记录 `GET /api/user/orders/export`

导出当前用户所有点菜记录。

#### Response 200

```json
{
  "success": true,
  "orders": [
    {
      "id": 1,
      "uuid": "dc-260622120000a1b2",
      "meal_type": "午餐",
      "selected_dishes": [...],
      "order_date": "2026-06-22",
      "order_time": "2026-06-22T12:00:00"
    }
  ],
  "total": 1
}
```

---

#### 2.5.2 导入点菜记录 `POST /api/user/orders/import`

批量导入点菜记录。基于 UUID 和时间戳策略合并。

#### Request

```json
{
  "orders": [
    {
      "meal_type": "午餐",
      "uuid": "dc-260622120000a1b2",
      "selected_dishes": [
        { "name": "番茄炒蛋", "price": 15.0, "unit": "份", "quantity": 2 }
      ],
      "order_time": "2026-06-22T12:00:00"
    }
  ]
}
```

> 也支持直接传数组或兼容 `{"meal": "午餐", "dishes": [...], "time": "..."}` 等格式。

#### Response 200

```json
{
  "success": true,
  "imported_count": 1,
  "skipped_count": 0,
  "total_count": 1,
  "imported_ids": [1],
  "orders": [...],
  "message": "成功导入 1 条记录"
}
```

---

## 3. AI 模块 `GET|POST /api/ai/*`

> **除 `/api/ai/status` 外均需 JWT，且仅限普通用户（管理员不可用）。**

---

### 3.1 AI 服务状态 `GET /api/ai/status`

检查 AI 服务是否已配置启用。

#### Response 200

```json
{
  "success": true,
  "enabled": true,
  "model": "gpt-4o-mini"
}
```

---

### 3.2 AI 通用对话 `POST /api/ai/chat`

通用 AI 对话接口。可自然语言描述需求：生成菜单、推荐菜品、闲聊等。

**AI 不会自动创建菜单，生成后需用户点击"保存"确认。**

#### Request

```json
{
  "message": "帮我生成一个三菜一汤的家常菜单"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `message` | string | 是 | 用户输入的自然语言消息 |

#### Response 200

```json
{
  "success": true,
  "type": "action",
  "text_intro": "好的，我已为你生成了一个家常菜单...",
  "data": {
    "action": "create_menu",
    "menu": {
      "name": "三菜一汤家常菜单",
      "dishes": [
        { "name": "番茄炒蛋", "price": 15, "unit": "份" },
        { "name": "青椒肉丝", "price": 20, "unit": "份" },
        { "name": "清炒时蔬", "price": 12, "unit": "份" },
        { "name": "紫菜蛋花汤", "price": 8, "unit": "份" }
      ]
    }
  },
  "menu_id": null,
  "saved": false
}
```

> `saved: false` 表示未保存，前端应展示"保存"按钮供用户确认。

#### 错误码

| HTTP | error | message |
|------|-------|---------|
| 400 | `MESSAGE_REQUIRED` | 请输入消息 |
| 401 | `TOKEN_INVALID` | 请先登录 |
| 503 | `AI_DISABLED` | AI 服务未配置，请联系管理员 |
| 500 | `AI_ERROR` | AI 服务异常 |

---

### 3.3 AI 创建菜单 `POST /api/ai/create-menu`

根据描述生成菜单。**默认不保存**，需传 `save: true` 才会入库。

#### Request

```json
{
  "description": "三菜一汤，偏清淡",
  "save": false
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `description` | string | 是 | 菜单描述 |
| `save` | boolean | 否 | 是否立即保存，默认 `false` |

#### Response 200

```json
{
  "success": true,
  "menu": {
    "name": "清淡三菜一汤",
    "dishes": [...]
  },
  "menu_id": null,
  "saved": false,
  "text_intro": "已根据你的描述生成...",
  "raw_json": "..."
}
```

> 当 `saved: true` 时，`menu_id` 为数据库中的菜单 ID；前端应据此展示已保存的状态。

#### 错误码

| HTTP | error | message |
|------|-------|---------|
| 400 | `DESCRIPTION_REQUIRED` | 请描述你想创建的菜单 |
| 401 | `TOKEN_INVALID` | 请先登录 |
| 503 | `AI_DISABLED` | AI 服务未配置 |
| 500 | `AI_ERROR` | AI 服务异常 |
| 500 | `SAVE_FAILED` | 菜单已生成但保存失败 |

---

### 3.4 AI 推荐菜品 `POST /api/ai/recommend`

根据用户口味偏好推荐菜品。

#### Request

```json
{
  "preference": "想吃辣的，不要猪肉",
  "exclude": "",
  "count": 5
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `preference` | string | 是 | 口味偏好（也支持 `query` 字段） |
| `exclude` | string | 否 | 排除的食材 |
| `count` | int | 否 | 推荐数量，默认 5 |

#### Response 200

```json
{
  "success": true,
  "dishes": [
    { "name": "麻辣水煮鱼", "price": 45, "unit": "份" },
    { "name": "辣子鸡丁", "price": 30, "unit": "份" }
  ],
  "text_intro": "为你推荐以下菜品...",
  "raw_json": "..."
}
```

#### 错误码

| HTTP | error | message |
|------|-------|---------|
| 400 | `PREFERENCE_REQUIRED` | 请描述你的口味偏好 |
| 401 | `TOKEN_INVALID` | 请先登录 |
| 503 | `AI_DISABLED` | AI 服务未配置 |
| 500 | `AI_ERROR` | AI 服务异常 |

---

## 4. 上传模块 `POST /api/upload/*`

> **均需 JWT。**

---

### 4.1 上传菜单 `POST /api/upload/menus`

上传菜单数据到服务器。

#### Request

```json
{
  "menus": [
    {
      "name": "家常菜单",
      "dishes": [
        { "name": "番茄炒蛋", "price": 15.0, "unit": "份" }
      ]
    }
  ]
}
```

> 如果菜单名已存在则更新，否则新增。

#### Response 200

```json
{
  "success": true,
  "message": "上传成功，新增 1 个菜单，更新 0 个菜单"
}
```

---

### 4.2 上传点菜记录 `POST /api/upload/orders`

上传点菜记录到服务器。

#### Request

```json
{
  "orders": [
    {
      "meal_type": "午餐",
      "selected_dishes": [
        { "name": "番茄炒蛋", "price": 15.0, "unit": "份", "quantity": 2 }
      ],
      "order_time": "2026-06-22T12:00:00"
    }
  ]
}
```

> 支持两种格式：`meal_type`/`selected_dishes` 或 `meal`/`dishes`/`time`（小程序兼容格式）。
> 重复记录会被自动过滤跳过。

#### Response 200

```json
{
  "success": true,
  "message": "上传成功，新增 1 个订单，0 个订单已存在"
}
```

---

## 5. 管理员模块 `GET|POST|DELETE /api/admin/*`

> `/api/admin/login` 无需 JWT，其余均需管理员 token（`is_admin: true`）。

---

### 5.1 管理员登录 `POST /api/admin/login`

#### Request

```json
{
  "username": "admin",
  "password": "admin123"
}
```

#### Response 200

```json
{
  "code": 0,
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIs..."
}
```

#### 错误码

| HTTP | code | message |
|------|------|---------|
| 400 | -1 | 用户名和密码必填 |
| 401 | -1 | 凭据无效 |

---

### 5.2 获取所有用户 `GET /api/admin/users`

#### Response 200

```json
{
  "code": 0,
  "success": true,
  "data": [
    {
      "id": 10001,
      "openid": "",
      "nickname": "小明",
      "avatar_url": null,
      "created_at": "2026-06-22 12:00:00",
      "last_login_at": "2026-06-22 12:30:00"
    }
  ],
  "count": 1
}
```

---

### 5.3 删除用户 `DELETE /api/admin/users/<user_id>`

#### Response 200

```json
{
  "code": 0,
  "success": true,
  "message": "用户 10001 已删除"
}
```

---

### 5.4 获取所有菜单 `GET /api/admin/menus`

#### Response 200

```json
{
  "code": 0,
  "success": true,
  "data": [...],
  "count": 10
}
```

---

### 5.5 删除菜单 `DELETE /api/admin/menus/<menu_id>`

#### Response 200

```json
{
  "code": 0,
  "success": true,
  "message": "菜单 1 已删除"
}
```

---

### 5.6 获取所有订单 `GET /api/admin/orders`

#### Response 200

```json
{
  "code": 0,
  "success": true,
  "data": [...],
  "count": 10
}
```

---

### 5.7 删除订单 `DELETE /api/admin/orders/<order_id>`

#### Response 200

```json
{
  "code": 0,
  "success": true,
  "message": "订单 1 已删除"
}
```

---

### 5.8 获取统计数据 `GET /api/admin/stats`

#### Response 200

```json
{
  "code": 0,
  "success": true,
  "data": {
    "userCount": 100,
    "menuCount": 50,
    "orderCount": 200,
    "todayOrderCount": 5
  }
}
```

---

## 6. 公共接口

### 6.1 健康检查 `GET /api/health`

```json
{
  "status": "ok",
  "message": "服务运行中",
  "timestamp": "2026-06-22T12:00:00"
}
```

### 6.2 SMTP 检查 `GET /api/auth/smtp-check`

检查邮件服务配置和连通性。

```json
{
  "success": true,
  "message": "SMTP 连接正常",
  "config": {
    "host": "smtp.qq.com",
    "port": 465,
    "user": "xxx@qq.com"
  }
}
```

---

## 数据模型

### Menu（菜单）

```jsonc
{
  "id": 1,                          // int, 自增主键
  "uuid": "cd-260622120000a1b2",    // 唯一标识，cd-yymmddhhmmssXXXXXX
  "name": "家常菜单",                // 菜单名称
  "user_id": 10001,                 // 所属用户 ID
  "dishes": [                       // 菜品数组（JSON）
    {
      "name": "番茄炒蛋",            // 菜品名称
      "price": 15.0,                // 单价
      "unit": "份"                  // 单位
    }
  ],
  "created_at": "2026-06-22 12:00:00",
  "updated_at": "2026-06-22 12:00:00"
}
```

### Order（点菜记录）

```jsonc
{
  "id": 1,                          // int, 自增主键
  "uuid": "dc-260622120000a1b2",    // 唯一标识，dc-yymmddhhmmssXXXXXX
  "user_id": 10001,
  "menu_id": 1,                     // 关联菜单 ID（可为空）
  "meal_type": "午餐",              // 餐别
  "selected_dishes": [              // 已选菜品数组（JSON）
    {
      "name": "番茄炒蛋",
      "price": 15.0,
      "unit": "份",
      "quantity": 2
    }
  ],
  "order_date": "2026-06-22",
  "order_time": "2026-06-22T12:00:00"
}
```

### User（用户）

```jsonc
{
  "id": 10001,
  "email": "user@example.com",
  "nickname": "小明",
  "avatar": null
}
```

### UUID 格式

- **菜单 UUID**：`cd-yymmddhhmmssXXXXXX`（cd-年月日时分秒 + 6 位随机字符）
- **点菜记录 UUID**：`dc-yymmddhhmmssXXXXXX`（dc-年月日时分秒 + 6 位随机字符）
- 创建时生成，编辑后不变，仅更新时间戳
- 导入时基于 UUID 匹配 + 时间戳比较策略决定覆盖还是跳过

---

## 错误码汇总

### 认证相关

| error | 含义 |
|-------|------|
| `EMAIL_REQUIRED` | 邮箱为空 |
| `EMAIL_INVALID` | 邮箱格式错误 |
| `EMAIL_REGISTERED` | 邮箱已被注册 |
| `CODE_REQUIRED` | 验证码为空 |
| `CODE_FORMAT` | 验证码格式错误 |
| `CODE_WRONG` | 验证码错误 |
| `CODE_EXPIRED` | 验证码过期 |
| `PASSWORD_REQUIRED` | 密码为空 |
| `PASSWORD_TOO_SHORT` | 密码太短 |
| `PASSWORD_WRONG` | 密码错误 |
| `USER_NOT_FOUND` | 用户不存在 |
| `USER_LOCKED` | 账号被锁定 |
| `TOKEN_MISSING` | 缺少 token |
| `TOKEN_INVALID` | token 无效 |
| `TOKEN_REQUIRED` | 请先登录 |
| `ADMIN_REQUIRED` | 需要管理员权限 |
| `ADMIN_NOT_ALLOWED` | 管理员不能使用此功能 |
| `NICKNAME_EMPTY` | 昵称为空 |
| `NICKNAME_TOO_LONG` | 昵称过长 |

### 限流相关

| error | 含义 |
|-------|------|
| `RATE_LIMIT_IP` | IP 当日发送/注册次数超限（10 次） |
| `RATE_LIMIT_RESEND` | 重发间隔不足 1 分钟 |
| `RATE_LIMIT_EMAIL` | 邮箱发送次数过多（10 分钟内 3 次） |

### 业务相关

| error | 含义 |
|-------|------|
| `NAME_REQUIRED` | 菜单名称为空 |
| `DISHES_EMPTY` | 菜品列表为空 |
| `DISHES_INVALID` | 菜品格式不正确 |
| `MEAL_TYPE_REQUIRED` | 餐别为空 |
| `MENU_NOT_FOUND` | 菜单不存在 |
| `NOT_FOUND` | 记录不存在 |
| `MESSAGE_REQUIRED` | AI 消息为空 |
| `DESCRIPTION_REQUIRED` | 菜单描述为空 |
| `PREFERENCE_REQUIRED` | 口味偏好为空 |
| `AI_DISABLED` | AI 服务未配置 |
| `AI_ERROR` | AI 服务异常 |
| `SAVE_FAILED` | 保存失败 |
| `IMPORT_ERROR` | 导入失败 |
| `EXPORT_ERROR` | 导出失败 |
| `INVALID_FORMAT` | 数据格式不正确 |
| `MAIL_SEND_FAIL` | 邮件发送失败 |
| `SERVER_ERROR` | 服务器内部错误 |
| `SAVE_ERROR` | 保存失败 |
| `UPDATE_ERROR` | 更新失败 |
| `DELETE_ERROR` | 删除失败 |
| `GET_ERROR` | 获取失败 |
| `LOGIN_ERROR` | 登录失败 |
| `UPLOAD_ERROR` | 上传失败 |
| `MISSING_DATA` | 缺少数据 |
| `UPDATE_FAILED` | 更新失败 |
| `UPDATE_FAIL` | 更新失败 |
| `CAPTCHA_MISSING` | 人机验证参数缺失 |
| `CAPTCHA_FAILED` | 人机验证失败 |
| `CAPTCHA_REQUIRED` | 需要人机验证 |