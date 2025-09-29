
#!/usr/bin/env python3
"""
测试 API 与 KiloCode 插件的兼容性
诊断可能的问题
"""
import requests
import json
import sys

# API 配置
API_URL = "https://api.autoschool.eu.org"
API_KEY = "sk-2ddt39UQQSk2dyW1RYuo3Kqu55bHuxydBewQF06QrGllfVOzby"

def test_basic_request():
    """测试基本请求"""
    print("1. 测试基本的非流式请求...")
    print("-" * 50)
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "claude-4.1-opus",
        "messages": [
            {"role": "user", "content": "介绍一下你自己"}
        ],
        "stream": False
    }
    
    try:
        response = requests.post(
            f"{API_URL}/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 基本请求成功")
            print(f"响应格式检查:")
            
            # 检查必要字段
            required_fields = ["id", "object", "created", "model", "choices"]
            for field in required_fields:
                if field in data:
                    print(f"  ✓ {field}: 存在")
                else:
                    print(f"  ✗ {field}: 缺失")
            
            # 检查 choices 结构
            if "choices" in data and len(data["choices"]) > 0:
                choice = data["choices"][0]
                print(f"\nchoices[0] 结构:")
                for key in ["index", "message", "finish_reason"]:
                    if key in choice:
                        print(f"  ✓ {key}: 存在")
                    else:
                        print(f"  ✗ {key}: 缺失")
                
                # 检查 message 结构
                if "message" in choice:
                    message = choice["message"]
                    print(f"\nmessage 结构:")
                    for key in ["role", "content"]:
                        if key in message:
                            print(f"  ✓ {key}: 存在")
                        else:
                            print(f"  ✗ {key}: 缺失")
            
            print(f"\n完整响应:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return True
        else:
            print(f"❌ 请求失败")
            print(f"错误响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_stream_request():
    """测试流式请求"""
    print("\n2. 测试流式请求...")
    print("-" * 50)
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream"  # 添加 Accept 头
    }
    
    payload = {
        "model": "claude-4.1-opus",
        "messages": [
            {"role": "user", "content": "说hello"}
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
        
        print(f"状态码: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'None')}")
        
        if response.status_code == 200:
            print(f"✅ 流式请求成功")
            print(f"前5个数据块:")
            
            chunk_count = 0
            for line in response.iter_lines():
                if line:
                    chunk_count += 1
                    line_str = line.decode('utf-8')
                    
                    if chunk_count <= 5:
                        print(f"\n块 {chunk_count}: {line_str}")
                        
                        # 解析 SSE 数据
                        if line_str.startswith("data: "):
                            data_str = line_str[6:]
                            if data_str != "[DONE]":
                                try:
                                    chunk_data = json.loads(data_str)
                                    print(f"  解析成功: {json.dumps(chunk_data, indent=2, ensure_ascii=False)[:200]}...")
                                except:
                                    print(f"  解析失败: {data_str}")
                    
                    if line_str == "data: [DONE]":
                        print(f"\n✅ 收到结束标记 [DONE]")
                        break
            
            print(f"\n总共接收 {chunk_count} 个数据块")
            return True
        else:
            print(f"❌ 流式请求失败")
            print(f"错误响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 流式请求异常: {e}")
        return False

def test_error_handling():
    """测试错误处理"""
    print("\n3. 测试错误处理...")
    print("-" * 50)
    
    # 测试无效的 API 密钥
    print("\n3.1 测试无效的 API 密钥...")
    headers = {
        "Authorization": "Bearer invalid-key",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "claude-4.1-opus",
        "messages": [{"role": "user", "content": "test"}],
        "stream": False
    }
    
    try:
        response = requests.post(
            f"{API_URL}/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 401:
            print(f"✅ 正确返回 401 未授权")
            error_data = response.json()
            print(f"错误格式: {json.dumps(error_data, indent=2)}")
        else:
            print(f"❌ 应该返回 401，但返回了 {response.status_code}")
    except Exception as e:
        print(f"异常: {e}")
    
    # 测试无效的模型名称
    print("\n3.2 测试有效 API 密钥但使用系统未定义的模型...")
    headers["Authorization"] = f"Bearer {API_KEY}"
    payload["model"] = "invalid-model-name"
    
    try:
        response = requests.post(
            f"{API_URL}/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"⚠️  系统接受了未定义的模型名称")
            data = response.json()
            print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
        else:
            print(f"返回错误: {response.status_code}")
            print(f"错误内容: {response.text}")
    except Exception as e:
        print(f"异常: {e}")

def test_kilocode_specific():
    """测试 KiloCode 可能需要的特定功能"""
    print("\n4. 测试 KiloCode 特定需求...")
    print("-" * 50)
    
    # 测试不同的参数组合
    test_cases = [
        {
            "name": "带 temperature 参数",
            "params": {"temperature": 0.7}
        },
        {
            "name": "带 max_tokens 参数",
            "params": {"max_tokens": 100}
        },
        {
            "name": "带 top_p 参数",
            "params": {"top_p": 0.9}
        },
        {
            "name": "带 system message",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello"}
            ]
        }
    ]
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    for test_case in test_cases:
        print(f"\n测试: {test_case['name']}")
        
        payload = {
            "model": "claude-4.1-opus",
            "messages": test_case.get("messages", [{"role": "user", "content": "test"}]),
            "stream": False
        }
        
        # 添加额外参数
        if "params" in test_case:
            payload.update(test_case["params"])
        
        try:
            response = requests.post(
                f"{API_URL}/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"  ✅ 成功")
                data = response.json()
                # 检查 usage 字段
                if "usage" in data:
                    print(f"  usage 字段存在: {data['usage']}")
            else:
                print(f"  ❌ 失败: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ 异常: {e}")

def main():
    """主函数"""
    print("=" * 60)
    print("KiloCode 插件兼容性测试")
    print("API URL:", API_URL)
    print("=" * 60)
    
    # 运行所有测试
    test_basic_request()
    test_stream_request()
    test_error_handling()
    test_kilocode_specific()
    
    print("\n" + "=" * 60)
    print("可能的问题及解决方案:")
    print("=" * 60)
    print("""
1. 如果 KiloCode 插件无法使用，可能的原因：
   
   a) API 密钥格式问题
      - 确保在 KiloCode 设置中正确输入 API 密钥
      - 不要包含 "Bearer " 前缀
   
   b) Base URL 设置问题
      - 在 KiloCode 中设置 Base URL 为: https://api.autoschool.eu.org
      - 不要在末尾加 /
   
   c) 模型名称问题
      - 确保使用支持的模型名称，如 "claude-4.1-opus"
      - 注意大小写
   
   d) 网络连接问题
      - 检查是否能访问 https://api.autoschool.eu.org
      - 检查代理设置
   
   e) KiloCode 版本兼容性
      - 更新到最新版本的 KiloCode
      - 某些旧版本可能不支持自定义 API 端点

2. 在 KiloCode 中的配置步骤：
   1. 打开 KiloCode 设置
   2. 选择 "Custom API"
   3. 输入 Base URL: https://api.autoschool.eu.org
   4. 输入 API Key: sk-2ddt39UQQSk2dyW1RYuo3Kqu55bHuxydBewQF06QrGllfVOzby
   5. 选择模型: claude-4.1-opus 或其他支持的模型
   6. 保存并测试
""")

if __name__ == "__main__":
    main()