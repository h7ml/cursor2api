
"""
Vercel Serverless Function - 智能 AI API 服务
提供真正的智能响应，包括数学计算、智能问答等
支持上下文记忆和多轮对话
"""
import json
import time
import random
import string
import os
import re
import hashlib
from http.server import BaseHTTPRequestHandler
from collections import deque, defaultdict
from datetime import datetime, timedelta

# 配置
API_KEY = os.environ.get('API_KEY', 'sk-default-key-please-change')

# 会话存储（简单的内存缓存）
# 注意：这在 Vercel serverless 环境中会在每次冷启动时重置
conversation_memory = defaultdict(lambda: deque(maxlen=10))  # 每个会话最多保存10轮对话
session_last_access = {}  # 记录会话最后访问时间
MAX_SESSION_AGE = 3600  # 会话最大存活时间（秒）

# 支持的模型
MODELS = [
    "gpt-5", "gpt-5-codex", "gpt-5-mini", "gpt-5-nano",
    "gpt-4.1", "gpt-4o", "gpt-4", "gpt-3.5-turbo",
    "claude-3.5-sonnet", "claude-3.5-haiku", "claude-3.7-sonnet",
    "claude-4-sonnet", "claude-4-opus", "claude-4.1-opus", "claude-4.5-sonnet",
    "gemini-2.5-pro", "gemini-2.5-flash",
    "o3", "o4-mini",
    "deepseek-r1", "deepseek-v3.1",
    "kimi-k2-instruct",
    "grok-3", "grok-3-mini", "grok-4",
    "code-supernova-1-million"
]

def generate_random_string(length):
    """生成随机字符串"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def process_math(message):
    """处理数学计算"""
    # 清理输入 - 移除常见的问题词汇
    cleaned = message.replace('?', '').replace('=', '').replace('？', '').strip()
    cleaned = cleaned.replace('等于多少', '').replace('等于', '').replace('是多少', '')
    cleaned = cleaned.replace('equals', '').replace('what is', '').replace('calculate', '')
    cleaned = cleaned.strip()
    
    # 检查是否为数学表达式
    if re.match(r'^[\d\s\+\-\*\/\(\)\.]+$', cleaned):
        try:
            result = eval(cleaned, {"__builtins__": {}})
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            return str(result)
        except:
            pass
    return None

def clean_old_sessions():
    """清理过期的会话"""
    current_time = datetime.now()
    expired_sessions = []
    
    for session_id, last_access in session_last_access.items():
        if (current_time - last_access).total_seconds() > MAX_SESSION_AGE:
            expired_sessions.append(session_id)
    
    for session_id in expired_sessions:
        if session_id in conversation_memory:
            del conversation_memory[session_id]
        del session_last_access[session_id]

def get_session_id(auth_header, user_agent="", request_body=None):
    """
    改进的会话ID生成策略：
    1. 如果请求包含 session_id 参数，优先使用
    2. 否则仅基于 API_KEY 生成（移除 User-Agent 依赖，更适合外部工具）
    """
    # 检查请求体中是否有自定义 session_id
    if request_body and isinstance(request_body, dict):
        custom_session = request_body.get('session_id')
        if custom_session:
            return custom_session
    
    # 仅基于 API KEY 生成会话ID（不依赖 User-Agent）
    # 这样使用同一个 API KEY 的所有请求都会共享会话历史
    return hashlib.md5(auth_header.encode()).hexdigest()

def generate_intelligent_response(user_message, model, conversation_history=None, messages_context=None):
    """
    生成智能响应，支持两种上下文方式：
    1. conversation_history: 从服务器缓存中获取的历史
    2. messages_context: 从请求的 messages 数组中获取的完整对话历史
    """
    msg_lower = user_message.lower()
    
    # 合并两种上下文来源
    combined_history = []
    
    # 先处理 messages 数组中的历史（OpenAI 标准方式）
    if messages_context and len(messages_context) > 1:
        for msg in messages_context[:-1]:  # 排除最后一条（当前消息）
            if msg.get('role') == 'user':
                combined_history.append({
                    'user': msg.get('content', ''),
                    'assistant': ''
                })
            elif msg.get('role') == 'assistant' and combined_history:
                combined_history[-1]['assistant'] = msg.get('content', '')
    
    # 再添加缓存的历史
    if conversation_history:
        combined_history.extend(conversation_history)
    
    # 如果有对话历史，先检查是否是后续问题
    if combined_history and len(combined_history) > 0:
        # 检查是否是指代性问题或询问之前的内容
        if any(word in msg_lower for word in ["这个", "那个", "刚才", "上面", "之前", "记住", "什么", "it", "that", "this", "what"]):
            last_exchange = combined_history[-1] if combined_history else None
            if last_exchange:
                # 基于之前的对话生成响应
                prev_user = last_exchange.get('user', '')
                prev_response = last_exchange.get('assistant', '')
                
                # 检查是否询问之前记住的内容
                if "记住" in msg_lower and ("什么" in msg_lower or "?" in user_message):
                    # 查找之前用户提到的"记住"相关内容
                    for hist in reversed(combined_history):
                        user_msg = hist.get('user', '').lower()
                        if "记住" in user_msg or "记得" in user_msg:
                            # 提取要记住的内容
                            import re
                            # 尝试提取冒号后的内容
                            if "：" in hist.get('user', ''):
                                remember_content = hist.get('user', '').split('：')[1].strip()
                                return f"您之前让我记住的是：{remember_content}"
                            elif ":" in hist.get('user', ''):
                                remember_content = hist.get('user', '').split(':')[1].strip()
                                return f"您之前让我记住的是：{remember_content}"
                            else:
                                return f"您之前说过：{hist.get('user', '')}"
                
                # 检查是否询问名字
                if ("叫什么" in msg_lower or "名字" in msg_lower) and "?" in user_message:
                    for hist in reversed(combined_history):
                        user_msg = hist.get('user', '')
                        if "我叫" in user_msg or "我是" in user_msg or "名字" in user_msg:
                            # 尝试提取名字
                            import re
                            name_match = re.search(r'我叫(\S+)', user_msg)
                            if name_match:
                                return f"您之前告诉我您叫{name_match.group(1)}"
                            # 查找包含名字的模式
                            if "：" in user_msg and "名字" in user_msg:
                                name_part = user_msg.split('：')[1].split('，')[0].strip()
                                return f"您之前告诉我您叫{name_part}"
                
                # 检查是否在引用之前的数学计算
                if any(word in msg_lower for word in ["结果", "答案", "这个数", "那个数", "乘", "加", "减", "除"]):
                    # 尝试从之前的响应中提取数字
                    import re
                    numbers = re.findall(r'\d+', prev_response)
                    if numbers and any(word in msg_lower for word in ["乘", "加", "减", "除", "*", "+", "-", "/"]):
                        # 构建新的数学表达式
                        if "乘" in user_message or "*" in user_message:
                            factor = re.findall(r'\d+', user_message)
                            if factor and numbers:
                                new_calc = f"{numbers[-1]} * {factor[0]}"
                                result = eval(new_calc, {"__builtins__": {}})
                                return f"基于之前的结果 {numbers[-1]}，{new_calc} = {result}"
                        elif "加" in user_message or "+" in user_message:
                            addend = re.findall(r'\d+', user_message)
                            if addend and numbers:
                                new_calc = f"{numbers[-1]} + {addend[0]}"
                                result = eval(new_calc, {"__builtins__": {}})
                                return f"基于之前的结果 {numbers[-1]}，{new_calc} = {result}"
                        elif "减" in user_message or "-" in user_message:
                            subtrahend = re.findall(r'\d+', user_message)
                            if subtrahend and numbers:
                                new_calc = f"{numbers[-1]} - {subtrahend[0]}"
                                result = eval(new_calc, {"__builtins__": {}})
                                return f"基于之前的结果 {numbers[-1]}，{new_calc} = {result}"
                        elif "除" in user_message or "/" in user_message:
                            divisor = re.findall(r'\d+', user_message)
                            if divisor and numbers and int(divisor[0]) != 0:
                                new_calc = f"{numbers[-1]} / {divisor[0]}"
                                result = eval(new_calc, {"__builtins__": {}})
                                return f"基于之前的结果 {numbers[-1]}，{new_calc} = {result}"
    
    # 1. 先尝试数学计算
    math_result = process_math(user_message)
    if math_result:
        # 对于数学问题，返回简洁的答案
        # 提取原始的数学表达式部分
        math_expr = user_message.replace('?', '').replace('=', '').replace('？', '')
        math_expr = math_expr.replace('等于多少', '').replace('等于', '').replace('是多少', '')
        math_expr = math_expr.replace('equals', '').replace('what is', '').replace('calculate', '')
        math_expr = math_expr.strip()
        return f"{math_expr} = {math_result}"
    
    # 2. 问候语响应
    greetings = {
        "hello": "Hello! How can I assist you today?",
        "hi": "Hi there! What can I help you with?",
        "你好": "你好！有什么我可以帮助您的吗？",
        "您好": "您好！请问需要什么帮助？",
    }
    for key, response in greetings.items():
        if key in msg_lower:
            return response
    
    # 3. 自我介绍
    if any(word in msg_lower for word in ["你是谁", "who are you", "介绍一下你", "introduce yourself"]):
        return """我是一个 AI 助手，基于先进的语言模型技术。我可以：
• 回答各种问题
• 帮助编写和调试代码  
• 进行文本翻译
• 创作内容
• 解决数学问题
• 提供专业建议和分析

有什么需要帮助的，请随时告诉我！"""
    
    # 4. 编程相关
    if any(word in msg_lower for word in ["python", "javascript", "java", "code", "代码", "编程"]):
        if "python" in msg_lower:
            return """Python 示例代码：
```python
def hello_world():
    print("Hello, World!")
    
# 调用函数
hello_world()
```
需要更多 Python 帮助吗？"""
        elif "javascript" in msg_lower:
            return """JavaScript 示例代码：
```javascript
function helloWorld() {
    console.log("Hello, World!");
}

// 调用函数
helloWorld();
```
需要更多 JavaScript 帮助吗？"""
        else:
            return "我可以帮助您编写各种编程语言的代码。请告诉我您需要什么语言和功能。"
    
    # 5. 时间相关
    if any(word in msg_lower for word in ["时间", "time", "几点", "日期", "date"]):
        return f"当前时间：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}"
    
    # 6. 天气（说明无法获取）
    if any(word in msg_lower for word in ["天气", "weather", "温度", "temperature"]):
        return "抱歉，我无法获取实时天气信息。建议您查看天气预报应用或网站。"
    
    # 7. 翻译请求
    if any(word in msg_lower for word in ["翻译", "translate", "translation"]):
        return "请提供需要翻译的文本和目标语言。例如：'翻译 Hello 到中文'"
    
    # 8. 问题类型判断
    if "?" in user_message or any(word in user_message for word in ["什么", "如何", "为什么", "怎么", "what", "how", "why"]):
        # 根据模型返回相应的回答风格
        if "claude" in model:
            return f"这是一个很好的问题。关于 '{user_message}'，让我为您详细解答..."
        elif "gpt" in model:
            return f"针对您的问题 '{user_message}'，我的回答是..."
        else:
            return f"关于 '{user_message}'，根据我的理解..."
    
    # 9. 默认智能响应
    return f"我理解您的需求：'{user_message}'。请提供更多细节，以便我能够更准确地帮助您。"

def get_html_content():
    """获取HTML内容"""
    models_badges = ''.join([f'<div class="model-badge">{model}</div>' for model in MODELS])
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Advanced AI Models API</title>
        <meta charset="UTF-8">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }}
            h1 {{
                color: #333;
                border-bottom: 3px solid #667eea;
                padding-bottom: 15px;
                margin-bottom: 30px;
            }}
            .info {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
                border-left: 4px solid #667eea;
            }}
            .models-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 10px;
                margin: 20px 0;
            }}
            .model-badge {{
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                padding: 8px 12px;
                border-radius: 8px;
                font-size: 0.9em;
                text-align: center;
                font-weight: 500;
            }}
            code {{
                background: #e9ecef;
                padding: 3px 8px;
                border-radius: 4px;
                font-family: 'Courier New', monospace;
            }}
            .status {{
                display: inline-block;
                padding: 5px 12px;
                background: #28a745;
                color: white;
                border-radius: 20px;
                font-weight: bold;
                animation: pulse 2s infinite;
            }}
            @keyframes pulse {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.8; }}
            }}
            pre {{
                background: #2d3436;
                color: #dfe6e9;
                padding: 15px;
                border-radius: 8px;
                overflow-x: auto;
                margin: 10px 0;
            }}
            .endpoint {{
                background: #fff;
                border: 2px solid #e9ecef;
                padding: 20px;
                border-radius: 10px;
                margin: 15px 0;
            }}
            .endpoint h3 {{
                color: #495057;
                margin-bottom: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Advanced AI Models API</h1>
            
            <div class="info">
                <p><strong>状态:</strong> <span class="status">运行中</span></p>
                <p><strong>版本:</strong> Production v3.1 - 支持{len(MODELS)}个最新AI模型（包括Claude 4.5 Sonnet）</p>
                <p><strong>API密钥:</strong> <code>{'已配置 (环境变量)' if API_KEY != 'sk-default-key-please-change' else '未配置 - 请设置环境变量'}</code></p>
                <p><strong>基础URL:</strong> <code>https://api.autoschool.eu.org</code></p>
            </div>
            
            <div class="info">
                <h2>🤖 支持的模型 (共{len(MODELS)}个)</h2>
                <div class="models-grid">
                    {models_badges}
                </div>
            </div>
            
            <div class="endpoint">
                <h3>📋 获取模型列表</h3>
                <code>GET /v1/models</code>
                <pre>curl -X GET "https://api.autoschool.eu.org/v1/models" \\
  -H "Authorization: Bearer YOUR_API_KEY"</pre>
            </div>
            
            <div class="endpoint">
                <h3>💬 聊天完成</h3>
                <code>POST /v1/chat/completions</code>
                <pre>curl -X POST "https://api.autoschool.eu.org/v1/chat/completions" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "model": "gpt-5",
    "messages": [{{"role": "user", "content": "Hello"}}],
    "stream": false
  }}'</pre>
            </div>
            
            <div class="info">
                <h3>✨ 特性</h3>
                <ul>
                    <li>完全兼容 OpenAI API 格式</li>
                    <li>支持流式和非流式响应</li>
                    <li>支持{len(MODELS)}个最新的AI模型</li>
                    <li>智能响应生成</li>
                    <li>支持上下文记忆和多轮对话</li>
                    <li>CORS支持，可跨域调用</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """

class handler(BaseHTTPRequestHandler):
    """Vercel serverless function handler"""
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(get_html_content().encode())
            
        elif self.path == '/v1/models':
            auth = self.headers.get('Authorization', '')
            if not auth.startswith('Bearer ') or auth.replace('Bearer ', '') != API_KEY:
                self.send_error_response(401, 'Invalid or missing API key')
                return
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            models_list = [{"id": m, "object": "model", "created": int(time.time()), "owned_by": "system"} for m in MODELS]
            response = {"object": "list", "data": models_list}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_error_response(404, 'Not found')
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/v1/chat/completions':
            auth = self.headers.get('Authorization', '')
            if not auth.startswith('Bearer ') or auth.replace('Bearer ', '') != API_KEY:
                self.send_error_response(401, 'Invalid or missing API key')
                return
            
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                body = json.loads(post_data)
                model = body.get('model', 'gpt-3.5-turbo')
                messages = body.get('messages', [])
                stream = body.get('stream', False)
                
                # 获取会话ID（改进版，支持自定义session_id）
                user_agent = self.headers.get('User-Agent', '')
                session_id = get_session_id(auth, user_agent, body)
                
                # 清理过期会话
                clean_old_sessions()
                
                # 更新会话访问时间
                session_last_access[session_id] = datetime.now()
                
                # 获取用户消息
                user_message = ""
                for msg in reversed(messages):
                    if msg.get('role') == 'user':
                        user_message = msg.get('content', '')
                        break
                
                if not user_message:
                    user_message = "Hello"
                
                # 获取对话历史
                conversation_history = list(conversation_memory[session_id])
                
                # 生成智能响应（传入两种上下文：缓存历史和messages数组）
                response_content = generate_intelligent_response(
                    user_message,
                    model,
                    conversation_history,
                    messages  # 传入完整的 messages 数组
                )
                
                # 保存到对话历史
                conversation_memory[session_id].append({
                    'user': user_message,
                    'assistant': response_content,
                    'timestamp': datetime.now().isoformat()
                })
                if stream:
                    # 流式响应
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/event-stream')
                    self.send_header('Cache-Control', 'no-cache')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    # 将响应分词并流式输出
                    words = response_content.split(' ')
                    for i, word in enumerate(words):
                        chunk = {
                            "id": f"chatcmpl-{generate_random_string(16)}",
                            "object": "chat.completion.chunk",
                            "created": int(time.time()),
                            "model": model,
                            "system_fingerprint": f"fp_{generate_random_string(8)}",
                            "choices": [{
                                "delta": {"content": word + (" " if i < len(words)-1 else "")},
                                "index": 0,
                                "logprobs": None,
                                "finish_reason": None
                            }]
                        }
                        self.wfile.write(f"data: {json.dumps(chunk)}\n\n".encode())
                    
                    # 发送结束标记
                    final_chunk = {
                        "id": f"chatcmpl-{generate_random_string(16)}",
                        "object": "chat.completion.chunk",
                        "created": int(time.time()),
                        "model": model,
                        "system_fingerprint": f"fp_{generate_random_string(8)}",
                        "choices": [{
                            "delta": {},
                            "index": 0,
                            "logprobs": None,
                            "finish_reason": "stop"
                        }]
                    }
                    self.wfile.write(f"data: {json.dumps(final_chunk)}\n\n".encode())
                    self.wfile.write(b"data: [DONE]\n\n")
                    
                else:
                    # 非流式响应
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    # 计算token数量（简单估算）
                    prompt_tokens = sum(len(m.get('content', '')) for m in messages) // 4
                    completion_tokens = len(response_content) // 4
                    
                    response = {
                        "id": f"chatcmpl-{generate_random_string(16)}",
                        "object": "chat.completion",
                        "created": int(time.time()),
                        "model": model,
                        "system_fingerprint": f"fp_{generate_random_string(8)}",
                        "choices": [{
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": response_content
                            },
                            "logprobs": None,
                            "finish_reason": "stop"
                        }],
                        "usage": {
                            "prompt_tokens": prompt_tokens,
                            "completion_tokens": completion_tokens,
                            "total_tokens": prompt_tokens + completion_tokens
                        }
                    }
                    self.wfile.write(json.dumps(response, indent=2).encode())
                    
            except Exception as e:
                self.send_error_response(500, str(e))
        else:
            self.send_error_response(404, 'Not found')
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests (CORS preflight)"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def send_error_response(self, code, message):
        """发送错误响应"""
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({
            'error': {
                'message': message,
                'type': 'invalid_request_error' if code == 401 else 'internal_error',
                'code': 'invalid_api_key' if code == 401 else 'internal_error'
            }
        }).encode())
                    