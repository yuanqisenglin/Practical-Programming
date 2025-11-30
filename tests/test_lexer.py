"""
词法分析器测试
"""

import unittest
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.dsl.lexer import Lexer, Token, TokenType


class TestLexer(unittest.TestCase):
    """词法分析器测试类"""
    
    def test_basic_tokens(self):
        """测试基本Token识别"""
        source = 'step start { speak "hello" }'
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        self.assertEqual(tokens[0].token_type, TokenType.STEP)
        self.assertEqual(tokens[1].token_type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[2].token_type, TokenType.LBRACE)
        self.assertEqual(tokens[3].token_type, TokenType.SPEAK)
        self.assertEqual(tokens[4].token_type, TokenType.STRING)
        self.assertEqual(tokens[4].value, "hello")
        self.assertEqual(tokens[5].token_type, TokenType.RBRACE)
    
    def test_string_with_escape(self):
        """测试转义字符串"""
        source = 'speak "hello\\nworld"'
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        string_token = [t for t in tokens if t.token_type == TokenType.STRING][0]
        self.assertEqual(string_token.value, "hello\nworld")
    
    def test_branch_condition(self):
        """测试分支条件Token"""
        source = 'branch user_intent == "订单查询" -> query_order'
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        token_types = [t.token_type for t in tokens if t.token_type != TokenType.EOF]
        self.assertIn(TokenType.BRANCH, token_types)
        self.assertIn(TokenType.EQ, token_types)
        self.assertIn(TokenType.ARROW, token_types)
    
    def test_comments(self):
        """测试注释跳过"""
        source = '# This is a comment\nstep start { }'
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        # 注释应该被跳过
        token_types = [t.token_type for t in tokens]
        self.assertNotIn(TokenType.UNKNOWN, token_types[:5])  # 前几个token不应该有UNKNOWN
    
    def test_numbers(self):
        """测试数字识别"""
        source = 'set count = 123'
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        number_token = [t for t in tokens if t.token_type == TokenType.NUMBER][0]
        self.assertEqual(number_token.value, "123")


if __name__ == '__main__':
    unittest.main()

