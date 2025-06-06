"""
项目1: 简单AI代理实现
学习目标: 理解AI代理的基本概念和实现方式
难度: ⭐⭐☆☆☆
"""

import asyncio
import json
from typing import List, Dict, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class Message:
    """消息类"""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            import time
            self.timestamp = time.time()

class Tool(ABC):
    """工具基类"""
    
    @abstractmethod
    def get_name(self) -> str:
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        pass

class CalculatorTool(Tool):
    """计算器工具"""
    
    def get_name(self) -> str:
        return "calculator"
    
    def get_description(self) -> str:
        return "执行基本数学计算，支持加减乘除"
    
    async def execute(self, expression: str) -> Dict[str, Any]:
        try:
            # 简单的安全计算（实际项目中需要更严格的安全检查）
            allowed_chars = set('0123456789+-*/().')
            if not all(c in allowed_chars or c.isspace() for c in expression):
                return {"error": "表达式包含不允许的字符"}
            
            result = eval(expression)
            return {"result": result, "expression": expression}
        except Exception as e:
            return {"error": f"计算错误: {str(e)}"}

class WeatherTool(Tool):
    """天气查询工具（模拟）"""
    
    def get_name(self) -> str:
        return "weather"
    
    def get_description(self) -> str:
        return "查询指定城市的天气信息"
    
    async def execute(self, city: str) -> Dict[str, Any]:
        # 模拟天气数据
        weather_data = {
            "北京": {"temperature": "22°C", "condition": "晴天", "humidity": "45%"},
            "上海": {"temperature": "25°C", "condition": "多云", "humidity": "60%"},
            "深圳": {"temperature": "28°C", "condition": "小雨", "humidity": "75%"},
        }
        
        if city in weather_data:
            return {"city": city, "weather": weather_data[city]}
        else:
            return {"error": f"未找到城市 {city} 的天气信息"}

class SimpleAgent:
    """简单AI代理"""
    
    def __init__(self, name: str = "SimpleAgent"):
        self.name = name
        self.tools: Dict[str, Tool] = {}
        self.conversation_history: List[Message] = []
        self.system_prompt = """你是一个有用的AI助手。你可以使用以下工具来帮助用户：
- calculator: 执行数学计算
- weather: 查询天气信息

当用户需要计算时，使用calculator工具。
当用户询问天气时，使用weather工具。
请根据用户的需求选择合适的工具。"""
    
    def add_tool(self, tool: Tool):
        """添加工具"""
        self.tools[tool.get_name()] = tool
    
    def add_message(self, message: Message):
        """添加消息到对话历史"""
        self.conversation_history.append(message)
    
    async def process_user_input(self, user_input: str) -> str:
        """处理用户输入"""
        # 添加用户消息
        user_message = Message(role="user", content=user_input)
        self.add_message(user_message)
        
        # 简单的意图识别和工具选择
        response = await self._generate_response(user_input)
        
        # 添加助手回复
        assistant_message = Message(role="assistant", content=response)
        self.add_message(assistant_message)
        
        return response
    
    async def _generate_response(self, user_input: str) -> str:
        """生成回复（简化版本，实际项目中会使用LLM）"""
        user_input_lower = user_input.lower()
        
        # 计算相关关键词
        calc_keywords = ['计算', '算', '+', '-', '*', '/', '等于', '加', '减', '乘', '除']
        if any(keyword in user_input_lower for keyword in calc_keywords):
            return await self._handle_calculation(user_input)
        
        # 天气相关关键词
        weather_keywords = ['天气', '温度', '下雨', '晴天', '多云']
        if any(keyword in user_input_lower for keyword in weather_keywords):
            return await self._handle_weather_query(user_input)
        
        # 默认回复
        return f"你好！我是{self.name}。我可以帮你进行计算或查询天气。请告诉我你需要什么帮助。"
    
    async def _handle_calculation(self, user_input: str) -> str:
        """处理计算请求"""
        if "calculator" not in self.tools:
            return "抱歉，计算器工具不可用。"
        
        # 简单提取数学表达式（实际项目中需要更复杂的NLP处理）
        import re
        math_pattern = r'[\d+\-*/().\s]+'
        matches = re.findall(math_pattern, user_input)
        
        if matches:
            expression = max(matches, key=len).strip()
            result = await self.tools["calculator"].execute(expression=expression)
            
            if "error" in result:
                return f"计算出错：{result['error']}"
            else:
                return f"计算结果：{result['expression']} = {result['result']}"
        else:
            return "请提供一个有效的数学表达式，例如：2 + 3 * 4"
    
    async def _handle_weather_query(self, user_input: str) -> str:
        """处理天气查询"""
        if "weather" not in self.tools:
            return "抱歉，天气查询工具不可用。"
        
        # 简单提取城市名（实际项目中需要更复杂的NER）
        cities = ["北京", "上海", "深圳", "广州", "杭州"]
        city = None
        for c in cities:
            if c in user_input:
                city = c
                break
        
        if city:
            result = await self.tools["weather"].execute(city=city)
            
            if "error" in result:
                return f"查询失败：{result['error']}"
            else:
                weather = result["weather"]
                return f"{city}的天气：温度{weather['temperature']}，{weather['condition']}，湿度{weather['humidity']}"
        else:
            return "请指定要查询的城市，例如：北京的天气怎么样？"
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """获取对话历史"""
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp
            }
            for msg in self.conversation_history
        ]
    
    def save_conversation(self, filename: str):
        """保存对话历史"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.get_conversation_history(), f, ensure_ascii=False, indent=2)
    
    def load_conversation(self, filename: str):
        """加载对话历史"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                history = json.load(f)
                self.conversation_history = [
                    Message(
                        role=msg["role"],
                        content=msg["content"],
                        timestamp=msg["timestamp"]
                    )
                    for msg in history
                ]
        except FileNotFoundError:
            print(f"文件 {filename} 不存在")

async def main():
    """主函数 - 演示代理使用"""
    print("🤖 简单AI代理演示")
    print("=" * 50)
    
    # 创建代理
    agent = SimpleAgent("小助手")
    
    # 添加工具
    agent.add_tool(CalculatorTool())
    agent.add_tool(WeatherTool())
    
    # 测试对话
    test_inputs = [
        "你好！",
        "帮我计算 2 + 3 * 4",
        "北京的天气怎么样？",
        "计算 (10 + 5) / 3",
        "上海今天下雨吗？",
        "谢谢你的帮助"
    ]
    
    for user_input in test_inputs:
        print(f"\n👤 用户: {user_input}")
        response = await agent.process_user_input(user_input)
        print(f"🤖 助手: {response}")
    
    # 保存对话历史
    agent.save_conversation("conversation_history.json")
    print(f"\n💾 对话历史已保存到 conversation_history.json")
    
    # 显示对话统计
    history = agent.get_conversation_history()
    print(f"\n📊 对话统计:")
    print(f"   总消息数: {len(history)}")
    print(f"   用户消息: {len([m for m in history if m['role'] == 'user'])}")
    print(f"   助手回复: {len([m for m in history if m['role'] == 'assistant'])}")

if __name__ == "__main__":
    asyncio.run(main())

"""
🎯 学习要点:

1. **代理架构**: 理解AI代理的基本组成部分
   - 消息处理
   - 工具集成
   - 对话历史管理

2. **工具系统**: 学习如何设计和实现工具
   - 抽象基类设计
   - 具体工具实现
   - 错误处理

3. **异步编程**: 掌握Python异步编程
   - async/await语法
   - 异步函数调用

4. **数据结构**: 使用dataclass和类型注解
   - 结构化数据表示
   - 类型安全

📝 练习任务:

1. 添加新工具（如时间查询、翻译等）
2. 改进意图识别逻辑
3. 添加对话上下文理解
4. 实现工具链调用
5. 添加配置文件支持

🚀 扩展方向:

1. 集成真实的LLM API
2. 添加更复杂的NLP处理
3. 实现插件系统
4. 添加Web界面
5. 支持多轮对话上下文
"""