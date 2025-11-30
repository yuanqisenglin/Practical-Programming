"""
语法分析器测试
"""

import unittest
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.dsl.lexer import Lexer
from src.dsl.parser import Parser, ParseError
from src.dsl.ast import StepNode, SpeakNode, ListenNode, BranchNode, SetNode, EndNode


class TestParser(unittest.TestCase):
    """语法分析器测试类"""
    
    def test_parse_simple_step(self):
        """测试解析简单Step"""
        source = '''
step start {
    speak "hello"
    end
}
'''
        lexer = Lexer(source)
        parser = Parser(lexer)
        script = parser.parse()
        
        self.assertEqual(len(script.steps), 1)
        self.assertEqual(script.steps[0].name, "start")
        self.assertEqual(len(script.steps[0].statements), 2)
        self.assertIsInstance(script.steps[0].statements[0], SpeakNode)
        self.assertIsInstance(script.steps[0].statements[1], EndNode)
    
    def test_parse_listen(self):
        """测试解析Listen语句"""
        source = '''
step start {
    listen user_input
}
'''
        lexer = Lexer(source)
        parser = Parser(lexer)
        script = parser.parse()
        
        listen_node = script.steps[0].statements[0]
        self.assertIsInstance(listen_node, ListenNode)
        self.assertEqual(listen_node.variable, "user_input")
    
    def test_parse_branch(self):
        """测试解析Branch语句"""
        source = '''
step start {
    branch user_intent == "订单查询" -> query_order
}
'''
        lexer = Lexer(source)
        parser = Parser(lexer)
        script = parser.parse()
        
        branch_node = script.steps[0].statements[0]
        self.assertIsInstance(branch_node, BranchNode)
        self.assertEqual(branch_node.condition, 'user_intent == "订单查询"')
        self.assertEqual(branch_node.target_step, "query_order")
    
    def test_parse_set(self):
        """测试解析Set语句"""
        source = '''
step start {
    set count = 10
    set message = "hello"
}
'''
        lexer = Lexer(source)
        parser = Parser(lexer)
        script = parser.parse()
        
        set_nodes = [s for s in script.steps[0].statements if isinstance(s, SetNode)]
        self.assertEqual(len(set_nodes), 2)
        self.assertEqual(set_nodes[0].variable, "count")
        self.assertEqual(set_nodes[0].value, 10)
        self.assertEqual(set_nodes[1].variable, "message")
        self.assertEqual(set_nodes[1].value, "hello")
    
    def test_parse_multiple_steps(self):
        """测试解析多个Step"""
        source = '''
step start {
    speak "hello"
}
step query {
    listen input
}
'''
        lexer = Lexer(source)
        parser = Parser(lexer)
        script = parser.parse()
        
        self.assertEqual(len(script.steps), 2)
        self.assertEqual(script.steps[0].name, "start")
        self.assertEqual(script.steps[1].name, "query")
    
    def test_parse_error_missing_brace(self):
        """测试解析错误：缺少大括号"""
        source = 'step start { speak "hello"'
        lexer = Lexer(source)
        parser = Parser(lexer)
        
        with self.assertRaises(ParseError):
            parser.parse()
    
    def test_parse_error_invalid_branch(self):
        """测试解析错误：无效的分支条件"""
        source = 'step start { branch invalid -> target }'
        lexer = Lexer(source)
        parser = Parser(lexer)
        
        with self.assertRaises(ParseError):
            parser.parse()


if __name__ == '__main__':
    unittest.main()

