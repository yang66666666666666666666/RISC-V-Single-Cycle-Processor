"""
项目3: OpenHands自定义代理实现
学习目标: 深入理解OpenHands架构，实现自定义代理
难度: ⭐⭐⭐⭐☆

注意：这个项目需要在OpenHands项目环境中运行
"""

import asyncio
import json
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

# 模拟OpenHands的核心组件（实际使用时应该从openhands包导入）
class Event:
    """事件基类"""
    def __init__(self, source: str = "agent"):
        self.source = source
        self.timestamp = asyncio.get_event_loop().time()

class Action(Event):
    """动作事件"""
    def __init__(self, source: str = "agent"):
        super().__init__(source)

class Observation(Event):
    """观察事件"""
    def __init__(self, source: str = "environment"):
        super().__init__(source)

class MessageAction(Action):
    """消息动作"""
    def __init__(self, content: str, source: str = "agent"):
        super().__init__(source)
        self.content = content
    
    def __str__(self):
        return f"MessageAction(content='{self.content}')"

class CmdRunAction(Action):
    """命令执行动作"""
    def __init__(self, command: str, source: str = "agent"):
        super().__init__(source)
        self.command = command
    
    def __str__(self):
        return f"CmdRunAction(command='{self.command}')"

class FileEditAction(Action):
    """文件编辑动作"""
    def __init__(self, path: str, content: str, source: str = "agent"):
        super().__init__(source)
        self.path = path
        self.content = content
    
    def __str__(self):
        return f"FileEditAction(path='{self.path}')"

class AgentFinishAction(Action):
    """代理完成动作"""
    def __init__(self, outputs: Dict[str, Any], source: str = "agent"):
        super().__init__(source)
        self.outputs = outputs
    
    def __str__(self):
        return f"AgentFinishAction(outputs={self.outputs})"

class CmdOutputObservation(Observation):
    """命令输出观察"""
    def __init__(self, content: str, command: str, exit_code: int = 0):
        super().__init__("environment")
        self.content = content
        self.command = command
        self.exit_code = exit_code
    
    def __str__(self):
        return f"CmdOutputObservation(exit_code={self.exit_code})"

class FileReadObservation(Observation):
    """文件读取观察"""
    def __init__(self, content: str, path: str):
        super().__init__("environment")
        self.content = content
        self.path = path
    
    def __str__(self):
        return f"FileReadObservation(path='{self.path}')"

class ErrorObservation(Observation):
    """错误观察"""
    def __init__(self, content: str, error_type: str = "general"):
        super().__init__("environment")
        self.content = content
        self.error_type = error_type
    
    def __str__(self):
        return f"ErrorObservation(error_type='{self.error_type}')"

@dataclass
class State:
    """代理状态"""
    history: List[Event]
    iteration: int = 0
    max_iterations: int = 100
    
    def get_last_action(self) -> Optional[Action]:
        """获取最后一个动作"""
        for event in reversed(self.history):
            if isinstance(event, Action):
                return event
        return None
    
    def get_last_observation(self) -> Optional[Observation]:
        """获取最后一个观察"""
        for event in reversed(self.history):
            if isinstance(event, Observation):
                return event
        return None
    
    def add_event(self, event: Event):
        """添加事件"""
        self.history.append(event)

class MockLLM:
    """模拟LLM"""
    def __init__(self, model: str = "mock-gpt"):
        self.model = model
    
    async def completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """模拟LLM补全"""
        if not messages:
            return "我需要更多信息来帮助你。"
        
        last_message = messages[-1]["content"].lower()
        
        # 简单的响应逻辑
        if "hello" in last_message or "你好" in last_message:
            return "你好！我是自定义代理，很高兴为你服务。"
        elif "file" in last_message or "文件" in last_message:
            return "我可以帮你处理文件。请告诉我具体需要做什么。"
        elif "run" in last_message or "执行" in last_message:
            return "我可以执行命令。请告诉我需要运行什么命令。"
        elif "finish" in last_message or "完成" in last_message:
            return "好的，任务完成。"
        else:
            return f"我理解了你的请求：{last_message}。让我来处理这个任务。"

class CustomAgent:
    """自定义OpenHands代理"""
    
    def __init__(self, llm: MockLLM, name: str = "CustomAgent"):
        self.llm = llm
        self.name = name
        self.system_prompt = """你是一个有用的AI代理，可以执行以下操作：
1. 执行shell命令
2. 读取和编辑文件
3. 与用户对话
4. 完成指定任务

请根据用户的需求选择合适的操作。"""
    
    async def step(self, state: State) -> Action:
        """执行一步操作"""
        # 构建对话历史
        messages = self._build_messages(state)
        
        # 获取LLM响应
        response = await self.llm.completion(messages)
        
        # 解析响应并生成动作
        action = self._parse_response_to_action(response, state)
        
        return action
    
    def _build_messages(self, state: State) -> List[Dict[str, str]]:
        """构建消息历史"""
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # 添加历史事件
        for event in state.history[-10:]:  # 只取最近10个事件
            if isinstance(event, MessageAction):
                if "user:" in event.content.lower():
                    messages.append({"role": "user", "content": event.content})
                else:
                    messages.append({"role": "assistant", "content": event.content})
            elif isinstance(event, CmdOutputObservation):
                messages.append({
                    "role": "system", 
                    "content": f"命令 '{event.command}' 的输出：{event.content[:200]}..."
                })
            elif isinstance(event, ErrorObservation):
                messages.append({
                    "role": "system",
                    "content": f"错误：{event.content}"
                })
        
        return messages
    
    def _parse_response_to_action(self, response: str, state: State) -> Action:
        """解析LLM响应为动作"""
        response_lower = response.lower()
        
        # 检查是否需要执行命令
        if any(keyword in response_lower for keyword in ["run", "execute", "命令", "执行"]):
            # 简单提取命令（实际项目中需要更复杂的解析）
            if "ls" in response_lower:
                return CmdRunAction("ls -la")
            elif "pwd" in response_lower:
                return CmdRunAction("pwd")
            elif "date" in response_lower:
                return CmdRunAction("date")
            else:
                return CmdRunAction("echo 'Hello from custom agent'")
        
        # 检查是否需要编辑文件
        elif any(keyword in response_lower for keyword in ["file", "edit", "write", "文件", "编辑"]):
            return FileEditAction(
                path="/tmp/agent_output.txt",
                content=f"Agent response: {response}\nTimestamp: {asyncio.get_event_loop().time()}"
            )
        
        # 检查是否完成任务
        elif any(keyword in response_lower for keyword in ["finish", "done", "complete", "完成"]):
            return AgentFinishAction(outputs={"result": response, "status": "completed"})
        
        # 默认返回消息动作
        else:
            return MessageAction(content=response)

class MockRuntime:
    """模拟运行时环境"""
    
    def __init__(self):
        self.files = {}  # 模拟文件系统
    
    async def execute_action(self, action: Action) -> Observation:
        """执行动作并返回观察"""
        if isinstance(action, CmdRunAction):
            return await self._execute_command(action)
        elif isinstance(action, FileEditAction):
            return await self._edit_file(action)
        elif isinstance(action, MessageAction):
            # 消息动作不需要执行，直接返回成功观察
            return CmdOutputObservation(
                content=f"Message sent: {action.content}",
                command="message",
                exit_code=0
            )
        else:
            return ErrorObservation(
                content=f"Unknown action type: {type(action).__name__}",
                error_type="action_error"
            )
    
    async def _execute_command(self, action: CmdRunAction) -> Observation:
        """执行命令"""
        command = action.command
        
        # 模拟命令执行
        if command == "ls -la":
            output = """total 8
drwxr-xr-x 2 user user 4096 Jan 1 12:00 .
drwxr-xr-x 3 user user 4096 Jan 1 12:00 ..
-rw-r--r-- 1 user user   42 Jan 1 12:00 agent_output.txt"""
        elif command == "pwd":
            output = "/tmp"
        elif command == "date":
            import datetime
            output = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elif command.startswith("echo"):
            output = command[5:]  # 去掉 "echo "
        else:
            output = f"Command '{command}' executed successfully"
        
        return CmdOutputObservation(
            content=output,
            command=command,
            exit_code=0
        )
    
    async def _edit_file(self, action: FileEditAction) -> Observation:
        """编辑文件"""
        self.files[action.path] = action.content
        
        return FileReadObservation(
            content=f"File {action.path} written successfully",
            path=action.path
        )

class AgentController:
    """代理控制器"""
    
    def __init__(self, agent: CustomAgent, runtime: MockRuntime):
        self.agent = agent
        self.runtime = runtime
    
    async def run_agent(self, initial_message: str, max_iterations: int = 10) -> State:
        """运行代理"""
        state = State(history=[], max_iterations=max_iterations)
        
        # 添加初始消息
        initial_action = MessageAction(content=f"User: {initial_message}")
        state.add_event(initial_action)
        
        print(f"🚀 开始运行代理: {self.agent.name}")
        print(f"📝 初始任务: {initial_message}")
        print("=" * 60)
        
        for iteration in range(max_iterations):
            state.iteration = iteration
            
            print(f"\n🔄 迭代 {iteration + 1}/{max_iterations}")
            
            # 代理决策
            action = await self.agent.step(state)
            print(f"🤖 代理动作: {action}")
            
            state.add_event(action)
            
            # 检查是否完成
            if isinstance(action, AgentFinishAction):
                print(f"✅ 任务完成: {action.outputs}")
                break
            
            # 执行动作
            observation = await self.runtime.execute_action(action)
            print(f"👁️ 环境观察: {observation}")
            
            state.add_event(observation)
            
            # 添加延迟
            await asyncio.sleep(0.5)
        
        print(f"\n📊 运行完成，共执行 {state.iteration + 1} 次迭代")
        return state

class ConversationManager:
    """对话管理器"""
    
    def __init__(self, controller: AgentController):
        self.controller = controller
        self.conversation_history = []
    
    async def start_interactive_session(self):
        """开始交互式会话"""
        print("🎯 OpenHands自定义代理交互式会话")
        print("输入 'quit' 退出，'help' 查看帮助")
        print("=" * 50)
        
        while True:
            try:
                user_input = input("\n👤 你: ").strip()
                
                if user_input.lower() == 'quit':
                    print("👋 再见！")
                    break
                elif user_input.lower() == 'help':
                    self._show_help()
                    continue
                elif not user_input:
                    continue
                
                # 运行代理
                state = await self.controller.run_agent(user_input, max_iterations=5)
                
                # 保存对话
                self.conversation_history.append({
                    "user_input": user_input,
                    "agent_response": self._extract_agent_response(state),
                    "events": [str(event) for event in state.history]
                })
                
            except KeyboardInterrupt:
                print("\n👋 会话被中断，再见！")
                break
            except Exception as e:
                print(f"❌ 发生错误: {e}")
    
    def _show_help(self):
        """显示帮助信息"""
        help_text = """
🆘 帮助信息:

可用命令示例:
- "执行 ls 命令" - 执行shell命令
- "创建一个文件" - 创建或编辑文件
- "你好" - 简单对话
- "完成任务" - 结束当前任务

代理能力:
✅ 执行shell命令
✅ 文件操作
✅ 对话交互
✅ 任务完成判断
        """
        print(help_text)
    
    def _extract_agent_response(self, state: State) -> str:
        """提取代理响应"""
        for event in reversed(state.history):
            if isinstance(event, MessageAction) and not event.content.startswith("User:"):
                return event.content
        return "代理没有明确回复"
    
    def save_conversation(self, filename: str):
        """保存对话历史"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
        print(f"💾 对话历史已保存到 {filename}")

async def demo_agent_capabilities():
    """演示代理能力"""
    print("🎪 OpenHands自定义代理能力演示")
    print("=" * 50)
    
    # 创建组件
    llm = MockLLM()
    agent = CustomAgent(llm, "DemoAgent")
    runtime = MockRuntime()
    controller = AgentController(agent, runtime)
    
    # 测试场景
    test_scenarios = [
        "你好，请介绍一下你自己",
        "执行 ls 命令查看当前目录",
        "创建一个包含当前时间的文件",
        "执行 date 命令",
        "任务完成，请结束"
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🎬 场景 {i}: {scenario}")
        print("-" * 40)
        
        state = await controller.run_agent(scenario, max_iterations=3)
        
        # 显示结果摘要
        actions = [e for e in state.history if isinstance(e, Action)]
        observations = [e for e in state.history if isinstance(e, Observation)]
        
        print(f"📈 结果摘要:")
        print(f"   动作数量: {len(actions)}")
        print(f"   观察数量: {len(observations)}")
        print(f"   迭代次数: {state.iteration + 1}")

async def main():
    """主函数"""
    print("🤖 OpenHands自定义代理项目")
    print("选择运行模式:")
    print("1. 能力演示")
    print("2. 交互式会话")
    
    try:
        choice = input("请选择 (1 或 2): ").strip()
        
        if choice == "1":
            await demo_agent_capabilities()
        elif choice == "2":
            # 创建组件
            llm = MockLLM()
            agent = CustomAgent(llm, "InteractiveAgent")
            runtime = MockRuntime()
            controller = AgentController(agent, runtime)
            conversation_manager = ConversationManager(controller)
            
            # 开始交互式会话
            await conversation_manager.start_interactive_session()
            
            # 保存对话
            conversation_manager.save_conversation("custom_agent_conversation.json")
        else:
            print("❌ 无效选择")
    
    except KeyboardInterrupt:
        print("\n👋 程序被中断，再见！")

if __name__ == "__main__":
    asyncio.run(main())

"""
🎯 学习要点:

1. **OpenHands架构**: 理解核心组件
   - Agent: 决策制定者
   - Action: 代理的行为
   - Observation: 环境反馈
   - State: 当前状态
   - Runtime: 执行环境

2. **事件驱动设计**: 掌握事件系统
   - 事件类型定义
   - 事件流处理
   - 状态管理

3. **代理控制循环**: 理解代理运行机制
   - 感知-思考-行动循环
   - 迭代控制
   - 终止条件

4. **工具集成**: 学习工具系统设计
   - 命令执行
   - 文件操作
   - 错误处理

📝 练习任务:

1. 添加更多动作类型（如网络请求、数据库操作）
2. 实现更复杂的LLM集成
3. 添加代理记忆系统
4. 实现多代理协作
5. 添加安全检查机制

🚀 扩展方向:

1. 集成真实的OpenHands组件
2. 实现自定义工具插件
3. 添加代理性能监控
4. 实现代理学习能力
5. 支持多模态输入

💡 实际应用:

1. 在OpenHands项目中创建自定义代理
2. 为特定任务优化代理行为
3. 集成企业内部工具
4. 实现专业领域代理
5. 构建代理测试框架

🔧 OpenHands集成步骤:

1. 继承openhands.controller.agent.Agent
2. 实现step方法
3. 注册代理类型
4. 配置代理参数
5. 测试和部署
"""