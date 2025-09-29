#!/usr/bin/env python3
"""
测试上下文记忆功能
验证 API 是否能记住之前的对话内容
"""

import requests
import json
import time

# API 配置
API_URL = "http://localhost:8000/v1/chat/completions"
API_KEY = "sk-yoursk"

def test_conversation():
    """测试多轮对话"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "TestClient/1.0"  # 固定的 User-Agent 以保持会话
    }
    
    print("=" * 50)
    print("测试上下文记忆功能")
    print("=" * 50)
    
    # 第一轮对话：问一个数学题
    print("\n第一轮对话：")
    data1 = {
        "model": "gpt-5",
        "messages": [{"role": "user", "content": "100+50等于多少？"}],
        "stream": False
    }
    
    response1 = requests.post(API_URL, headers=headers, json=data1)
    if response1.status_code == 200:
        result1 = response1.json()
        answer1 = result1['choices'][0]['message']['content']
        print(f"用户: 100+50等于多少？")
        print(f"AI: {answer1}")
    else:
        print(f"错误: {response1.status_code}")
        return
    
    time.sleep(1)  # 短暂延迟
    
    # 第二轮对话：引用之前的内容
    print("\n第二轮对话（引用上下文）：")
    data2 = {
        "model": "gpt-5",
        "messages": [{"role": "user", "content": "这个结果再乘以2是多少？"}],
        "stream": False
    }
    
    response2 = requests.post(API_URL, headers=headers, json=data2)
    if response2.status_code == 200:
        result2 = response2.json()
        answer2 = result2['choices'][0]['message']['content']
        print(f"用户: 这个结果再乘以2是多少？")
        print(f"AI: {answer2}")
    else:
        print(f"错误: {response2.status_code}")
        return
    
    time.sleep(1)
    
    # 第三轮对话：继续引用
    print("\n第三轮对话（继续引用）：")
    data3 = {
        "model": "gpt-5",
        "messages": [{"role": "user", "content": "刚才的计算都对吗？"}],
        "stream": False
    }
    
    response3 = requests.post(API_URL, headers=headers, json=data3)
    if response3.status_code == 200:
        result3 = response3.json()
        answer3 = result3['choices'][0]['message']['content']
        print(f"用户: 刚才的计算都对吗？")
        print(f"AI: {answer3}")
    else:
        print(f"错误: {response3.status_code}")
        return
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("如果 AI 能够理解'这个结果'和'刚才'的引用，")
    print("说明上下文记忆功能正常工作。")
    print("=" * 50)

def test_different_sessions():
    """测试不同会话的隔离性"""
    print("\n" + "=" * 50)
    print("测试会话隔离性")
    print("=" * 50)
    
    # 会话1
    headers1 = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "TestClient1"
    }
    
    data = {
        "model": "gpt-5",
        "messages": [{"role": "user", "content": "记住数字888"}],
        "stream": False
    }
    
    print("\n会话1：")
    response1 = requests.post(API_URL, headers=headers1, json=data)
    if response1.status_code == 200:
        result1 = response1.json()
        print(f"用户: 记住数字888")
        print(f"AI: {result1['choices'][0]['message']['content']}")
    
    # 会话2（不同的 User-Agent）
    headers2 = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "TestClient2"
    }
    
    print("\n会话2（不同客户端）：")
    data2 = {
        "model": "gpt-5",
        "messages": [{"role": "user", "content": "我刚才说的数字是什么？"}],
        "stream": False
    }
    
    response2 = requests.post(API_URL, headers=headers2, json=data2)
    if response2.status_code == 200:
        result2 = response2.json()
        print(f"用户: 我刚才说的数字是什么？")
        print(f"AI: {result2['choices'][0]['message']['content']}")
        print("（预期：AI 不应该知道888，因为是不同的会话）")

if __name__ == "__main__":
    print("开始测试上下文记忆功能...")
    print("注意：需要先启动本地服务器")
    print("python api/index.py")
    print()
    
    try:
        test_conversation()
        test_different_sessions()
    except requests.exceptions.ConnectionError:
        print("\n错误：无法连接到 API 服务器")
        print("请先运行: python api/index.py")
    except Exception as e:
        print(f"\n发生错误: {e}")