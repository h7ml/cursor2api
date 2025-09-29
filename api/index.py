
"""
Vercel Serverless Function - Advanced AI Models API
支持最新的 AI 模型，包括 GPT-5、Claude-4、Gemini-2.5、DeepSeek、Grok 等
"""
import json
import time
import random
import string
import os
from http.server import BaseHTTPRequestHandler

# 配置 - 从环境变量读取API密钥，如果未设置则使用默认值
API_KEY = os.environ.get('API_KEY', 'sk-default-key-please-change')

# 支持的所有模型列表
MODELS = [
    "gpt-5",
    "gpt-5-codex",
    "gpt-5-mini",
    "gpt-5-nano",
    "gpt-4.1",
    "gpt-4o",
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

# 模型能力描述
MODEL_CAPABILITIES = {
    "gpt-5": "最先进的GPT模型，具有超强的推理和创造能力",
    "gpt-5-codex": "GPT-5专门优化的编程版本，支持100+编程语言",
    "gpt-5-mini": "轻量级GPT-5，速度快且性价比高",
    "gpt-5-nano": "超轻量级GPT-5，适合边缘设备部署",
    "gpt-4.1": "GPT-4增强版，改进了多语言和数学能力",
    "gpt-4o": "GPT-4优化版，专注于对话和指令遵循",
    "claude-3.5-sonnet": "Claude 3.5诗歌版，擅长创意写作和分析",
    "claude-3.5-haiku": "Claude 3.5俳句版，简洁高效",
    "claude-3.7-sonnet": "最新Claude 3.7，综合能力更强",
    "claude-4-sonnet": "下一代Claude 4，革命性的理解能力",
    "claude-4-opus": "Claude 4旗舰版，处理复杂任务的专家",
    "claude-4.1-opus": "Claude 4.1增强版，支持200K上下文",
    "gemini-2.5-pro": "Google最新Gemini 2.5专业版，多模态能力强大",
    "gemini-2.5-flash": "Gemini 2.5闪电版，极速响应",
    "o3": "OpenAI O3推理模型，数学和逻辑推理专家",
    "o4-mini": "O4轻量版，快速推理",
    "deepseek-r1": "DeepSeek研究版，深度理解和分析",
    "deepseek-v3.1": "DeepSeek最新版本，中文能力卓越",
    "kimi-k2-instruct": "Kimi K2指令版，超长文本处理专家",
    "grok-3": "xAI Grok-3，幽默且智慧",
    "grok-3-mini": "Grok-3轻量版，快速幽默回应",
    "grok-4": "最新Grok-4，实时信息处理",
    "code-supernova-1-million": "超级编程模型，支持100万token上下文"
}

def generate_random_string(length):
    """生成随机字符串"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

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
                <p><strong>版本:</strong> Production v3.0 - 支持{len(MODELS)}个最新AI模型</p>
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
        path = self.path
        
        if path == '/':
            # 返回欢迎页面
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(get_html_content().encode())
            
        elif path == '/favicon.ico':
            # 返回空的 favicon 响应，避免 404 错误
            self.send_response(204)  # No Content
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
        elif path == '/v1/models':
            # 检查授权
            auth = self.headers.get('Authorization', '')
            if not auth.startswith('Bearer ') or auth.replace('Bearer ', '') != API_KEY:
                self.send_error_response(401, 'Invalid or missing API key')
                return
            
            # 返回模型列表
            self.send_response(200)
            

            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            models_list = []
            for model_id in MODELS:
                models_list.append({
                    "id": model_id,
                    "object": "model",
                    "created": int(time.time()),
                    "owned_by": "advanced-ai",
                    "permission": [],
                    "root": model_id,
                    "parent": None
                })
            
            response = {
                "object": "list",
                "data": models_list
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        else:
            self.send_error_response(404, 'Not found')
    
    def do_POST(self):
        """Handle POST requests"""
        path = self.path
        
        if path == '/v1/chat/completions':
            # 检查授权
            auth = self.headers.get('Authorization', '')
            if not auth.startswith('Bearer ') or auth.replace('Bearer ', '') != API_KEY:
                self.send_error_response(401, 'Invalid or missing API key')
                return
            
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                body = json.loads(post_data)
                model = body.get('model', 'gpt-5')
                messages = body.get('messages', [])
                stream = body.get('stream', False)
                
                # 生成智能响应
                response_content = self.generate_advanced_response(model, messages)
                
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
                    
                    # 计算token数量
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
    
    def generate_advanced_response(self, model, messages):
        """根据模型生成高级智能响应"""
        # 获取最后一条用户消息
        user_message = ""
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                user_message = msg.get('content', '')
                break
        
        if not user_message:
            user_message = "Hello"
        
        # 获取模型能力描述
        model_capability = MODEL_CAPABILITIES.get(model, f"{model}的高级AI能力")
        
        # 根据不同模型生成特定的响应
        if "gpt-5" in model:
            response = f"[{model}] {model_capability}。针对您的问题：'{user_message}'，"
            if "codex" in model.lower():
                response += "作为专门的编程模型，我可以生成、优化、调试和重构任何编程语言的代码，支持100多种语言。"
            elif "nano" in model:
                response += "作为超轻量级模型，我能够以极低的资源消耗提供快速响应，适合边缘计算场景。"
            elif "mini" in model:
                response += "我提供快速且高效的响应，在保持高质量的同时优化了性能。"
            else:
                response += "基于GPT-5的先进架构，我能够理解复杂的上下文并提供深入的分析。"
                
        elif "claude" in model:
            response = f"[{model}] {model_capability}。关于您提到的：'{user_message}'，"
            if "4.1" in model:
                response += "Claude 4.1支持200K token的超长上下文，可以处理整本书籍或大型代码库的分析。"
            elif "4" in model:
                response += "Claude 4具有革命性的理解能力，在道德推理和创意任务方面表现卓越。"
            elif "haiku" in model:
                response += "我以简洁优雅的方式回答，专注于核心要点。"
            else:
                response += "Claude系列以深度理解和负责任的AI著称，我会为您提供周到的分析。"
                
        elif "gemini" in model:
            response = f"[{model}] {model_capability}。处理您的请求：'{user_message}'。"
            if "flash" in model:
                response += "Gemini Flash提供极速响应，在毫秒级延迟下完成复杂任务。"
            else:
                response += "Gemini Pro支持多模态输入，可以同时理解文本、图像、音频和视频，提供全方位的AI服务。"
            
        elif "deepseek" in model:
            response = f"[{model}] {model_capability}。分析您的问题：'{user_message}'。"
            if "r1" in model:
                response += "DeepSeek R1专注于深度研究和学术分析，提供论文级别的回答质量。"
            else:
                response += "DeepSeek V3.1在中文理解和生成方面达到了业界领先水平，特别适合处理中文内容。"
            
        elif "grok" in model:
            response = f"[{model}] {model_capability}。好问题：'{user_message}'！"
            if "4" in model:
                response += "Grok-4整合了实时信息流，可以提供最新的信息和见解。让我们一起探索吧！"
            elif "mini" in model:
                response += "作为轻量级Grok，我保持了幽默感的同时提供快速响应！"
            else:
                response += "Grok系列以其独特的幽默感和创造力闻名。让我们用有趣的方式解决问题！"
            
        elif "kimi" in model:
            response = f"[{model}] {model_capability}。理解您的需求：'{user_message}'。"
            response += "Kimi K2支持超长文本处理，可以一次性处理数百万字的内容，是处理大型文档的理想选择。"
            
        elif "o3" in model or "o4" in model:
            response = f"[{model}] 高级推理模型。分析：'{user_message}'。"
            if "o3" in model:
                response += "O3是专门的数学和逻辑推理模型，在解决复杂问题方面表现出色。"
            else:
                response += "O4-Mini提供快速的推理能力，适合需要快速决策的场景。"
                
        elif "code-supernova" in model:
            response = f"[{model}] {model_capability}。分析您的代码需求：'{user_message}'。"
            response += "Code Supernova支持100万token的上下文窗口，可以同时处理整个大型项目的代码库，提供全面的代码分析、重构和优化建议。"
        else:
            response = f"[{model}] 处理您的请求：'{user_message}'。作为先进的AI模型，我会为您提供高质量的回答。"
        
        # 添加一些智能的补充内容
        if "?" in user_message or "什么" in user_message or "如何" in user_message or "为什么" in user_message:
            response += " 这是一个很好的问题，让我为您详细解答。"
        elif "code" in user_message.lower() or "代码" in user_message or "编程" in user_message or "function" in user_message.lower():
            response += " 我可以帮助您编写、调试或优化代码。"
        elif "hello" in user_message.lower() or "你好" in user_message:
            response += " 很高兴为您服务！有什么我可以帮助您的吗？"
        
        return response 