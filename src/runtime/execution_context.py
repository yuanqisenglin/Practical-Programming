"""
执行上下文（Execution Context）
管理每个用户的独立执行环境，包括变量表、当前Step等状态
"""

from typing import Dict, Any, Optional
import threading


class ExecutionContext:
    """执行上下文：为每个用户维护独立的执行状态"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.variables: Dict[str, Any] = {}
        self.current_step: Optional[str] = None
        self.pending_input: Optional[str] = None  # 待处理的用户输入
        self.input_used: bool = False  # 输入是否已被使用
        self.lock = threading.Lock()  # 用于线程安全
    
    def set_variable(self, name: str, value: Any):
        """设置变量"""
        with self.lock:
            self.variables[name] = value
    
    def get_variable(self, name: str) -> Any:
        """获取变量值"""
        with self.lock:
            return self.variables.get(name)
    
    def set_current_step(self, step_name: str):
        """设置当前执行的Step"""
        with self.lock:
            self.current_step = step_name
    
    def get_current_step(self) -> Optional[str]:
        """获取当前执行的Step"""
        with self.lock:
            return self.current_step
    
    def set_pending_input(self, user_input: str):
        """设置待处理的用户输入"""
        with self.lock:
            self.pending_input = user_input
            self.input_used = False
    
    def get_and_consume_input(self) -> Optional[str]:
        """获取并消费待处理的输入（只能使用一次）"""
        with self.lock:
            if self.pending_input and not self.input_used:
                self.input_used = True
                return self.pending_input
            return None
    
    def clear(self):
        """清空执行上下文"""
        with self.lock:
            self.variables.clear()
            self.current_step = None
            self.pending_input = None
            self.input_used = False
    
    def __repr__(self):
        return f"ExecutionContext(user_id={self.user_id}, step={self.current_step}, vars={len(self.variables)})"


class ContextManager:
    """上下文管理器：管理多个用户的执行上下文"""
    
    def __init__(self):
        self.contexts: Dict[str, ExecutionContext] = {}
        self.lock = threading.Lock()
    
    def get_context(self, user_id: str) -> ExecutionContext:
        """获取或创建用户的执行上下文"""
        with self.lock:
            if user_id not in self.contexts:
                self.contexts[user_id] = ExecutionContext(user_id)
            return self.contexts[user_id]
    
    def remove_context(self, user_id: str):
        """移除用户的执行上下文"""
        with self.lock:
            if user_id in self.contexts:
                del self.contexts[user_id]
    
    def clear_all(self):
        """清空所有上下文"""
        with self.lock:
            self.contexts.clear()

