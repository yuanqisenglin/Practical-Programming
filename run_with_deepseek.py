"""
使用 DeepSeek API 运行示例脚本
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.main import AgentSystem, interactive_mode

# DeepSeek API 配置
DEEPSEEK_API_KEY = "sk-78c61c5b0f1347ccb4508f7bb6cb216d"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

def main():
    """使用 DeepSeek API 运行脚本"""
    import argparse
    
    parser = argparse.ArgumentParser(description="使用 DeepSeek API 运行 DSL 脚本")
    parser.add_argument("--script", "-s", default="scripts/order_inquiry.dsl", 
                       help="DSL脚本文件路径（默认：scripts/order_inquiry.dsl）")
    parser.add_argument("--user-id", default="default", help="用户ID（默认：default）")
    
    args = parser.parse_args()
    
    # 检查脚本文件是否存在
    if not os.path.exists(args.script):
        print(f"错误：脚本文件不存在: {args.script}")
        sys.exit(1)
    
    try:
        print("=" * 60)
        print("使用 DeepSeek API 运行智能客服系统")
        print("=" * 60)
        print(f"API: {DEEPSEEK_BASE_URL}")
        print(f"模型: {DEEPSEEK_MODEL}")
        print("=" * 60)
        print()
        
        # 创建Agent系统（不使用模拟模式，使用真实的 DeepSeek API）
        agent = AgentSystem(
            args.script, 
            use_mock_llm=False,  # 使用真实 API
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
            model=DEEPSEEK_MODEL
        )
        
        # 进入交互模式
        interactive_mode(agent, args.user_id)
    
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

