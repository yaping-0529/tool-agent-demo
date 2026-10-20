markdown
# 基于 Function Calling 的轻量级 Tool Agent

这是一个不依赖任何重框架（如 LangChain），使用原生 Python 和大模型 API 手写实现的 Agent 核心循环。

## 💡 核心特性
- **原生 API 通信**：基于 OpenAI SDK 接入兼容接口（如 DeepSeek）。
- **工具编排（Tool Orchestration）**：支持动态注册工具（计算器、时间查询），通过 JSON Schema 约束大模型调用。
- **闭环执行机制**：实现了 `LLM输出决策 -> 代码执行工具 -> 结果回传LLM -> 最终答复` 的完整循环。
- **异常与边界兜底**：
  - 包含 `max_steps` 最大步数限制，防止无限循环刷爆 Token。
  - 包含工具执行异常捕获机制，工具报错时能将错误信息回传，让大模型自我修正或向用户解释。

## 🚀 如何运行
1. 安装依赖：`pip install openai python-dotenv`
2. 在根目录创建 `.env` 文件，写入：`DEEPSEEK_API_KEY=你的密钥`
3. 运行：`python tool_agent.py`