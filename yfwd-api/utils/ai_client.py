"""AI 服务客户端，兼容 OpenAI API 格式"""

import json
import re
import requests
from config import Config


class AIClient:

    @staticmethod
    def is_enabled():
        return Config.AI_ENABLED and Config.AI_API_KEY and Config.AI_API_KEY != 'sk-your-api-key-here'

    @staticmethod
    def _chat(messages, max_tokens=None, temperature=None):
        """底层调用 AI API，返回 (success, content, error_msg)"""
        if not AIClient.is_enabled():
            return False, '', 'AI 服务未配置，请在环境变量中设置 AI_API_KEY'

        url = f"{Config.AI_API_URL}/chat/completions"
        headers = {
            'Authorization': f'Bearer {Config.AI_API_KEY}',
            'Content-Type': 'application/json',
        }
        body = {
            'model': Config.AI_MODEL,
            'messages': messages,
            'max_tokens': max_tokens or Config.AI_MAX_TOKENS,
            'temperature': temperature or Config.AI_TEMPERATURE,
        }

        try:
            resp = requests.post(url, headers=headers, json=body, timeout=60)
            if resp.status_code != 200:
                err_detail = resp.text[:300]
                print(f'[AI] API 错误 {resp.status_code}: {err_detail}')
                return False, '', f'AI 服务返回错误 {resp.status_code}'
            data = resp.json()
            content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
            return True, content, ''
        except requests.Timeout:
            return False, '', 'AI 服务请求超时'
        except requests.ConnectionError:
            return False, '', '无法连接 AI 服务'
        except Exception as e:
            print(f'[AI] 请求异常: {e}')
            return False, '', f'AI 服务调用异常: {e}'

    @staticmethod
    def _extract_json_from_markdown(content):
        """从 markdown 代码块中提取 JSON，返回 (text_intro, json_str)。

        支持两种格式：
        1. 前面是文字介绍，后面是 ```json ... ```
        2. 整个内容被 ```json ... ``` 包裹
        """
        content = content.strip()

        # 查找所有 ```json 代码块
        json_block_pattern = re.compile(r'```(?:json)?\s*([\s\S]*?)\s*```', re.IGNORECASE)
        matches = list(json_block_pattern.finditer(content))

        if matches:
            # 取最后一个代码块作为 JSON（文字介绍可能在前面）
            last_match = matches[-1]
            json_str = last_match.group(1).strip()

            # 文字介绍是代码块之前的内容，去掉其他代码块
            text_intro = content[:last_match.start()].strip()
            # 去掉之前的代码块内容
            text_intro = json_block_pattern.sub('', text_intro).strip()

            return text_intro, json_str

        # 没有代码块，尝试直接解析整个内容为 JSON
        try:
            json.loads(content)
            return '', content
        except json.JSONDecodeError:
            pass

        return content, ''

    @staticmethod
    def _normalize_dishes(dishes):
        """把 AI 生成的 dishes 标准化成数据库格式：[{name, price, unit}, ...]"""
        if not isinstance(dishes, list):
            return []
        normalized = []
        for d in dishes:
            if not isinstance(d, dict):
                continue
            name = str(d.get('name') or d.get('菜名') or '').strip()
            if not name:
                continue
            # 价格
            price_raw = d.get('price') or d.get('价格') or d.get('参考价格') or 0
            try:
                price = float(price_raw)
                if price < 0:
                    price = 0
            except (TypeError, ValueError):
                # 可能是 "¥18" 这样的字符串
                digits = re.findall(r'\d+\.?\d*', str(price_raw))
                price = float(digits[0]) if digits else 0

            # 单位
            unit = str(d.get('unit') or d.get('单位') or '份').strip()
            if not unit:
                unit = '份'

            normalized.append({'name': name, 'price': price, 'unit': unit})
        return normalized

    @staticmethod
    def chat(user_input, context=''):
        """通用对话：可创建菜单、推荐菜品等"""

        system_prompt = '''你是一饭为定美食助手的 AI 助手。你可以：
1. 帮用户创建菜单：理解用户想吃什么，生成结构化菜单
2. 推荐菜品：根据用户的偏好、季节、心情等推荐合适的菜品
3. 闲聊饮食话题

=== 回复格式规则（严格遵守）===

【场景1：用户明确要创建菜单（如"帮我做菜单"、"我想吃川菜"等）】
回复分两部分：
① 上面：用自然语言写一段简短的菜单介绍和推荐理由（100-200字，口语化，亲切）
② 下面：用 ```json 代码块包裹以下 JSON 格式（代码块必须以 ```json 开头，以 ``` 结尾）

JSON 内容必须严格遵循以下格式（字段名和数据类型不能改）：
{
  "action": "create_menu",
  "name": "菜单名（不超过8个中文字，简洁有创意）",
  "dishes": [
    {"name": "菜名1", "price": 价格数字, "unit": "份"},
    {"name": "菜名2", "price": 价格数字, "unit": "份"}
  ]
}

【场景2：用户要推荐菜品（如"推荐几道"、"我想吃辣的"等）】
回复分两部分：
① 上面：用自然语言写推荐理由和每道菜的介绍（150-250字）
② 下面：用 ```json 代码块包裹以下 JSON 格式：

{
  "action": "recommend",
  "dishes": [
    {"name": "菜名1", "price": 价格数字, "unit": "份"},
    {"name": "菜名2", "price": 价格数字, "unit": "份"}
  ],
  "summary": "推荐总结语"
}

【场景3：普通聊天或闲聊饮食】
直接回复自然语言文字，不要写 JSON。

=== 重要约束（必须遵守）===
1. 菜名以中式家常菜和小吃为主，默认一人份，如果用户说明是多人，则平均一人1.5道菜，菜的份数取整
2. price 必须是数字（整数或小数都行），不能是字符串，不能加 ¥ 符号
3. unit 默认是 "份"，也可以是 "碗"、"盘"、"份" 等，按真实情况决定
4. 菜单名不超过 8 个中文字
5. JSON 必须是合法格式，字段名必须是英文
6. 代码块必须用 ```json 和 ``` 包裹，JSON 外面不能有其他文字'''

        messages = [{'role': 'system', 'content': system_prompt}]
        if context:
            messages.append({'role': 'system', 'content': f'用户已有菜单参考：{context}'})
        messages.append({'role': 'user', 'content': user_input})

        ok, content, err = AIClient._chat(messages)

        if not ok:
            return {'success': False, 'error': err}

        text_intro, json_str = AIClient._extract_json_from_markdown(content)

        if json_str:
            try:
                parsed = json.loads(json_str)
                if isinstance(parsed, dict):
                    action = parsed.get('action')
                    if action == 'create_menu':
                        dishes = AIClient._normalize_dishes(parsed.get('dishes', []))
                        return {
                            'success': True,
                            'type': 'action',
                            'text_intro': text_intro,
                            'data': {
                                'action': 'create_menu',
                                'name': str(parsed.get('name') or 'AI 菜单'),
                                'dishes': dishes
                            },
                            'raw_json': json_str
                        }
                    elif action == 'recommend':
                        dishes = AIClient._normalize_dishes(parsed.get('dishes', []))
                        return {
                            'success': True,
                            'type': 'action',
                            'text_intro': text_intro,
                            'data': {
                                'action': 'recommend',
                                'dishes': dishes,
                                'summary': str(parsed.get('summary') or '')
                            },
                            'raw_json': json_str
                        }
            except json.JSONDecodeError:
                pass

        return {
            'success': True,
            'type': 'chat',
            'data': {'reply': text_intro or content.strip()}
        }

    @staticmethod
    def create_menu(description, user_menus_context=''):
        """根据描述创建菜单"""

        system_prompt = '''你是一饭为定美食 AI。根据用户描述帮他生成一份菜单。

=== 回复格式（严格遵守）===

回复分两部分：
① 上面：用自然语言写一段简短的菜单介绍和推荐理由（100-200字，亲切自然，说明这套餐的特色和适合的场景）
② 下面：用 ```json 代码块包裹以下 JSON 格式

JSON 内容必须严格遵循以下格式（字段名和数据类型不能改，必须与数据库格式一致）：
{
  "name": "菜单名（不超过8个中文字，简洁有创意）",
  "dishes": [
    {"name": "菜名1", "price": 价格数字, "unit": "份"},
    {"name": "菜名2", "price": 价格数字, "unit": "份"}
  ]
}

=== 约束 ===
1. 菜名以中式家常菜和小吃为主，默认一人份，如果用户说明是多人，则平均一人1.5道菜，菜的份数取整
2. price 必须是数字（整数，比如 18、25、38），不能是字符串，不能加 ¥ 符号
3. unit 默认是 "份"，也可以是 "碗"、"盘" 等
4. 菜单名不超过 8 个中文字
5. JSON 必须是合法格式，字段名必须是英文
6. 代码块必须用 ```json 和 ``` 包裹，代码块外面只能有文字介绍
7. 文字介绍和代码块之间最好空一行，让格式更清晰'''

        messages = [{'role': 'system', 'content': system_prompt}]
        if user_menus_context:
            messages.append({
                'role': 'system',
                'content': f'用户已有菜单参考：{user_menus_context}'
            })
        messages.append({
            'role': 'user',
            'content': f'请帮我创建菜单，要求：{description}'
        })

        ok, content, err = AIClient._chat(messages, max_tokens=2000)
        if not ok:
            return {'success': False, 'error': err}

        text_intro, json_str = AIClient._extract_json_from_markdown(content)

        if json_str:
            try:
                menu = json.loads(json_str)
                if isinstance(menu, dict) and 'dishes' in menu:
                    dishes = AIClient._normalize_dishes(menu.get('dishes', []))
                    normalized_menu = {
                        'name': str(menu.get('name') or description[:8] or 'AI 菜单'),
                        'dishes': dishes
                    }
                    return {
                        'success': True,
                        'menu': normalized_menu,
                        'text_intro': text_intro,
                        'raw_json': json_str
                    }
            except json.JSONDecodeError:
                pass

        return {'success': False, 'error': 'AI 返回格式异常，请重试', 'raw': content[:300]}

    @staticmethod
    def recommend(preference, exclude_names='', count=5):
        """推荐菜品"""

        system_prompt = '''你是一饭为定美食推荐 AI。根据用户偏好推荐菜品。

=== 回复格式（严格遵守）===

回复分两部分：
① 上面：用自然语言写推荐理由，逐道菜介绍特点和为什么推荐（150-250字，亲切自然）
② 下面：用 ```json 代码块包裹以下 JSON 格式

JSON 内容必须严格遵循以下格式（字段名和数据类型不能改，必须与数据库格式一致）：
{
  "dishes": [
    {"name": "菜名1", "price": 价格数字, "unit": "份"},
    {"name": "菜名2", "price": 价格数字, "unit": "份"}
  ],
  "summary": "总结推荐语，一句话"
}

=== 约束 ===
1. 菜名以中式家常菜和小吃为主，默认一人份，如果用户说明是多人，则平均一人1.5道菜，菜的份数取整，考虑季节和营养搭配
2. price 必须是数字（整数），不能是字符串，不能加 ¥ 符号
3. unit 默认是 "份"，也可以是 "碗"、"盘" 等
4. JSON 必须是合法格式，字段名必须是英文
5. 代码块必须用 ```json 和 ``` 包裹，代码块外面只能有文字介绍'''

        user_msg = f'请推荐菜品。偏好：{preference}。'
        if exclude_names:
            user_msg += f' 排除：{exclude_names}。'
        user_msg += f' 推荐 {count} 道左右。'

        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_msg},
        ]

        ok, content, err = AIClient._chat(messages, max_tokens=2000)
        if not ok:
            return {'success': False, 'error': err}

        text_intro, json_str = AIClient._extract_json_from_markdown(content)

        if json_str:
            try:
                result = json.loads(json_str)
                if isinstance(result, dict) and 'dishes' in result:
                    dishes = AIClient._normalize_dishes(result.get('dishes', []))
                    return {
                        'success': True,
                        'data': {
                            'dishes': dishes,
                            'summary': str(result.get('summary') or '')
                        },
                        'text_intro': text_intro,
                        'raw_json': json_str
                    }
            except json.JSONDecodeError:
                pass

        return {'success': False, 'error': 'AI 返回格式异常，请重试', 'raw': content[:300]}
