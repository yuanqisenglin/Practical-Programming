"""
词法分析器（Lexer）
将DSL脚本文件解析为Token序列
"""

from typing import List, Optional
from enum import Enum
import re


class TokenType(Enum):
    """Token类型枚举"""
    # 关键字
    STEP = "STEP"
    SPEAK = "SPEAK"
    LISTEN = "LISTEN"
    BRANCH = "BRANCH"
    SET = "SET"
    END = "END"
    
    # 标识符和字面量
    IDENTIFIER = "IDENTIFIER"
    STRING = "STRING"
    NUMBER = "NUMBER"
    
    # 运算符和分隔符
    LBRACE = "LBRACE"      # {
    RBRACE = "RBRACE"      # }
    EQUALS = "EQUALS"       # =
    ARROW = "ARROW"         # ->
    EQ = "EQ"              # ==
    NE = "NE"              # !=
    
    # 其他
    NEWLINE = "NEWLINE"
    EOF = "EOF"
    UNKNOWN = "UNKNOWN"


class Token:
    """Token类：表示词法单元"""
    
    def __init__(self, token_type: TokenType, value: str, line_number: int = 0, column: int = 0):
        self.token_type = token_type
        self.value = value
        self.line_number = line_number
        self.column = column
    
    def __repr__(self):
        return f"Token({self.token_type.value}, '{self.value}', line={self.line_number})"
    
    def __eq__(self, other):
        if not isinstance(other, Token):
            return False
        return (self.token_type == other.token_type and 
                self.value == other.value)


class Lexer:
    """词法分析器"""
    
    # 关键字映射
    KEYWORDS = {
        'step': TokenType.STEP,
        'speak': TokenType.SPEAK,
        'listen': TokenType.LISTEN,
        'branch': TokenType.BRANCH,
        'set': TokenType.SET,
        'end': TokenType.END,
    }
    
    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line_number = 1
        self.column = 0
        self.tokens: List[Token] = []
    
    def current_char(self) -> Optional[str]:
        """获取当前字符"""
        if self.position >= len(self.source):
            return None
        return self.source[self.position]
    
    def peek_char(self, offset: int = 1) -> Optional[str]:
        """向前查看字符"""
        pos = self.position + offset
        if pos >= len(self.source):
            return None
        return self.source[pos]
    
    def advance(self) -> Optional[str]:
        """前进一个字符"""
        if self.position >= len(self.source):
            return None
        
        char = self.source[self.position]
        self.position += 1
        
        if char == '\n':
            self.line_number += 1
            self.column = 0
        else:
            self.column += 1
        
        return char
    
    def skip_whitespace(self):
        """跳过空白字符（除了换行符）"""
        while self.current_char() and self.current_char() in ' \t\r':
            self.advance()
    
    def skip_comment(self):
        """跳过注释（以#开头的行）"""
        if self.current_char() == '#':
            while self.current_char() and self.current_char() != '\n':
                self.advance()
    
    def read_string(self) -> str:
        """读取字符串字面量（双引号包围）"""
        quote_char = self.current_char()  # 应该是 " 或 '
        self.advance()  # 跳过开始引号
        
        value = ""
        while self.current_char() and self.current_char() != quote_char:
            if self.current_char() == '\\':
                self.advance()
                if self.current_char() == 'n':
                    value += '\n'
                elif self.current_char() == 't':
                    value += '\t'
                elif self.current_char() == '\\':
                    value += '\\'
                elif self.current_char() == quote_char:
                    value += quote_char
                else:
                    value += self.current_char()
                self.advance()
            else:
                value += self.current_char()
                self.advance()
        
        if self.current_char() == quote_char:
            self.advance()  # 跳过结束引号
        
        return value
    
    def read_number(self) -> str:
        """读取数字"""
        value = ""
        while self.current_char() and (self.current_char().isdigit() or self.current_char() == '.'):
            value += self.current_char()
            self.advance()
        return value
    
    def read_identifier(self) -> str:
        """读取标识符"""
        value = ""
        while self.current_char() and (self.current_char().isalnum() or self.current_char() == '_'):
            value += self.current_char()
            self.advance()
        return value
    
    def tokenize(self) -> List[Token]:
        """执行词法分析，返回Token列表"""
        self.tokens = []
        self.position = 0
        self.line_number = 1
        self.column = 0
        
        while self.position < len(self.source):
            self.skip_whitespace()
            
            if not self.current_char():
                break
            
            # 跳过注释
            if self.current_char() == '#':
                self.skip_comment()
                continue
            
            # 换行符
            if self.current_char() == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, '\n', self.line_number, self.column))
                self.advance()
                continue
            
            char = self.current_char()
            start_line = self.line_number
            start_column = self.column
            
            # 字符串字面量
            if char in ('"', "'"):
                value = self.read_string()
                self.tokens.append(Token(TokenType.STRING, value, start_line, start_column))
                continue
            
            # 数字
            if char.isdigit():
                value = self.read_number()
                self.tokens.append(Token(TokenType.NUMBER, value, start_line, start_column))
                continue
            
            # 标识符或关键字
            if char.isalpha() or char == '_':
                value = self.read_identifier()
                token_type = self.KEYWORDS.get(value.lower(), TokenType.IDENTIFIER)
                self.tokens.append(Token(token_type, value, start_line, start_column))
                continue
            
            # 运算符和分隔符
            if char == '{':
                self.tokens.append(Token(TokenType.LBRACE, '{', start_line, start_column))
                self.advance()
            elif char == '}':
                self.tokens.append(Token(TokenType.RBRACE, '}', start_line, start_column))
                self.advance()
            elif char == '=':
                if self.peek_char() == '=':
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.EQ, '==', start_line, start_column))
                else:
                    self.tokens.append(Token(TokenType.EQUALS, '=', start_line, start_column))
                    self.advance()
            elif char == '!':
                if self.peek_char() == '=':
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.NE, '!=', start_line, start_column))
                else:
                    self.tokens.append(Token(TokenType.UNKNOWN, char, start_line, start_column))
                    self.advance()
            elif char == '-' and self.peek_char() == '>':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.ARROW, '->', start_line, start_column))
            else:
                # 未知字符
                self.tokens.append(Token(TokenType.UNKNOWN, char, start_line, start_column))
                self.advance()
        
        # 添加EOF标记
        self.tokens.append(Token(TokenType.EOF, '', self.line_number, self.column))
        
        return self.tokens

