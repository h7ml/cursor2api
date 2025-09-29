
"""
Vercel Serverless Function - 改进的 AI API 服务
使用多种 AI 服务提供真正的智能响应
"""
import json
import time
import random
import string
import os
import requests
from http.server import BaseHTTPRequestHandler

# 配置 - 从环境变量读取API密钥
API_KEY = os.environ.get('API_KEY', 'sk-default-key-please-change')

# 使用免费或易获取的 AI 服务
# 1. HuggingFace Inference API (免费，有限额)
HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY', '')

# 2. Cohere API (有免费额度)
COHERE_API_KEY = os.environ.get('COHERE_API_KEY', '')

# 3. Together AI (有免费试用)
TOGETHER_API_KEY = os.environ.get('TOGETHER_API_KEY', '')

# 4. DeepInfra (有免费额度)
DEEPINFRA_API_KEY = os.environ.get('DEEPINFRA_API_KEY', '')

# 5. 使用第三方代理服务
PROXY_URL = os.environ.get('PROXY_URL', '')  # 如: https://api.openai-proxy.com
PROXY_API_KEY = os.environ.get('PROXY_API_KEY', '')

# 支持的模型列表
SUPPORTED_MODELS = [
    "gpt-3.5-turbo",
    "gpt-4",
    "gpt-4o",
    "claude-3-opus",
    "claude-3-sonnet",
    "claude-3-haiku",
    "claude-3.5-sonnet",
    "claude-4-opus",
    "claude-4.1-opus",
    "llama-2-70b",
    "llama-3-70b",
    "mixtral-8x7b",
    "deepseek-chat",
    "qwen-72b",
    "yi-34b",
]

def generate_random_string(length):
    """生成随机字符串"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def get_html_content():
    """获取欢迎页面HTML内容"""
    models_badges = ''.join([f'<div class="model-badge">{model}</div>' for model in SUPPORTED_MODELS])
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI API Proxy Service</title>
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
            .status {{
                display: inline-block;
                padding: 5px 12px;
                background: #28a745;
                color: white;
                border-radius: 20px;
                font-weight: bold;
            }}
            code {{
                background: #e9ecef;
                padding: 3px 8px;
                border-radius: 4px;
                font-family: 'Courier New', monospace;
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
            <h1>🚀 AI API Proxy Service</h1>
            
            <div class="info">
                <p><strong>状态:</strong> <span class="status">运行中</span></p>
                <p><strong>版本:</strong> v2.0 - 真实 AI 响应</p>
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
                <h3>📡 API 使用示例</h3>
                <pre>curl -X POST "https://api.autoschool.eu.org/v1/chat/completions" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "model": "claude-3.5-sonnet",
    "messages": [{{"role": "user", "content": "99+2=?"}}],
    "stream": false
  }}'</pre>
            </div>
            
            <div class="info">
                <h3>✨ 特性</h3>
                <ul>
                    <li>✅ 真实 AI 响应（不是模板）</li>
                    <li>✅ 支持多个 AI 提供商</li>
                    <li>✅ OpenAI API 格式兼容</li>
                    <li>✅ 支持流式和非流式响应</li>
                    <li>✅ 智能降级和负载均衡</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """

class AIService:
    """AI 服务调用类"""
    
    @staticmethod
    def call_huggingface(messages, model):
        """调用 HuggingFace Inference API"""
        if not HUGGINGFACE_API_KEY:
            return None
        
        # 使用 HuggingFace 的开源模型
        hf_models = {
            "llama-2-70b": "meta-llama/Llama-2-70b-chat-hf",
            "mixtral-8x7b": "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "default": "microsoft/DialoGPT-medium"
        }
        
        hf_model = hf_models.get(model, hf_models["default"])
        
        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # 构造输入
        user_message = ""
        for msg in messages:
            if msg["role"] == "user":
                user_message = msg["content"]
        
        data = {
            "inputs": user_message,
            "parameters": {
                "max_new_tokens": 200,
                "temperature": 0.7,
                "top_p": 0.95
            }
        }
        
        try:
            response = requests.post(
                f"https://api-inference.huggingface.co/models/{hf_model}",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "")
                return str(result)
        except Exception as e:
            print(f"HuggingFace API error: {e}")
        
        return None
    
    @staticmethod
    def call_together_ai(messages, model):
        """调用 Together AI"""
        if not TOGETHER_API_KEY:
            return None
        
        # Together AI 模型映射
        together_models = {
            "llama-2-70b": "meta-llama/Llama-2-70b-chat-hf",
            "llama-3-70b": "meta-llama/Meta-Llama-3-70B-Instruct",
            "mixtral-8x7b": "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "qwen-72b": "Qwen/Qwen1.5-72B-Chat",
            "yi-34b": "zero-one-ai/Yi-34B-Chat",
            "default": "meta-llama/Llama-2-7b-chat-hf"
        }
        
        actual_model = together_models.get(model, together_models["default"])
        
        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": actual_model,
            "messages": messages,
            "max_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.7,
            "top_k": 50,
            "stream": False
        }
        
        try:
            response = requests.post(
                "https://api.together.xyz/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result
        except Exception as e:
            print(f"Together AI error: {e}")
        
        return None
    
    @staticmethod
    def call_deepinfra(messages, model):
        """调用 DeepInfra API"""
        if not DEEPINFRA_API_KEY:
            return None
        
        # DeepInfra 模型映射
        deepinfra_models = {
            "llama-2-70b": "meta-llama/Llama-2-70b-chat-hf",
            "mixtral-8x7b": "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "qwen-72b": "Qwen/Qwen2-72B-Instruct",
            "yi-34b": "01-ai/Yi-34B-Chat",
            "default": "meta-llama/Llama-2-7b-chat-hf"
        }
        
        actual_model = deepinfra_models.get(model, deepinfra_models["default"])
        
        headers = 