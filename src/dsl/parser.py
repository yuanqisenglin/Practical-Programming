"""
语法分析器（Parser）
将Token序列解析为抽象语法树（AST）
"""

from typing import List, Optional
from src.dsl.lexer import Lexer, Token, TokenType
from src.dsl.ast import (
    ASTNode, ScriptNode, StepNode, SpeakNode, 
    ListenNode, BranchNode, SetNode, EndNode
)


class ParseError(Exception):
    """语法分析错误"""
    def __init__(self, message: str, token: Optional[Token] = None):
        self.message = message
        self.token = token
        if token:
            super().__init__(f"{message} at line {token.line_number}, column {token.column}")
        else:
            super().__init__(message)


class Parser:
    """语法分析器"""
    
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.tokens: List[Token] = []
        self.position = 0
    
    def current_token(self) -> Optional[Token]:
        """获取当前Token"""
        if self.position >= len(self.tokens):
            return None
        return self.tokens[self.position]
    
    def peek_token(self, offset: int = 1) -> Optional[Token]:
        """向前查看Token"""
        pos = self.position + offset
        if pos >= len(self.tokens):
            return None
        return self.tokens[pos]
    
    def advance(self) -> Optional[Token]:
        """前进一个Token"""
        if self.position < len(self.tokens):
            token = self.tokens[self.position]
            self.position += 1
            return token
        return None
    
    def expect(self, token_type: TokenType, error_message: str = None) -> Token:
        """期望下一个Token是指定类型，否则抛出错误"""
        token = self.current_token()
        if not token or token.token_type != token_type:
            msg = error_message or f"Expected {token_type.value}, got {token.token_type.value if token else 'EOF'}"
            raise ParseError(msg, token)
        return self.advance()
    
    def skip_newlines(self):
        """跳过换行符"""
        while self.current_token() and self.current_token().token_type == TokenType.NEWLINE:
            self.advance()
    
    def parse(self) -> ScriptNode:
        """解析整个脚本，返回ScriptNode"""
        # 先进行词法分析
        self.tokens = self.lexer.tokenize()
        self.position = 0
        
        # 跳过开头的换行符
        self.skip_newlines()
        
        # 解析所有Step
        steps: List[StepNode] = []
        while self.current_token() and self.current_token().token_type != TokenType.EOF:
            if self.current_token().token_type == TokenType.STEP:
                step = self.parse_step()
                steps.append(step)
            else:
                raise ParseError(
                    f"Unexpected token: {self.current_token().token_type.value}",
                    self.current_token()
                )
            self.skip_newlines()
        
        return ScriptNode(steps)
    
    def parse_step(self) -> StepNode:
        """解析Step定义"""
        # step <name> {
        token = self.expect(TokenType.STEP, "Expected 'step' keyword")
        line_number = token.line_number
        
        # 获取Step名称
        name_token = self.expect(TokenType.IDENTIFIER, "Expected step name")
        step_name = name_token.value
        
        # 跳过换行符
        self.skip_newlines()
        
        # 期望左大括号
        self.expect(TokenType.LBRACE, "Expected '{' after step name")
        self.skip_newlines()
        
        # 解析Step内的语句
        statements: List[ASTNode] = []
        while self.current_token() and self.current_token().token_type != TokenType.RBRACE:
            self.skip_newlines()
            
            if self.current_token().token_type == TokenType.SPEAK:
                statements.append(self.parse_speak())
            elif self.current_token().token_type == TokenType.LISTEN:
                statements.append(self.parse_listen())
            elif self.current_token().token_type == TokenType.BRANCH:
                statements.append(self.parse_branch())
            elif self.current_token().token_type == TokenType.SET:
                statements.append(self.parse_set())
            elif self.current_token().token_type == TokenType.END:
                statements.append(self.parse_end())
            elif self.current_token().token_type == TokenType.RBRACE:
                break
            else:
                raise ParseError(
                    f"Unexpected statement: {self.current_token().token_type.value}",
                    self.current_token()
                )
            
            self.skip_newlines()
        
        # 期望右大括号
        self.expect(TokenType.RBRACE, "Expected '}' to close step")
        
        return StepNode(step_name, statements, line_number)
    
    def parse_speak(self) -> SpeakNode:
        """解析Speak语句"""
        token = self.expect(TokenType.SPEAK, "Expected 'speak' keyword")
        line_number = token.line_number
        
        # 期望字符串
        string_token = self.expect(TokenType.STRING, "Expected string after 'speak'")
        message = string_token.value
        
        return SpeakNode(message, line_number)
    
    def parse_listen(self) -> ListenNode:
        """解析Listen语句"""
        token = self.expect(TokenType.LISTEN, "Expected 'listen' keyword")
        line_number = token.line_number
        
        # 期望标识符（变量名）
        var_token = self.expect(TokenType.IDENTIFIER, "Expected variable name after 'listen'")
        variable = var_token.value
        
        return ListenNode(variable, line_number)
    
    def parse_branch(self) -> BranchNode:
        """解析Branch语句"""
        token = self.expect(TokenType.BRANCH, "Expected 'branch' keyword")
        line_number = token.line_number
        
        # 解析条件表达式
        # 格式：branch <condition> -> <step_name>
        # condition可以是：variable == "value" 或 variable != "value"
        
        # 读取条件左侧（变量名）
        left_token = self.expect(TokenType.IDENTIFIER, "Expected variable name in branch condition")
        left = left_token.value
        
        # 读取比较运算符
        op_token = self.current_token()
        if op_token and op_token.token_type == TokenType.EQ:
            op = "=="
            self.advance()
        elif op_token and op_token.token_type == TokenType.NE:
            op = "!="
            self.advance()
        else:
            raise ParseError("Expected '==' or '!=' in branch condition", op_token)
        
        # 读取条件右侧（值）
        right_token = self.current_token()
        if right_token and right_token.token_type == TokenType.STRING:
            right = f'"{right_token.value}"'
            self.advance()
        elif right_token and right_token.token_type == TokenType.IDENTIFIER:
            right = right_token.value
            self.advance()
        elif right_token and right_token.token_type == TokenType.NUMBER:
            right = right_token.value
            self.advance()
        else:
            raise ParseError("Expected value in branch condition", right_token)
        
        condition = f"{left} {op} {right}"
        
        # 期望箭头
        self.expect(TokenType.ARROW, "Expected '->' after branch condition")
        
        # 读取目标Step名称
        target_token = self.expect(TokenType.IDENTIFIER, "Expected target step name after '->'")
        target_step = target_token.value
        
        return BranchNode(condition, target_step, line_number)
    
    def parse_set(self) -> SetNode:
        """解析Set语句"""
        token = self.expect(TokenType.SET, "Expected 'set' keyword")
        line_number = token.line_number
        
        # 变量名
        var_token = self.expect(TokenType.IDENTIFIER, "Expected variable name after 'set'")
        variable = var_token.value
        
        # 等号
        self.expect(TokenType.EQUALS, "Expected '=' after variable name")
        
        # 值
        value_token = self.current_token()
        if not value_token:
            raise ParseError("Expected value after '='", None)
        
        if value_token.token_type == TokenType.STRING:
            value = value_token.value
            self.advance()
        elif value_token.token_type == TokenType.NUMBER:
            # 尝试转换为数字
            try:
                if '.' in value_token.value:
                    value = float(value_token.value)
                else:
                    value = int(value_token.value)
            except ValueError:
                value = value_token.value
            self.advance()
        elif value_token.token_type == TokenType.IDENTIFIER:
            value = value_token.value
            self.advance()
        else:
            raise ParseError(f"Unexpected value type: {value_token.token_type.value}", value_token)
        
        return SetNode(variable, value, line_number)
    
    def parse_end(self) -> EndNode:
        """解析End语句"""
        token = self.expect(TokenType.END, "Expected 'end' keyword")
        return EndNode(token.line_number)

