"""
快速运行示例脚本
用于演示系统功能
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.main import AgentSystem, interactive_mode

if __name__ == "__main__":
    # 使用模拟LLM运行订单查询场景
    print("正在加载订单查询场景脚本...")
    agent = AgentSystem("scripts/order_inquiry.dsl", use_mock_llm=True)
    print("脚本加载成功！\n")
    
    # 进入交互模式
    interactive_mode(agent, "demo_user")

