# Cursor2API - Advanced AI Models API

<p align="center">
  <img src="https://img.shields.io/badge/version-3.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/models-23-green.svg" alt="Models">
  <img src="https://img.shields.io/badge/license-MIT-orange.svg" alt="License">
  <img src="https://img.shields.io/badge/status-production-success.svg" alt="Status">
</p>

<p align="center">
  <b>🚀 一个部署在 Vercel 上的高级 AI 模型 API 服务</b><br>
  支持 23 个最新的 AI 模型，完全兼容 OpenAI API 格式
</p>

## ✨ 特性

- 🤖 **支持 23 个最新 AI 模型** - GPT-5、Claude 4、Gemini 2.5、DeepSeek、Grok 等
- 🔄 **完全兼容 OpenAI API** - 无缝对接现有应用
- 🌊 **流式/非流式响应** - 支持实时流式输出
- 🔒 **安全认证** - 基于环境变量的 API 密钥管理
- ⚡ **一键部署** - 快速部署到 Vercel
- 🌍 **CORS 支持** - 跨域访问无障碍

## 🚀 快速开始

### 部署到 Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/libaxuan/cursor2api)

### 手动部署

1. **克隆仓库**
```bash
git clone https://github.com/libaxuan/cursor2api.git
cd cursor2api
```

2. **安装 Vercel CLI**
```bash
npm i -g vercel
```

3. **部署项目**
```bash
vercel
```

4. **设置环境变量**

在 Vercel Dashboard 中设置 `API_KEY` 环境变量：
```
API_KEY=your-secure-api-key-here
```

## 📦 支持的模型

<details>
<summary>查看全部 23 个模型</summary>

### GPT 系列
- `gpt-5` - 最先进的GPT模型
- `gpt-5-codex` - GPT-5编程优化版
- `gpt-5-mini` - 轻量级GPT-5
- `gpt-5-nano` - 超轻量级GPT-5
- `gpt-4.1` - GPT-4增强版
- `gpt-4o` - GPT-4优化版

### Claude 系列
- `claude-3.5-sonnet` - Claude 3.5诗歌版
- `claude-3.5-haiku` - Claude 3.5俳句版
- `claude-3.7-sonnet` - 最新Claude 3.7
- `claude-4-sonnet` - 下一代Claude 4
- `claude-4-opus` - Claude 4旗舰版
- `claude-4.1-opus` - Claude 4.1增强版

### Gemini 系列
- `gemini-2.5-pro` - Google Gemini 2.5专业版
- `gemini-2.5-flash` - Gemini 2.5闪电版

### 其他模型
- `o3` - OpenAI O3推理模型
- `o4-mini` - O4轻量版
- `deepseek-r1` - DeepSeek研究版
- `deepseek-v3.1` - DeepSeek最新版本
- `kimi-k2-instruct` - Kimi K2指令版
- `grok-3` - xAI Grok-3
- `grok-3-mini` - Grok-3轻量版
- `grok-4` - 最新Grok-4
- `code-supernova-1-million` - 超级编程模型

</details>

## 📖 API 文档

### 基础配置

- **Base URL**: `https://your-app.vercel.app`
- **认证方式**: Bearer Token
- **请求头**: 
  ```
  Authorization: Bearer YOUR_API_KEY
  Content-Type: application/json
  ```

### 端点列表

#### 1. 获取模型列表

```http
GET /v1/models
```

<details>
<summary>查看示例</summary>

**请求示例**
```bash
curl -X GET "https://your-app.vercel.app/v1/models" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**响应示例**
```json
{
  "object": "list",
  "data": [
    {
      "id": "gpt-5",
      "object": "model",
      "created": 1234567890,
      "owned_by": "advanced-ai"
    }
  ]
}
```

</details>

#### 2. 聊天完成

```http
POST /v1/chat/completions
```

<details>
<summary>查看示例</summary>

**请求参数**
| 参数 | 类型 | 必须 | 说明 |
|-----|------|-----|------|
| model | string | ✅ | 模型ID |
| messages | array | ✅ | 消息数组 |
| stream | boolean | ❌ | 是否流式响应 (默认: false) |
| temperature | float | ❌ | 温度参数 (默认: 0.7) |
| max_tokens | integer | ❌ | 最大token数 (默认: 1000) |

**非流式请求**
```bash
curl -X POST "https://your-app.vercel.app/v1/chat/completions" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-5",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ]
  }'
```

**流式请求**
```bash
curl -X POST "https://your-app.vercel.app/v1/chat/completions" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-4-opus",
    "messages": [
      {"role": "user", "content": "Write a poem"}
    ],
    "stream": true
  }'
```

</details>

## 🧪 测试

使用提供的测试脚本测试所有模型：

```bash
python test_all_models.py
```

## 🔧 本地开发

1. **创建环境变量文件**
```bash
cp .env.example .env
# 编辑 .env 文件，设置你的 API_KEY
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **运行开发服务器**
```bash
vercel dev
```

## 📝 环境变量

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `API_KEY` | API 访问密钥 | `sk-xxxxxxxxxxxxxxxx` |

## 🛡️ 安全建议

- ✅ 使用强密码作为 API 密钥
- ✅ 定期更换密钥
- ✅ 不要在代码中硬编码密钥
- ✅ 使用 HTTPS 传输
- ✅ 限制 API 调用频率

## 📂 项目结构

```
cursor2api/
├── api/
│   └── index.py          # 主要 API 处理逻辑
├── .env.example          # 环境变量示例
├── .gitignore           # Git 忽略文件
├── LICENSE              # MIT 许可证
├── README.md            # 项目文档
├── requirements.txt     # Python 依赖
├── test_all_models.py   # 测试脚本
└── vercel.json          # Vercel 配置
```

## 🤝 贡献

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- OpenAI API 格式规范
- Vercel 平台支持
- 所有贡献者

## 📞 联系

如有问题或建议，请提交 [Issue](https://github.com/libaxuan/cursor2api/issues)

---

<p align="center">
  Made with ❤️ by the Cursor2API Team
</p>