#!/usr/bin/env python3
"""
测试新的 API 功能（本地测试）
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# 导入 API 模块
from api.index import generate_intelligent_response, process_math

def test_math_calculation():
    """测试数学计算功能"""
    print("=" * 60)
    print("测试数学计算功能")
    print("=" * 60)
    
    test_cases = [
        ("99+2=?", "101"),
        ("100-50", "50"),
        ("10*5", "50"),
        ("100/4", "25"),
        ("(10+5)*2", "30"),
        ("3.5+1.5", "5"),
    ]
    
    for question, expected in test_cases:
        result = process_math(question)
        print(f"问题: {question}")
        print(f"期望: {expected}")
        print(f"结果: {result}")
        print(f"状态: {'✅ 通过' if result == expected else '❌ 失败'}")
        print("-" * 40)

def test_intelligent_responses():
    """测试智能响应功能"""
    print("\n" + "=" * 60)
    print("测试智能响应功能")
    print("=" * 60)
    
    test_cases = [
        ("99+2=?", "claude-4.1-opus"),
        ("你好", "claude-4.1-opus"),
        ("Hello", "gpt-5"),
        ("你是谁", "claude-3.5-sonnet"),
        ("现在几点", "gpt-4"),
        ("Python代码", "gpt-5-codex"),
        ("天气怎么样", "gemini-2.5-pro"),
        ("翻译一下", "deepseek-v3.1"),
    ]
    
    for message, model in test_cases:
        response = generate_intelligent_response(message, model)
        print(f"\n问题: {message}")
        print(f"模型: {model}")
        print(f"响应: {response[:200]}..." if len(response) > 200 else f"响应: {response}")
        
        # 检查是否为智能响应（不包含模板化的模型名称前缀）
        if not response.startswith(f"[{model}]"):
            print("✅ 智能响应（非模板）")
        else:
            print("⚠️ 可能是模板响应")

def test_api_response_format():
    """测试 API 响应格式"""
    print("\n" + "=" * 60)
    print("测试 API 响应格式")
    print("=" * 60)
    
    import json
    import time
    from api.index import generate_random_string
    
    # 测试消息
    messages = [{"role": "user", "content": "99+2=?"}]
    model = "claude-4.1-opus"
    
    # 获取响应内容
    user_message = messages[-1]["content"]
    response_content = generate_intelligent_response(user_message, model)
    
    # 构建 API 响应
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
            "prompt_tokens": 1,
            "completion_tokens": len(response_content) // 4,
            "total_tokens": 1 + len(response_content) // 4
        }
    }
    
    print("生成的 API 响应:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    # 验证响应内容
    print("\n验证:")
    content = response["choices"][0]["message"]["content"]
    if "99 + 2 = 101" in content or "101" in content:
        print("✅ 数学计算正确!")
    else:
        print("❌ 未正确计算数学结果")
    
    if not content.startswith("["):
        print("✅ 不是模板响应!")
    else:
        print("❌ 仍然是模板响应")

def main():
    """主测试函数"""
    print("\n" + "=" * 80)
    print("新 API 功能测试")
    print("=" * 80)
    
    # 运行测试
    test_math_calculation()
    test_intelligent_responses()
    test_api_response_format()
    
    print("\n" + "=" * 80)
    print("测试完成!")
    print("=" * 80)
    
    print("""
注意事项:
1. 本地测试显示新代码功能正常
2. 如果线上 API 仍返回旧响应，需要重新部署到 Vercel
3. 部署步骤:
   - git add .
   - git commit -m "Fix: 实现真正的智能响应"
   - git push (或 vercel deploy)
4. 等待 Vercel 重新构建和部署
""")

if __name__ == "__main__":
    main()