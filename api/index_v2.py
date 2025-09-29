
"""
Vercel Serverless Function - AI API Proxy Service
支持多个 AI 服务提供商的统一接口
"""
import json
import time
import random
import string
import os
import requests
from http.server import BaseHTTPRequestHandler
from typing import Dict, List, Any, Optional

# 配置 - 从环境变量读取
API_KEY = os.environ.get('API_KEY', 'sk-default-key-please-change')

# AI 服务提供商的 API 密钥（从环境变量读取）
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', '')
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
MOONSHOT_API_KEY = os.environ.get('MOONSHOT_API_KEY', '')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')

# 模型映射配置
MODEL_MAPPINGS = {
    # OpenAI 模型
    "gpt-4": {"provider": "openai", "model": "gpt-4"},
    "gpt-4-turbo": {"provider": "openai", "model": "gpt-4-turbo-preview"},
    "gpt-4o": {"provider": "openai", "model": "gpt-4o"},
    "gpt-3.5-turbo": {"provider": "openai", "model": "gpt-3.5-turbo"},
    "gpt-4-32k": {"provider": "openai", "model": "gpt-4-32k"},
    
    # Anthropic Claude 模型
    "claude-3-opus": {"provider": "anthropic", "model": "claude-3-opus-20240229"},
    "claude-3-sonnet": {"provider": "anthropic", "model": "claude-3-sonnet-20240229"},
    "claude-3-haiku": {"provider": "anthropic", "model": "claude-3-haiku-20240307"},
    "claude-3.5-sonnet": {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"},
    "claude-2.1": {"provider": "anthropic", "model": "claude-2.1"},
    
    # DeepSeek 模型
    "deepseek-chat": {"provider": "deepseek", "model": "deepseek-chat"},
    "deepseek-coder": {"provider": "deepseek", "model": "deepseek-coder"},
    
    # Moonshot/Kimi 模型
    "moonshot-v1-8k": {"provider": "moonshot", "model": "moonshot-v1-8k"},
    "moonshot-v1-32k": {"provider": "moonshot", "model": "moonshot-v1-32k"},
    "moonshot-v1-128k": {"provider": "moonshot", "model": "moonshot-v1-128k"},
    
    # Groq 模型（开源模型，速度快）
    "llama3-70b": {"provider": "groq", "model": "llama3-70b-8192"},
    "llama3-8b": {"provider": "groq", "model": "llama3-8b-8192"},
    "mixtral-8x7b": {"provider": "groq", "model": "mixtral-8x7b-32768"},
    "gemma-7b": {"provider": "groq", "model": "gemma-7b-it"},
    
    # 默认模型（使用 Groq 的免费模型）
    "default": {"provider": "groq", "model": "llama3-8b-8192"},
}

# API 端点配置
API_ENDPOINTS = {
    "openai": "https://api.openai.com/v1/chat/completions",
    "anthropic": "https://api.anthropic.com/v1/messages",
    "deepseek": "https://api.deepseek.com/v1/chat/completions",
    "moonshot": "https://api.moonshot.cn/v1/chat/completions",
    "groq": "https://api.groq.com/openai/v1/chat/completions",
}

def generate_random_string(length):
    """生成随机字符串"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

class AIProvider:
    """AI 服务提供商基类"""
    
    @staticmethod
    def call_api(messages: List[Dict], model: str, stream: bool = False, **kwargs) -> Dict:
        """统一的 API 调用接口"""
        # 获取模型配置
        model_config = MODEL_MAPPINGS.get(model, MODEL_MAPPINGS["default"])
        provider = model_config["provider"]
        actual_model = model_config["model"]
        
        # 根据提供商调用相应的 API
        if provider == "openai":
            return AIProvider.call_openai(messages, actual_model, stream, **kwargs)
        elif provider == "anthropic":
            return AIProvider.call_anthropic(messages, actual_model, stream, **kwargs)
        elif provider == "deepseek":
            return AIProvider.call_deepseek(messages, actual_model, stream, **kwargs)
        elif provider == "moonshot":
            return AIProvider.call_moonshot(messages, actual_model, stream, **kwargs)
        elif provider == "groq":
            return AIProvider.call_groq(messages, actual_model, stream, **kwargs)
        else:
            return AIProvider.generate_fallback_response(messages, model)
    
    @staticmethod
    def call_openai(messages: List[Dict], model: str, stream: bool = False, **kwargs) -> Dict:
        """调用 OpenAI API"""
        if not OPENAI_API_KEY:
            return None
        
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": messages,
            "stream": stream,
            **kwargs
        }
        
        try:
            response = requests.post(
                API_ENDPOINTS["openai"],
                headers=headers,
                json=data,
                timeout=30,
                stream=stream
            )
            
            if response.status_code == 200:
                if stream:
                    return {"stream": response}
                else:
                    return response.json()
        except Exception as e:
            print(f"OpenAI API error: {e}")
        return None
    
    @staticmethod
    def call_anthropic(messages: List[Dict], model: str, stream: bool = False, **kwargs) -> Dict:
        """调用 Anthropic Claude API"""
        if not ANTHROPIC_API_KEY:
            return None
        
        headers = {
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        # 转换消息格式
        system_message = ""
        claude_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                claude_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        data = {
            "model": model,
            "messages": claude_messages,
            "max_tokens": kwargs.get("max_tokens", 1000),
            "stream": stream
        }
        
        if system_message:
            data["system"] = system_message
        
        try:
            response = requests.post(
                API_ENDPOINTS["anthropic"],
                headers=headers,
                json=data,
                timeout=30,
                stream=stream
            )
            
            if response.status_code == 200:
                if stream:
                    return {"stream": response}
                else:
                    claude_response = response.json()
                    return AIProvider.convert_anthropic_to_openai(claude_response, model)
        except Exception as e:
            print(f"Anthropic API error: {e}")
        return None
    
    @staticmethod
    def call_deepseek(messages: List[Dict], model: str, stream: bool = False, **kwargs) -> Dict:
        """调用 DeepSeek API"""
        if not DEEPSEEK_API_KEY:
            return None
        
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": messages,
            "stream": stream,
            **kwargs
        }
        
        try:
            response = requests.post(
                API_ENDPOINTS["deepseek"],
                headers=headers,
                json=data,
                timeout=30,
                stream=stream
            )
            
            if response.status_code == 200:
                if stream:
                    return {"stream": response}
                else:
                    return response.json()
        except Exception as e:
            print(f"DeepSeek API error: {e}")
        return None
    
    @staticmethod
    def call_moonshot(messages: List[Dict], model: str, stream: bool = False, **kwargs) -> Dict:
        """调用 Moonshot/Kimi API"""
        if not MOONSHOT_API_KEY:
            return None
        
        headers = {
            "Authorization": f"Bearer {MOONSHOT_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": messages,
            "stream": stream,
            **kwargs
        }
        
        try:
            response = requests.post(
                API_ENDPOINTS["moonshot"],
                headers=headers,
                json=data,
                timeout=30,
                stream=stream
            )
            
            if response.status_code == 200:
                if stream:
                    return {"stream": response}
                else:
                    return response.json()
        except Exception as e:
            print(f"Moonshot API error: {e}")
        return None
    
    @staticmethod
    def call_groq(messages: List[Dict], model: str, stream: bool = False, **kwargs) -> Dict:
        """调用 Groq API（开源模型，速度快）"""
        if not GROQ_API_KEY:
            # Groq 提供免费试用，可以使用默认密钥
            return None
        
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": messages,
            "stream": stream,
            **kwargs
        }
        
        try:
            response = requests.post(
                API_ENDPOINTS["groq"],
                headers=headers,
                json=data,
                timeout=30,
                stream=stream
            )
            
            if response.status_code == 200:
                if stream:
                    return {"stream": response}
                else:
                    return response.json()
        except Exception as e:
            print(f"Groq API error: {e}")
        return None
    
    @staticmethod
    def convert_anthropic_to_openai(claude_response: Dict, model: str) -> Dict:
        """将 Anthropic 响应格式转换为 OpenAI 格式"""
        content = claude_response.get("content", [{}])[0].get("text", "")
        
        return {
            "id": f"chatcmpl-{generate_random_string(16)}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": content
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": claude_response.get("usage", {}).get("input_tokens", 0),
                "completion_tokens": claude_response.get("usage", {}).get("output_tokens", 0),
                "total_tokens": claude_response.get("usage", {}).get("input_tokens", 0) + 
                               claude_response.get("usage", {}).get("output_tokens", 0)
            }
        }
    
    @staticmethod
    def generate_fallback_response(messages: List[Dict], model: str) -> Dict:
        """生成降级响应"""
        user_message = ""
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                user_message = msg.get('content', '')
                break
        
        response = f"抱歉，当前没有可用的 AI 服务。请检查 API 