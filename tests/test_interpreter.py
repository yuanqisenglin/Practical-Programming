"""
解释器测试
"""

import unittest
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.dsl.lexer import Lexer
from src.dsl.parser import Parser
from src.dsl.interpreter import Interpreter
from src.runtime.execution_context import ExecutionContext


class TestInterpreter(unittest.TestCase):
    """解释器测试类"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建简单的测试脚本
        source = '''
step start {
    speak "欢迎"
    listen user_input
    branch user_intent == "查询" -> query
    speak "未识别"
    end
}
step query {
    speak "查询中"
    end
}
'''
        lexer = Lexer(source)
        parser = Parser(lexer)
        self.script = parser.parse()
    
    def test_execute_speak(self):
        """测试执行Speak语句"""
        interpreter = Interpreter(self.script)
        context = ExecutionContext("test_user")
        
        result = interpreter.execute(context)
        # 执行speak后会继续执行到listen，如果没有input_callback会返回waiting_input
        # 但消息中应该包含speak的内容
        self.assertEqual(result["status"], "waiting_input")
        # 消息应该包含"欢迎"（来自speak）和"等待用户输入"（来自listen）
        message = result.get("message", "")
        self.assertIn("欢迎", message)
    
    def test_execute_branch_true(self):
        """测试执行Branch语句（条件为真）"""
        interpreter = Interpreter(self.script)
        context = ExecutionContext("test_user")
        context.set_variable("user_intent", "查询")
        
        # 模拟输入回调
        def input_callback(prompt):
            return "查询订单"
        
        result = interpreter.execute(context, input_callback)
        # 应该跳转到query步骤
        self.assertEqual(context.get_current_step(), "query")
    
    def test_execute_branch_false(self):
        """测试执行Branch语句（条件为假）"""
        interpreter = Interpreter(self.script)
        context = ExecutionContext("test_user")
        context.set_variable("user_intent", "其他")
        
        def input_callback(prompt):
            return "其他"
        
        result = interpreter.execute(context, input_callback)
        # 不应该跳转，应该继续执行
        self.assertNotEqual(context.get_current_step(), "query")
    
    def test_execute_set(self):
        """测试执行Set语句"""
        source = '''
step start {
    set count = 10
    set message = "hello"
    end
}
'''
        lexer = Lexer(source)
        parser = Parser(lexer)
        script = parser.parse()
        
        interpreter = Interpreter(script)
        context = ExecutionContext("test_user")
        
        interpreter.execute(context)
        
        self.assertEqual(context.get_variable("count"), 10)
        self.assertEqual(context.get_variable("message"), "hello")
    
    def test_variable_substitution(self):
        """测试变量替换"""
        source = '''
step start {
    set name = "张三"
    speak "你好，${name}"
    end
}
'''
        lexer = Lexer(source)
        parser = Parser(lexer)
        script = parser.parse()
        
        interpreter = Interpreter(script)
        context = ExecutionContext("test_user")
        
        result = interpreter.execute(context)
        # 执行完speak后执行end，应该返回speak的消息
        message = result.get("message", "")
        self.assertIn("张三", message)


if __name__ == '__main__':
    unittest.main()

