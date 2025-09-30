#!/usr/bin/env python3
"""
测试所有支持的模型
"""
import requests
import json
import time
import os
import sys

# API配置 - 从环境变量读取，或使用默认值
API_URL = os.getenv("API_URL", "http://127.0.0.1:8001")
API_KEY = os.getenv("API_KEY", "your-secure-api-key-here")

# 检查 API 密钥
if not API_KEY or API_KEY == "your-api-key-here":
    print("❌ 错误：请设置环境变量 API_KEY")
    print("   例如：export API_KEY=your-actual-api-key")
    sys.exit(1)

# 所有支持的模型
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

def test_models_endpoint():
    """测试模型列表端点"""
    print("=" * 60)
    print("测试 /v1/models 端点")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    
    try:
        response = requests.get(f"{API_URL}/v1/models", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 成功获取模型列表")
            print(f"📊 模型数量: {len(data['data'])}")
            print(f"📋 前5个模型:")
            for model in data['data'][:5]:
                print(f"   - {model['id']}")
            print(f"   ... 共 {len(data['data'])} 个模型")
            return True
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_chat_completion(model_name, test_message):
    """测试单个模型的聊天完成"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": test_message}
        ],
        "stream": False,
        "max_tokens": 100
    }
    
    try:
        response = requests.post(
            f"{API_URL}/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            # 截取前100个字符
            preview = content[:100] + "..." if len(content) > 100 else content
            print(f"✅ {model_name:30} | 响应: {preview}")
            return True
        else:
            print(f"❌ {model_name:30} | 错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {model_name:30} | 异常: {str(e)[:50]}")
        return False

def test_all_models():
    """测试所有模型"""
    print("\n" + "=" * 60)
    print("测试所有模型的聊天完成功能")
    print("=" * 60)
    
    success_count = 0
    failed_count = 0
    
    # 测试不同类型的消息
    test_messages = [
        "Hello, what model are you?",
        "写一段Python代码",
        "Explain quantum computing",
    ]
    
    for i, model in enumerate(MODELS, 1):
        # 使用轮换的测试消息
        test_msg = test_messages[i % len(test_messages)]
        print(f"\n[{i}/{len(MODELS)}] 测试模型: {model}")
        
        if test_chat_completion(model, test_msg):
            success_count += 1
        else:
            failed_count += 1
        
        # 避免请求过快
        time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print(f"✅ 成功: {success_count}/{len(MODELS)}")
    print(f"❌ 失败: {failed_count}/{len(MODELS)}")
    print(f"📊 成功率: {(success_count/len(MODELS)*100):.1f}%")

def test_stream_response():
    """测试流式响应"""
    print("\n" + "=" * 60)
    print("测试流式响应 (使用 gpt-5 模型)")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-5",
        "messages": [
            {"role": "user", "content": "Count from 1 to 5"}
        ],
        "stream": True
    }
    
    try:
        response = requests.post(
            f"{API_URL}/v1/chat/completions",
            headers=headers,
            json=payload,
            stream=True,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ 流式响应成功，接收到的数据块:")
            chunk_count = 0
            for line in response.iter_lines():
                if line:
                    chunk_count += 1
                    line_str = line.decode('utf-8')
                    if chunk_count <= 3:
                        print(f"   块 {chunk_count}: {line_str[:100]}...")
            print(f"   ... 共接收 {chunk_count} 个数据块")
            return True
        else:
            print(f"❌ 流式响应失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 流式响应错误: {e}")
        return False

def main():
    """主测试函数"""
    print("\n")
    print("🚀 " + "=" * 58)
    print("   Advanced AI Models API - 完整测试")
    print("   API URL: " + API_URL)
    print("   模型总数: " + str(len(MODELS)))
    print("=" * 60)
    
    # 1. 测试模型列表
    models_ok = test_models_endpoint()
    
    # 2. 测试所有模型
    if models_ok:
        test_all_models()
    
    # 3. 测试流式响应
    test_stream_response()
    
    print("\n" + "=" * 60)
    print("🎉 测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()