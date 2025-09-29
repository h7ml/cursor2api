
"""
Vercel Serverless Function - 改进的 AI API 服务
提供真正的智能响应，而不是模板化的回复
"""
import json
import time
import random
import string
import os
import re
import requests
from http.server import BaseHTTPRequestHandler

# 配置 - 从环境变量读取API密钥
API_KEY = os.environ.get('API_KEY', 'sk-default-key-please-change')

# 外部 AI 服务配置（可选）
EXTERNAL_AI_URL = os.environ.get('EXTERNAL_AI_URL', '')  # 例如: https://api.openai.com
EXTERNAL_AI_KEY = os.environ.get('EXTERNAL_AI_KEY', '')  # 真实的 API 密钥

# 支持的所有模型列表
MODELS = [
    "gpt-5",
    "gpt-5-codex",
    "gpt-5-mini",
    "gpt-5-nano",
    "gpt-4.1",
    "gpt-4o",
    "gpt-4",
    "gpt-3.5-turbo",
    "claude-3.5-sonnet",
    "claude-3.5-haiku",
    "claude-3.7-sonnet",
    "claude-4-sonnet",
    "claude-4-opus",
    "claude-4.1-opus",
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "o3",
    "o4-mini",
    "deepseek-r1",
    "deepseek-v3.1",
    "kimi-k2-instruct",
    "grok-3",
    "grok-3-mini",
    "grok-4",
    "code-supernova-1-million"
]

def generate_random_string(length):
    """生成随机字符串"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def get_html_content():
    """获取HTML欢迎页面"""
    models_badges = ''.join([f'<div class="model-badge">{model}</div>' for model in MODELS])
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Models API Service</title>
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
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 AI Models API Service</h1>
            
            <div class="info">
                <p><strong>状态:</strong> <span class="status">运行中</span></p>
                <p><strong>版本:</strong> v3.0 - 智能响应版</p>
                <p><strong>基础URL:</strong> <code>https://api.autoschool.eu.org</code></p>
                <p><strong>API密钥:</strong> <code>{'已配置' if API_KEY != 'sk-default-key-please-change' else '需要配置'}</code></p>
            </div>
            
            <div class="info">
                <h2>🤖 支持的模型</h2>
                <div class="models-grid">
                    {models_badges}
                </div>
            </div>
            
            <div class="info">
                <h3>📡 API 调用示例</h3>
                <pre>curl -X POST "https://api.autoschool.eu.org/v1/chat/completions" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "model": "claude-4.1-opus",
    "messages": [{{"role": "user", "content": "99+2=?"}}],
    "stream": false
  }}'

# 响应示例：
{{
  "choices": [{{
    "message": {{
      "content": "99 + 2 = 101"
    }}
  }}]
}}</pre>
            </div>
        </div>
    </body>
    </html>
    """

class IntelligentResponder:
    """智能响应生成器"""
    
    @staticmethod
    def process_math_expression(message):
        """处理数学表达式"""
        # 清理消息，移除问号和等号
        cleaned = message.replace('?', '').replace('=', '').replace('？', '').strip()
        
        # 检查是否是数学表达式
        if re.match(r'^[\d\s\+\-\*\/\(\)\.]+$', cleaned):
            try:
                # 安全评估数学表达式
                result = eval(cleaned, {"__builtins__": {}})
                return f"{cleaned} = {result}"
            except:
                pass
        return None
    
    @staticmethod
    def get_contextual_response(message, model):
        """生成上下文相关的响应"""
        msg_lower = message.lower()
        
        # 常见问答库
        qa_responses = {
            # 问候语
            "hello": "Hello! How can I assist you today?",
            "hi": "Hi there! What can I help you with?",
            "你好": "你好！有什么我可以帮助您的吗？",
            "您好": "您好！请问需要什么帮助？",
            
            # 自我介绍
            "你是谁": "我是一个 AI 助手，可以帮助您回答问题、解决问题、编写代码等。",
            "who are you": "I'm an AI assistant that can help you with various tasks including answering questions, solving problems, and writing code.",
            "介绍一下你自己": "我是基于大语言模型的 AI 助手，具备自然语言理解和生成能力。我可以协助您进行对话、回答问题、编程辅助、文本创作等多种任务。",
            
            # 能力相关
            "你能做什么": "我可以：\n1. 回答各种问题\n2. 帮助编写和调试代码\n3. 翻译文本\n4. 创作内容\n5. 解决数学问题\n6. 提供建议和分析",
            "what can you do": "I can:\n1. Answer questions\n2. Help with coding\n3. Translate text\n4. Create content\n5. Solve math problems\n6. Provide advice and analysis",
            
            # 时间相关
            "现在几点": f"当前时间是：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}",
            "what time": f"Current time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}",
            "今天几号": f"今天是：{time.strftime('%Y年%m月%d日', time.localtime())}",
        }
        
        # 检查精确匹配
        for key, response in qa_responses.items():
            if key in msg_lower:
                return response
        
        # 处理编程相关问题
        if any(word in msg_lower for word in ['python', 'javascript', 'java', 'code', '代码', '编程', 'function', '函数']):
            code_examples = {
                "python": "```python\n# Python 示例\ndef hello_world():\n    print('Hello, World!')\n\nhello_world()\n```",
                "javascript": "```javascript\n// JavaScript 示例\nfunction helloWorld() {\n    console.log('Hello, World!');\n}\n\nhelloWorld();\n```",
                "java": "```java\n// Java 示例\npublic class HelloWorld {\n    public static void main(String[] args) {\n        System.out.println('Hello, World!');\n    }\n}\n```",
            }
            
            for lang, code in code_examples.items():
                if lang in msg_lower:
                    return f"这是一个 {lang.capitalize()} 的示例：\n\n{code}"
            
            return "我可以帮助您编写代码。请告诉我您需要什么编程语言和具体功能。"
        
        # 处理翻译请求
        if any(word in msg_lower for word in ['translate', '翻译', 