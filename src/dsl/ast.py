"""
抽象语法树（AST）节点定义
定义DSL脚本的语法树结构
"""

from typing import List, Optional, Any
from enum import Enum


class NodeType(Enum):
    """节点类型枚举"""
    STEP = "step"
    SPEAK = "speak"
    LISTEN = "listen"
    BRANCH = "branch"
    SET = "set"
    END = "end"
    SCRIPT = "script"


class ASTNode:
    """抽象语法树节点基类"""
    
    def __init__(self, node_type: NodeType, line_number: int = 0):
        self.node_type = node_type
        self.line_number = line_number
    
    def __repr__(self):
        return f"{self.node_type.value}(line={self.line_number})"


class StepNode(ASTNode):
    """Step节点：定义一个执行步骤"""
    
    def __init__(self, name: str, statements: List[ASTNode], line_number: int = 0):
        super().__init__(NodeType.STEP, line_number)
        self.name = name
        self.statements = statements
    
    def __repr__(self):
        return f"StepNode(name={self.name}, statements={len(self.statements)})"


class SpeakNode(ASTNode):
    """Speak节点：输出话术"""
    
    def __init__(self, message: str, line_number: int = 0):
        super().__init__(NodeType.SPEAK, line_number)
        self.message = message
    
    def __repr__(self):
        return f"SpeakNode(message={self.message[:30]}...)"


class ListenNode(ASTNode):
    """Listen节点：接收用户输入并进行意图识别"""
    
    def __init__(self, variable: str, line_number: int = 0):
        super().__init__(NodeType.LISTEN, line_number)
        self.variable = variable
    
    def __repr__(self):
        return f"ListenNode(variable={self.variable})"


class BranchNode(ASTNode):
    """Branch节点：条件分支"""
    
    def __init__(self, condition: str, target_step: str, line_number: int = 0):
        super().__init__(NodeType.BRANCH, line_number)
        self.condition = condition  # 条件表达式，如 "user_intent == '订单查询'"
        self.target_step = target_step
    
    def __repr__(self):
        return f"BranchNode(condition={self.condition}, target={self.target_step})"


class SetNode(ASTNode):
    """Set节点：设置变量"""
    
    def __init__(self, variable: str, value: Any, line_number: int = 0):
        super().__init__(NodeType.SET, line_number)
        self.variable = variable
        self.value = value
    
    def __repr__(self):
        return f"SetNode(variable={self.variable}, value={self.value})"


class EndNode(ASTNode):
    """End节点：结束当前流程"""
    
    def __init__(self, line_number: int = 0):
        super().__init__(NodeType.END, line_number)


class ScriptNode(ASTNode):
    """Script节点：整个脚本的根节点"""
    
    def __init__(self, steps: List[StepNode], line_number: int = 0):
        super().__init__(NodeType.SCRIPT, line_number)
        self.steps = steps
        self.step_map = {step.name: step for step in steps}
    
    def get_step(self, name: str) -> Optional[StepNode]:
        """根据名称获取Step节点"""
        return self.step_map.get(name)
    
    def __repr__(self):
        return f"ScriptNode(steps={len(self.steps)})"

