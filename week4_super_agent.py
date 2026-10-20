import os
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")

# ================= 1. 我们的“本地资料库” =================
# 实际工作中这是存在数据库里的，这里我们直接放进一个列表
knowledge_base = [
    "公司规定：每年有5天带薪年假。",
    "报销规定：打车费超过100元需要主管审批。",
    "考勤规定：每天早上9点半前打卡。"
]

# ================= 2. 定义 Agent 的两个工具 =================
# 工具一：搜资料（查公司手册）
def search_docs(query: str):
    # 极简搜索：只要用户问的词（比如“打车”、“年假”）在资料里，就找出来
    results = [doc for doc in knowledge_base if any(word in doc for word in query.split())]
    if not results:
        return "没找到相关资料。"
    return "\n".join(results)

# 工具二：算数
def calculator(expression: str):
    try:
        return str(eval(expression))
    except Exception as e:
        return f"算不出来: {e}"

# 告诉大模型，我们手里有哪些工具可以调用
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "search_docs",
            "description": "当你需要查阅公司制度（如年假、报销、考勤）时，调用此工具。",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "搜索关键词"}},
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "用于计算数学表达式，如 '(45 * 12) + 88'",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"]
            }
        }
    }
]

available_tools = {"search_docs": search_docs, "calculator": calculator}

# ================= 3. 核心 Agent 循环 =================
def run_agent(user_query):
    print(f"\n👤 用户: {user_query}")
    messages = [{"role": "system", "content": "你是一个智能助理。请根据需要使用工具。只知道资料里的内容，不要瞎编。"},
                {"role": "user", "content": user_query}]
    
    # 最多循环 5 次，防止死循环
    for step in range(5):
        print(f"--- 第 {step+1} 轮思考 ---")
        
        # 大模型思考
        response = client.chat.completions.create(
            model="deepseek-chat", messages=messages, tools=tools_schema, temperature=0.1
        )
        msg = response.choices[0].message
        messages.append(msg)
        
        # 如果模型没有调用工具，说明它想好答案了，直接打印并结束
        if not msg.tool_calls:
            print(f"🤖 Agent 最终回复:\n{msg.content}")
            return
            
        # 如果模型要调用工具，我们就去执行
        for tool_call in msg.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            print(f"⚙️ 模型决定调用: {name}")
            
            # 执行真实的函数
            result = available_tools[name](**args)
            print(f"✅ 工具返回的结果: {result}")
            
            # 把结果塞回给模型
            messages.append({"tool_call_id": tool_call.id, "role": "tool", "name": name, "content": result})

# ================= 4. 跑起来试试！ =================
run_agent("帮我算一下 (100 * 5) + 20 等于几？")  # 测试算数
run_agent("出差打车花了120块，能报销吗？")       # 测试查资料
run_agent("我明年有多少天年假？")                 # 测试查资料