"""
项目2: LLM集成实践
学习目标: 学习如何集成大语言模型API，实现真正的AI对话
难度: ⭐⭐⭐☆☆
"""

import asyncio
import json
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import aiohttp
from datetime import datetime

@dataclass
class ChatMessage:
    """聊天消息"""
    role: str  # 'system', 'user', 'assistant'
    content: str
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class LLMProvider(ABC):
    """LLM提供商抽象基类"""
    
    @abstractmethod
    async def chat_completion(
        self, 
        messages: List[ChatMessage], 
        **kwargs
    ) -> Dict[str, Any]:
        pass

class OpenAIProvider(LLMProvider):
    """OpenAI API提供商"""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1"
    
    async def chat_completion(
        self, 
        messages: List[ChatMessage], 
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> Dict[str, Any]:
        """调用OpenAI Chat Completion API"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 转换消息格式
        api_messages = [
            {"role": msg.role, "content": msg.content} 
            for msg in messages
        ]
        
        payload = {
            "model": self.model,
            "messages": api_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "content": result["choices"][0]["message"]["content"],
                            "usage": result.get("usage", {}),
                            "model": result.get("model", self.model)
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"API错误 {response.status}: {error_text}"
                        }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"请求异常: {str(e)}"
                }

class MockLLMProvider(LLMProvider):
    """模拟LLM提供商（用于测试）"""
    
    def __init__(self):
        self.responses = {
            "计算": "我可以帮你进行数学计算。请告诉我具体的计算表达式。",
            "天气": "我可以查询天气信息。请告诉我你想查询哪个城市的天气。",
            "你好": "你好！我是AI助手，很高兴为你服务。有什么我可以帮助你的吗？",
            "谢谢": "不客气！如果还有其他问题，随时可以问我。"
        }
    
    async def chat_completion(
        self, 
        messages: List[ChatMessage], 
        **kwargs
    ) -> Dict[str, Any]:
        """模拟LLM响应"""
        
        # 模拟API延迟
        await asyncio.sleep(0.5)
        
        if not messages:
            return {
                "success": False,
                "error": "没有消息"
            }
        
        last_message = messages[-1].content.lower()
        
        # 简单的关键词匹配
        for keyword, response in self.responses.items():
            if keyword in last_message:
                return {
                    "success": True,
                    "content": response,
                    "usage": {"total_tokens": 50},
                    "model": "mock-llm"
                }
        
        # 默认响应
        return {
            "success": True,
            "content": "我理解了你的问题。让我想想如何最好地帮助你...",
            "usage": {"total_tokens": 30},
            "model": "mock-llm"
        }

class FunctionTool:
    """函数工具类"""
    
    def __init__(self, name: str, description: str, parameters: Dict[str, Any], function):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.function = function
    
    def to_openai_format(self) -> Dict[str, Any]:
        """转换为OpenAI函数调用格式"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """执行函数"""
        try:
            if asyncio.iscoroutinefunction(self.function):
                result = await self.function(**kwargs)
            else:
                result = self.function(**kwargs)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

class SmartAgent:
    """智能代理（集成LLM）"""
    
    def __init__(self, llm_provider: LLMProvider, name: str = "SmartAgent"):
        self.llm_provider = llm_provider
        self.name = name
        self.conversation_history: List[ChatMessage] = []
        self.tools: Dict[str, FunctionTool] = {}
        self.system_prompt = """你是一个有用的AI助手。你可以：
1. 回答各种问题
2. 进行数学计算
3. 查询天气信息
4. 提供建议和帮助

请根据用户的需求提供准确、有用的回复。如果需要使用工具，请明确说明。"""
        
        # 添加系统消息
        self.add_message(ChatMessage(role="system", content=self.system_prompt))
    
    def add_tool(self, tool: FunctionTool):
        """添加工具"""
        self.tools[tool.name] = tool
    
    def add_message(self, message: ChatMessage):
        """添加消息"""
        self.conversation_history.append(message)
    
    async def chat(self, user_input: str) -> str:
        """与用户对话"""
        # 添加用户消息
        user_message = ChatMessage(role="user", content=user_input)
        self.add_message(user_message)
        
        # 获取LLM响应
        response = await self.llm_provider.chat_completion(
            messages=self.conversation_history,
            temperature=0.7
        )
        
        if response["success"]:
            assistant_content = response["content"]
            
            # 检查是否需要使用工具
            tool_response = await self._check_and_use_tools(user_input, assistant_content)
            if tool_response:
                assistant_content = tool_response
            
            # 添加助手回复
            assistant_message = ChatMessage(role="assistant", content=assistant_content)
            self.add_message(assistant_message)
            
            return assistant_content
        else:
            error_message = f"抱歉，我遇到了一些问题：{response['error']}"
            assistant_message = ChatMessage(role="assistant", content=error_message)
            self.add_message(assistant_message)
            return error_message
    
    async def _check_and_use_tools(self, user_input: str, llm_response: str) -> Optional[str]:
        """检查并使用工具"""
        user_input_lower = user_input.lower()
        
        # 计算工具
        if "calculator" in self.tools and any(
            keyword in user_input_lower 
            for keyword in ['计算', '算', '+', '-', '*', '/', '等于']
        ):
            # 提取数学表达式
            import re
            math_pattern = r'[\d+\-*/().\s]+'
            matches = re.findall(math_pattern, user_input)
            
            if matches:
                expression = max(matches, key=len).strip()
                result = await self.tools["calculator"].execute(expression=expression)
                
                if result["success"]:
                    return f"计算结果：{expression} = {result['result']}"
                else:
                    return f"计算出错：{result['error']}"
        
        # 天气工具
        if "weather" in self.tools and any(
            keyword in user_input_lower 
            for keyword in ['天气', '温度', '下雨', '晴天']
        ):
            # 提取城市名
            cities = ["北京", "上海", "深圳", "广州", "杭州"]
            city = None
            for c in cities:
                if c in user_input:
                    city = c
                    break
            
            if city:
                result = await self.tools["weather"].execute(city=city)
                
                if result["success"]:
                    weather = result["result"]
                    return f"{city}的天气：{weather}"
                else:
                    return f"查询失败：{result['error']}"
        
        return None
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """获取对话摘要"""
        messages = [msg for msg in self.conversation_history if msg.role != "system"]
        return {
            "total_messages": len(messages),
            "user_messages": len([m for m in messages if m.role == "user"]),
            "assistant_messages": len([m for m in messages if m.role == "assistant"]),
            "conversation_start": messages[0].timestamp if messages else None,
            "conversation_end": messages[-1].timestamp if messages else None
        }
    
    def export_conversation(self, filename: str):
        """导出对话"""
        conversation_data = {
            "agent_name": self.name,
            "summary": self.get_conversation_summary(),
            "messages": [asdict(msg) for msg in self.conversation_history]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(conversation_data, f, ensure_ascii=False, indent=2)

# 工具函数定义
def calculator_function(expression: str) -> str:
    """计算器函数"""
    try:
        # 安全计算
        allowed_chars = set('0123456789+-*/().')
        if not all(c in allowed_chars or c.isspace() for c in expression):
            raise ValueError("表达式包含不允许的字符")
        
        result = eval(expression)
        return str(result)
    except Exception as e:
        raise ValueError(f"计算错误: {str(e)}")

async def weather_function(city: str) -> str:
    """天气查询函数"""
    # 模拟天气数据
    weather_data = {
        "北京": "晴天，22°C，湿度45%",
        "上海": "多云，25°C，湿度60%", 
        "深圳": "小雨，28°C，湿度75%",
        "广州": "晴天，30°C，湿度50%",
        "杭州": "多云，24°C，湿度55%"
    }
    
    if city in weather_data:
        return weather_data[city]
    else:
        raise ValueError(f"未找到城市 {city} 的天气信息")

async def main():
    """主函数"""
    print("🧠 智能AI代理演示（LLM集成版）")
    print("=" * 50)
    
    # 选择LLM提供商
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print("🔑 使用OpenAI API")
        llm_provider = OpenAIProvider(api_key)
    else:
        print("🎭 使用模拟LLM（设置OPENAI_API_KEY环境变量以使用真实API）")
        llm_provider = MockLLMProvider()
    
    # 创建智能代理
    agent = SmartAgent(llm_provider, "智能助手")
    
    # 添加工具
    calculator_tool = FunctionTool(
        name="calculator",
        description="执行数学计算",
        parameters={
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "数学表达式"
                }
            },
            "required": ["expression"]
        },
        function=calculator_function
    )
    
    weather_tool = FunctionTool(
        name="weather",
        description="查询城市天气",
        parameters={
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称"
                }
            },
            "required": ["city"]
        },
        function=weather_function
    )
    
    agent.add_tool(calculator_tool)
    agent.add_tool(weather_tool)
    
    # 测试对话
    test_conversations = [
        "你好！你能做什么？",
        "帮我计算 15 * 8 + 32",
        "北京今天天气怎么样？",
        "请解释一下什么是人工智能",
        "计算 (100 - 25) / 5",
        "上海的天气如何？",
        "谢谢你的帮助！"
    ]
    
    for user_input in test_conversations:
        print(f"\n👤 用户: {user_input}")
        response = await agent.chat(user_input)
        print(f"🤖 助手: {response}")
        
        # 添加延迟，模拟真实对话
        await asyncio.sleep(1)
    
    # 显示对话摘要
    summary = agent.get_conversation_summary()
    print(f"\n📊 对话摘要:")
    print(f"   总消息数: {summary['total_messages']}")
    print(f"   用户消息: {summary['user_messages']}")
    print(f"   助手回复: {summary['assistant_messages']}")
    
    # 导出对话
    agent.export_conversation("smart_conversation.json")
    print(f"\n💾 对话已导出到 smart_conversation.json")

if __name__ == "__main__":
    asyncio.run(main())

"""
🎯 学习要点:

1. **LLM集成**: 学习如何集成大语言模型API
   - API调用封装
   - 错误处理
   - 异步请求

2. **提供商抽象**: 设计可扩展的LLM提供商系统
   - 抽象基类
   - 多种实现
   - 统一接口

3. **工具系统**: 实现函数调用和工具集成
   - 工具定义
   - 参数验证
   - 结果处理

4. **对话管理**: 管理多轮对话上下文
   - 消息历史
   - 上下文保持
   - 对话导出

📝 练习任务:

1. 添加更多LLM提供商（Anthropic、Google等）
2. 实现流式响应
3. 添加对话记忆压缩
4. 实现工具链调用
5. 添加对话评估指标

🚀 扩展方向:

1. 实现RAG系统
2. 添加多模态支持
3. 实现Agent规划能力
4. 添加安全过滤
5. 支持插件系统

💡 使用提示:

1. 设置环境变量 OPENAI_API_KEY 使用真实API
2. 可以扩展工具系统添加更多功能
3. 注意API调用的成本控制
4. 实现适当的错误重试机制
"""