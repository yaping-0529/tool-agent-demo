import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import datetime

load_dotenv()
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")

# ================= 1. 定义你的“工具库” =================
def calculator(expression: str):
    try:
        # 警告：eval有安全风险，仅限本地学习演示使用
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"计算错误: {e}"

def get_current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ================= 2. 告诉模型有哪些工具 =================
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "用于计算数学表达式，例如 '(23 * 7) / 3'",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "数学表达式字符串"}
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前的日期和时间",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]

# ================= 3. 工具名称到真实函数的映射 =================
available_functions = {
    "calculator": calculator,
    "get_current_time": get_current_time
}

# ================= 4. 核心 Agent 循环 =================
def run_agent(user_query):
    print(f"\n👤 用户: {user_query}")
    
    messages = [
        {"role": "system", "content": "你是一个智能助手。你可以使用工具来解决问题。请先思考是否需要调用工具。"},
        {"role": "user", "content": user_query}
    ]

    max_steps = 1
    step = 0

    while step < max_steps:
        step += 1
        print(f"--- 第 {step} 轮思考 ---")
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=tools_schema,
            temperature=0.1
        )

        response_message = response.choices[0].message
        messages.append(response_message)

        tool_calls = response_message.tool_calls
        if not tool_calls:
            print(f"🤖 Agent 最终回复: {response_message.content}")
            break
            
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            print(f"⚙️ 模型请求调用工具: {function_name}，参数: {function_args}")
            
            # 执行真实的函数
            function_response = available_functions[function_name](**function_args)
            print(f"✅ 工具执行结果: {function_response}")

            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response,
            })
    
    if step == max_steps:
        print("⚠️ 达到最大循环步数，任务终止。")

# ================= 5. 测试 =================
if __name__ == "__main__":
    run_agent("现在几点了？另外帮我算一下 (45 * 12) + 88 是多少？")