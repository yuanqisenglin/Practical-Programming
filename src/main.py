"""
主程序入口
整合DSL解释器、LLM意图识别和多线程支持
"""

import argparse
import sys
import os
import threading
from typing import Optional, Callable
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.dsl.lexer import Lexer
from src.dsl.parser import Parser
from src.dsl.interpreter import Interpreter
from src.runtime.execution_context import ContextManager
from src.llm.intent_analyzer import IntentAnalyzer, MockIntentAnalyzer

# 尝试导入配置文件（如果存在）
try:
    import config
    DEFAULT_API_KEY = getattr(config, 'DEFAULT_API_KEY', None)
    DEFAULT_BASE_URL = getattr(config, 'DEFAULT_BASE_URL', None)
    DEFAULT_MODEL = getattr(config, 'DEFAULT_MODEL', None)
except ImportError:
    DEFAULT_API_KEY = None
    DEFAULT_BASE_URL = None
    DEFAULT_MODEL = None


class AgentSystem:
    """Agent系统：管理多个用户的对话"""
    
    def __init__(self, script_path: str, use_mock_llm: bool = False, api_key: Optional[str] = None, 
                 base_url: Optional[str] = None, model: Optional[str] = None):
        """
        初始化Agent系统
        
        Args:
            script_path: DSL脚本文件路径
            use_mock_llm: 是否使用模拟LLM（用于测试）
            api_key: LLM API密钥
            base_url: API基础URL（用于DeepSeek等兼容OpenAI的API）
            model: 使用的模型名称
        """
        # 读取并解析脚本
        with open(script_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        lexer = Lexer(script_content)
        parser = Parser(lexer)
        self.script = parser.parse()
        
        # 初始化意图识别器
        if use_mock_llm:
            self.intent_analyzer = MockIntentAnalyzer()
        else:
            try:
                self.intent_analyzer = IntentAnalyzer(api_key=api_key, base_url=base_url, model=model)
            except Exception as e:
                print(f"警告：无法初始化LLM接口，使用模拟模式。错误：{e}")
                self.intent_analyzer = MockIntentAnalyzer()
        
        # 创建意图识别包装函数
        def analyze_intent(user_input: str) -> dict:
            # 包含所有可能的意图，确保意图识别器能正确识别
            intents = [
                "返回主菜单",  # 操作类意图，优先
                "查看订单详情",
                "查看物流信息",
                "重新查询",
                "重新申请",
                "商品质量问题",
                "商品与描述不符",
                "不需要了",
                "其他原因",
                "查询进度",
                "查询投诉",
                "提交投诉",
                "提交建议",
                "物流查询",
                "退款申请",
                "订单查询",
                "产品咨询",
                "投诉建议"
            ]
            return self.intent_analyzer.analyze(user_input, intents)
        
        # 创建解释器
        self.interpreter = Interpreter(self.script, analyze_intent)
        
        # 上下文管理器
        self.context_manager = ContextManager()
        
        # 线程锁
        self.lock = threading.Lock()
    
    def process_user_input(self, user_id: str, user_input: Optional[str] = None) -> dict:
        """
        处理用户输入
        
        Args:
            user_id: 用户ID
            user_input: 用户输入（如果为None，则继续执行当前流程）
        
        Returns:
            执行结果字典
        """
        # 获取或创建用户上下文
        context = self.context_manager.get_context(user_id)
        
        # 如果提供了用户输入，设置为待处理输入
        if user_input:
            context.set_pending_input(user_input)
            context.set_variable("last_input", user_input)
            # 重置输入使用标志，允许新的输入被使用
            # 注意：这里不直接重置，因为set_pending_input已经处理了
        
        # 定义输入回调函数
        def input_callback(prompt: str) -> str:
            # 尝试获取并消费待处理的输入（只能使用一次）
            pending = context.get_and_consume_input()
            if pending:
                return pending
            # 如果没有待处理的输入，返回空字符串（表示等待输入）
            return ""
        
        # 执行解释器
        result = self.interpreter.execute(context, input_callback)
        
        return result
    
    def start_conversation(self, user_id: str = "default"):
        """开始一个新对话"""
        context = self.context_manager.get_context(user_id)
        context.clear()
        return self.process_user_input(user_id)


def interactive_mode(agent: AgentSystem, user_id: str = "default"):
    """交互模式：命令行交互"""
    print("=" * 60)
    print("智能客服Agent系统")
    print("=" * 60)
    print("输入 'quit' 或 'exit' 退出\n")
    
    # 开始对话
    result = agent.start_conversation(user_id)
    print(result.get("message", ""))
    
    while True:
        try:
            # 获取用户输入
            user_input = input("您: ").strip()
            
            if user_input.lower() in ('quit', 'exit', 'q'):
                print("再见！")
                break
            
            if not user_input:
                continue
            
            # 处理用户输入
            result = agent.process_user_input(user_id, user_input)
            
            # 显示结果
            if result.get("status") == "waiting_input":
                print("系统: " + result.get("message", "等待输入..."))
            elif result.get("status") == "finished":
                # 显示最后的消息
                message = result.get("message", "对话结束")
                if message:
                    lines = message.split('\n')
                    for line in lines:
                        if line.strip():
                            print("系统: " + line)
                # 不立即退出，允许用户继续对话
                # break  # 注释掉，让用户可以继续输入
            elif result.get("status") == "error":
                print("错误: " + result.get("message", "未知错误"))
                break
            else:
                message = result.get("message", "")
                if message:
                    # 分割多行消息，逐行显示
                    lines = message.split('\n')
                    for line in lines:
                        if line.strip():  # 只显示非空行
                            print("系统: " + line)
                
                # 如果状态是running但需要继续，继续执行（只处理当前输入后的连续执行）
                if result.get("status") == "running":
                    # 继续执行直到需要用户输入或结束
                    # 注意：这里不传入新的user_input，让系统自然执行到下一个listen
                    max_iterations = 20  # 减少迭代次数，避免过度执行
                    iteration = 0
                    last_messages = set()  # 用于去重，避免重复显示相同消息
                    while iteration < max_iterations:
                        iteration += 1
                        # 不传入新输入，让系统继续执行
                        next_result = agent.process_user_input(user_id, None)
                        if next_result.get("status") == "waiting_input":
                            # 需要新的用户输入，停止循环，等待用户输入
                            print("系统: " + next_result.get("message", "等待输入..."))
                            break
                        elif next_result.get("status") == "finished":
                            # 步骤执行完毕，显示消息但不退出
                            msg = next_result.get("message", "对话结束")
                            if msg:
                                lines = msg.split('\n')
                                for line in lines:
                                    if line.strip():
                                        print("系统: " + line)
                            break  # 停止循环，等待新的用户输入
                        elif next_result.get("status") == "error":
                            print("错误: " + next_result.get("message", "未知错误"))
                            return
                        else:
                            msg = next_result.get("message", "")
                            if msg:
                                # 检查是否已经显示过这条消息
                                msg_hash = hash(msg)
                                if msg_hash not in last_messages:
                                    last_messages.add(msg_hash)
                                    # 分割多行消息，逐行显示
                                    lines = msg.split('\n')
                                    for line in lines:
                                        if line.strip():  # 只显示非空行
                                            print("系统: " + line)
                            # 如果状态不是running，停止循环
                            if next_result.get("status") != "running":
                                break
                    
                    if iteration >= max_iterations:
                        print("错误: 执行超时，可能存在无限循环")
                        break
        
        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"错误: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="基于DSL的多业务场景Agent系统")
    parser.add_argument("--script", "-s", required=True, help="DSL脚本文件路径")
    parser.add_argument("--mock", "-m", action="store_true", help="使用模拟LLM（不调用真实API）")
    parser.add_argument("--api-key", help="LLM API密钥（如果不设置，从环境变量OPENAI_API_KEY或config.py读取）")
    parser.add_argument("--base-url", help="API基础URL（用于DeepSeek等兼容OpenAI的API）")
    parser.add_argument("--model", help="使用的模型名称（DeepSeek使用：deepseek-chat）")
    parser.add_argument("--user-id", default="default", help="用户ID（默认：default）")
    
    args = parser.parse_args()
    
    # 检查脚本文件是否存在
    if not os.path.exists(args.script):
        print(f"错误：脚本文件不存在: {args.script}")
        sys.exit(1)
    
    # 如果没有指定API key，尝试使用配置文件中的默认值
    api_key = args.api_key or DEFAULT_API_KEY
    base_url = args.base_url or DEFAULT_BASE_URL
    model = args.model or DEFAULT_MODEL
    
    try:
        # 创建Agent系统
        agent = AgentSystem(args.script, use_mock_llm=args.mock, api_key=api_key, 
                           base_url=base_url, model=model)
        
        # 进入交互模式
        interactive_mode(agent, args.user_id)
    
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

