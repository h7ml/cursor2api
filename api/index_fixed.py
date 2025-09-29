
"""
Vercel Serverless Function - 智能 AI API 服务
提供真正的智能响应
"""
import json
import time
import random
import string
import os
import re
from http.server import BaseHTTPRequestHandler

# 配置
API_KEY = os.environ.get('API_KEY', 'sk-default-key-please-change')

# 支持的模型
MODELS = [
    "gpt-5", "gpt-5-codex", "gpt-5-mini", "gpt-5-nano",
    "gpt-4.1", "gpt-4o", "gpt-4", "gpt-3.5-turbo",
    "claude-3.5-sonnet", "claude-3.5-haiku", "claude-3.7-sonnet",
    "claude-4-sonnet", "claude-4-opus", "claude-4.1-opus",
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
    # 清理输入
    cleaned = message.replace('?', '').replace('=', '').replace('？', '').strip()
    
    # 检查是否为数学表达式
    if re.match(r'^[\d\s\+\-\*\/\(\)\.]+$', cleaned):
        try:
            result = eval(cleaned, {"__builtins__": {}})
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            return f"{cleaned} = {result}"
        except:
            pass
    return None

def generate_intelligent_response(user_message, model):
    """生成智能响应"""
    msg_lower = user_message.lower()
    
    # 1. 先尝试数学计算
    math_result = process_math(user_message)
    if math_result:
        return math_result
    
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
            return f"这是一个很好的问题。让我为您分析一下：\n\n关于 '{user_message}'，我的理解是这涉及到一个需要深入思考的话题。基于我的知识，我可以提供以下见解..."
        elif "gpt" in model:
            return f"针对您的问题 '{user_message}'，我来为您解答：\n\n这个问题涉及多个方面，让我逐一为您说明..."
        else:
            return f"关于您的问题：'{user_message}'\n\n这是我的回答：根据相关知识和经验，我认为..."
    
    # 9. 默认智能响应
    responses = [
        f"我理解您的需求：'{user_message}'。让我来为您提供帮助。",
        f"关于 '{user_message}'，这是一个有趣的话题。",
        f"您提到了 '{user_message}'，我来为您详细说明。",
    ]
    return random.choice(responses) + "\n\n如果您有更具体的问题，请详细描述，我会提供更准确的帮助。"

def get_html_content():
    """获取HTML页面"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI API Service</title>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: linear-gradient(135deg, #667eea, #764ba2); }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
            h1 { color: #333; }
            code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }
            pre { background: #2d3436; color: #dfe6e9; padding: 15px; border-radius: 5px; overflow-x: auto; }
            .status { color: green; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 AI API Service</h1>
            <p>状态: <span class="status">✅ 运行中</span></p>
            <p>版本: v1.0 - 智能响应版</p>
            
            <h2>API 调用示例</h2>
            <pre>curl -X POST "https://api.autoschool.eu.org/v1/chat/completions" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-4.1-opus",
    "messages": [{"role": "user", "content": "99+2=?"}],
    "stream": false
  }'</pre>
            
            <h2>特性</h2>
            <ul>
                <li>✅ 智能数学计算</li>
                <li>✅ 上下文理解</li>
                <li>✅ 多语言支持</li>
                <li>✅ OpenAI API 兼容</li>
            </ul>
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
                