# OpenHands 开发环境设置指南

## 🛠️ 环境准备

### 1. 系统要求
- Linux, macOS, 或 Windows WSL2 (Ubuntu >= 22.04)
- Python 3.12
- Node.js >= 20.0.0
- Docker
- Poetry >= 1.8

### 2. 快速安装脚本

```bash
#!/bin/bash
# OpenHands开发环境一键安装脚本

echo "🚀 开始安装OpenHands开发环境..."

# 检查并安装Python 3.12
if ! command -v python3.12 &> /dev/null; then
    echo "安装Python 3.12..."
    sudo apt update
    sudo apt install -y python3.12 python3.12-dev python3.12-venv
fi

# 安装Poetry
if ! command -v poetry &> /dev/null; then
    echo "安装Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
fi

# 安装Node.js
if ! command -v node &> /dev/null; then
    echo "安装Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

# 安装Docker
if ! command -v docker &> /dev/null; then
    echo "安装Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
fi

echo "✅ 基础环境安装完成！"
```

### 3. 克隆和构建项目

```bash
# 克隆项目
git clone https://github.com/All-Hands-AI/OpenHands.git
cd OpenHands

# 安装Python依赖
poetry install

# 安装前端依赖
cd frontend
npm install
cd ..

# 构建项目
make build
```

## 🔧 开发工作流

### 1. 启动开发服务器

```bash
# 启动后端开发服务器
make start-backend

# 启动前端开发服务器 (新终端)
make start-frontend
```

### 2. 运行测试

```bash
# 运行Python测试
poetry run pytest

# 运行前端测试
cd frontend && npm test

# 运行端到端测试
cd frontend && npm run test:e2e
```

### 3. 代码质量检查

```bash
# Python代码格式化和检查
poetry run black .
poetry run flake8 .
poetry run mypy .

# 前端代码检查
cd frontend && npm run lint
```

## 🧪 实验和学习项目

### 项目1: 创建自定义Agent

```python
# 文件: openhands/agenthub/my_agent/my_agent.py

from openhands.controller.agent import Agent
from openhands.controller.state.state import State
from openhands.core.config import AgentConfig
from openhands.events.action import Action, MessageAction
from openhands.llm.llm import LLM

class MyCustomAgent(Agent):
    """
    自定义AI代理示例
    """
    
    def __init__(self, llm: LLM, config: AgentConfig):
        super().__init__(llm, config)
        self.name = "MyCustomAgent"
    
    def step(self, state: State) -> Action:
        """
        代理的核心逻辑
        """
        # 获取最新的用户消息
        latest_user_message = state.get_latest_user_message()
        
        # 简单的响应逻辑
        if latest_user_message:
            response = f"我收到了你的消息: {latest_user_message}"
            return MessageAction(content=response)
        
        return MessageAction(content="你好！我是自定义代理。")
```

### 项目2: 添加新工具

```python
# 文件: openhands/agenthub/codeact_agent/tools/my_tool.py

from typing import Any, Dict
from litellm import ChatCompletionToolParam

def create_my_custom_tool() -> ChatCompletionToolParam:
    """
    创建自定义工具
    """
    return {
        "type": "function",
        "function": {
            "name": "my_custom_tool",
            "description": "这是我的自定义工具",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_text": {
                        "type": "string",
                        "description": "输入文本"
                    }
                },
                "required": ["input_text"]
            }
        }
    }

def execute_my_custom_tool(input_text: str) -> Dict[str, Any]:
    """
    执行自定义工具逻辑
    """
    # 在这里实现你的工具逻辑
    result = f"处理结果: {input_text.upper()}"
    
    return {
        "success": True,
        "result": result
    }
```

### 项目3: 事件处理扩展

```python
# 文件: my_event_handler.py

from openhands.events.event import Event
from openhands.events.action import Action
from openhands.events.observation import Observation

class CustomEventHandler:
    """
    自定义事件处理器
    """
    
    def __init__(self):
        self.event_history = []
    
    def handle_event(self, event: Event):
        """
        处理事件
        """
        self.event_history.append(event)
        
        if isinstance(event, Action):
            self.handle_action(event)
        elif isinstance(event, Observation):
            self.handle_observation(event)
    
    def handle_action(self, action: Action):
        """
        处理动作事件
        """
        print(f"处理动作: {action.__class__.__name__}")
        # 添加自定义逻辑
    
    def handle_observation(self, observation: Observation):
        """
        处理观察事件
        """
        print(f"处理观察: {observation.__class__.__name__}")
        # 添加自定义逻辑
```

## 📊 性能监控和调试

### 1. 日志配置

```python
# 文件: debug_config.py

import logging
from openhands.core.logger import openhands_logger

# 设置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 启用OpenHands详细日志
openhands_logger.setLevel(logging.DEBUG)
```

### 2. 性能分析

```python
# 文件: performance_monitor.py

import time
import psutil
from functools import wraps

def monitor_performance(func):
    """
    性能监控装饰器
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        print(f"函数 {func.__name__}:")
        print(f"  执行时间: {end_time - start_time:.2f}秒")
        print(f"  内存使用: {end_memory - start_memory:.2f}MB")
        
        return result
    return wrapper

# 使用示例
@monitor_performance
def my_function():
    # 你的代码
    pass
```

## 🔍 调试技巧

### 1. 使用调试器

```python
# 在代码中添加断点
import pdb; pdb.set_trace()

# 或使用ipdb (更友好的界面)
import ipdb; ipdb.set_trace()
```

### 2. 事件重放调试

```python
# 文件: debug_replay.py

from openhands.controller.replay import ReplayManager
from openhands.core.config import OpenHandsConfig

def debug_session(session_id: str):
    """
    调试特定会话
    """
    config = OpenHandsConfig()
    replay_manager = ReplayManager(config)
    
    # 重放会话事件
    events = replay_manager.get_session_events(session_id)
    
    for event in events:
        print(f"事件类型: {event.__class__.__name__}")
        print(f"事件内容: {event}")
        print("-" * 50)
```

## 🚀 部署和发布

### 1. Docker构建

```dockerfile
# 自定义Dockerfile
FROM python:3.12-slim

WORKDIR /app

# 复制依赖文件
COPY pyproject.toml poetry.lock ./

# 安装依赖
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

# 复制源代码
COPY . .

# 启动命令
CMD ["python", "-m", "openhands.server.listen"]
```

### 2. 环境配置

```bash
# .env文件示例
LLM_MODEL=anthropic/claude-3-sonnet-20240229
LLM_API_KEY=your_api_key_here
SANDBOX_RUNTIME_CONTAINER_IMAGE=docker.all-hands.dev/all-hands-ai/runtime:0.41-nikolaik
LOG_LEVEL=INFO
```

## 📚 学习资源

### 1. 代码阅读顺序建议

1. `openhands/core/main.py` - 主入口点
2. `openhands/controller/agent.py` - 代理基类
3. `openhands/agenthub/codeact_agent/` - 具体代理实现
4. `openhands/events/` - 事件系统
5. `openhands/runtime/` - 运行时环境
6. `openhands/server/` - Web服务器

### 2. 重要概念理解

- **Agent**: AI代理的抽象基类
- **Action**: 代理执行的动作
- **Observation**: 环境的反馈
- **State**: 当前会话状态
- **Runtime**: 代码执行环境
- **Event**: 系统中的事件

### 3. 贡献指南

```bash
# 创建功能分支
git checkout -b feature/my-new-feature

# 提交更改
git add .
git commit -m "添加新功能: 描述"

# 推送分支
git push origin feature/my-new-feature

# 创建Pull Request
```

## 🎯 下一步行动

1. **设置开发环境** - 按照上述步骤配置
2. **阅读核心代码** - 理解项目架构
3. **实现小项目** - 从简单的自定义Agent开始
4. **参与社区** - 加入Slack/Discord讨论
5. **贡献代码** - 提交Pull Request

记住：学习是一个渐进的过程，从小项目开始，逐步深入！