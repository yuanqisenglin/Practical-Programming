"""
解释器（Interpreter）
执行抽象语法树，驱动脚本流程
"""

from typing import Optional, Callable, Any
from src.dsl.ast import (
    ScriptNode, StepNode, SpeakNode, ListenNode, 
    BranchNode, SetNode, EndNode, ASTNode
)
from src.runtime.execution_context import ExecutionContext
import re
import os


class InterpreterError(Exception):
    """解释器执行错误"""
    pass


class Interpreter:
    """解释器：执行AST"""
    
    def __init__(self, script: ScriptNode, intent_analyzer: Optional[Callable[[str], dict[str, Any]]] = None, max_recursion_depth: int = 100):
        self.script = script
        self.intent_analyzer = intent_analyzer  # 意图识别函数
        self.max_recursion_depth = max_recursion_depth  # 最大递归深度
    
    def execute(self, context: ExecutionContext, input_callback: Optional[Callable[[str], str]] = None, recursion_depth: int = 0) -> dict[str, Any]:
        """
        执行脚本
        
        Args:
            context: 执行上下文
            input_callback: 用户输入回调函数，接收提示信息，返回用户输入
            recursion_depth: 当前递归深度（内部使用）
        
        Returns:
            执行结果字典，包含：
            - status: "running" | "waiting_input" | "finished" | "error"
            - message: 输出消息
            - next_step: 下一个要执行的Step名称
            - error: 错误信息（如果有）
        """
        try:
            # 检查递归深度
            if recursion_depth >= self.max_recursion_depth:
                return {
                    "status": "error",
                    "message": f"递归深度超限（最大{self.max_recursion_depth}），可能存在无限循环",
                    "error": "Maximum recursion depth exceeded"
                }
            
            # 如果没有当前Step，从start开始
            if not context.current_step:
                if "start" in self.script.step_map:
                    context.set_current_step("start")
                else:
                    # 如果没有start，使用第一个Step
                    if self.script.steps:
                        context.set_current_step(self.script.steps[0].name)
                    else:
                        return {
                            "status": "error",
                            "message": "脚本中没有定义任何Step",
                            "error": "No steps defined"
                        }
                # 重置语句索引，因为开始新步骤
                context.set_statement_index(0)
            
            current_step_name = context.get_current_step()
            step_node = self.script.get_step(current_step_name)
            
            if not step_node:
                return {
                    "status": "error",
                    "message": f"Step '{current_step_name}' 不存在",
                    "error": f"Step not found: {current_step_name}"
                }
            
            # 执行Step中的语句
            result = self._execute_step(step_node, context, input_callback, recursion_depth)
            return result
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"执行错误: {str(e)}",
                "error": str(e)
            }
    
    def _execute_step(self, step: StepNode, context: ExecutionContext, 
                     input_callback: Optional[Callable[[str], str]], recursion_depth: int = 0) -> dict[str, Any]:
        """执行Step节点"""
        messages = []  # 收集所有speak消息
        
        # 获取当前执行位置（从上次中断的地方继续）
        start_index = context.get_statement_index()
        
        for index, statement in enumerate(step.statements):
            # 如果索引小于起始位置，跳过已执行的语句
            if index < start_index:
                continue
            result = self._execute_statement(statement, context, input_callback)
            
            # 收集speak消息
            if isinstance(result, dict) and result.get("status") == "running" and result.get("message"):
                messages.append(result.get("message"))
            
            # 如果语句返回结果，需要处理
            if isinstance(result, dict):
                # 如果状态是waiting_input，需要等待用户输入
                if result.get("status") == "waiting_input":
                    # 保存当前执行位置，下次从这个位置继续
                    context.set_statement_index(index)
                    # 如果有收集到的消息，合并到结果中
                    if messages:
                        result["message"] = "\n".join(messages) + "\n" + result.get("message", "")
                    return result
                
                # 如果状态是finished或error，直接返回
                if result.get("status") in ("finished", "error"):
                    # 如果有收集到的消息，优先使用speak消息
                    if messages:
                        # 对于finished状态，合并所有speak消息
                        if result.get("status") == "finished":
                            result["message"] = "\n".join(messages)
                        else:
                            result["message"] = "\n".join(messages) + "\n" + result.get("message", "")
                    return result
                
                # 如果有next_step，跳转到下一个Step
                if result.get("next_step"):
                    context.set_current_step(result["next_step"])
                    # 重置语句索引，因为跳转到新步骤
                    context.set_statement_index(0)
                    # 递归执行下一个Step，增加递归深度
                    next_step_node = self.script.get_step(result["next_step"])
                    if next_step_node:
                        # 检查递归深度
                        if recursion_depth + 1 >= self.max_recursion_depth:
                            error_result = {
                                "status": "error",
                                "message": f"递归深度超限（最大{self.max_recursion_depth}），可能存在无限循环",
                                "error": "Maximum recursion depth exceeded"
                            }
                            if messages:
                                error_result["message"] = "\n".join(messages) + "\n" + error_result["message"]
                            return error_result
                        
                        next_result = self._execute_step(next_step_node, context, input_callback, recursion_depth + 1)
                        # 当branch跳转时，不合并之前步骤的消息，只显示新步骤的消息
                        # 这样可以避免显示不相关的信息
                        return next_result
                    else:
                        error_result = {
                            "status": "error",
                            "message": f"Step '{result['next_step']}' 不存在",
                            "error": f"Step not found: {result['next_step']}"
                        }
                        if messages:
                            error_result["message"] = "\n".join(messages) + "\n" + error_result["message"]
                        return error_result
                
                # 如果listen返回running状态，说明已经处理了输入，继续执行下一个语句
                # 不需要特殊处理，继续循环
        
        # Step执行完毕，但没有明确的结束或跳转
        # 重置语句索引，因为步骤执行完毕
        context.set_statement_index(0)
        result = {
            "status": "finished",
            "message": f"Step '{step.name}' 执行完毕"
        }
        # 如果有收集到的消息，合并所有speak消息
        if messages:
            result["message"] = "\n".join(messages)
        return result
    
    def _execute_statement(self, statement: ASTNode, context: ExecutionContext,
                          input_callback: Optional[Callable[[str], str]]) -> Optional[dict[str, Any]]:
        """执行单个语句"""
        if isinstance(statement, SpeakNode):
            return self._execute_speak(statement, context)
        elif isinstance(statement, ListenNode):
            return self._execute_listen(statement, context, input_callback)
        elif isinstance(statement, BranchNode):
            return self._execute_branch(statement, context)
        elif isinstance(statement, SetNode):
            return self._execute_set(statement, context)
        elif isinstance(statement, EndNode):
            return self._execute_end(statement, context)
        else:
            raise InterpreterError(f"Unknown statement type: {type(statement)}")
    
    def _execute_speak(self, node: SpeakNode, context: ExecutionContext) -> dict[str, Any]:
        """执行Speak语句"""
        message = self._substitute_variables(node.message, context)
        return {
            "status": "running",
            "message": message
        }
    
    def _execute_listen(self, node: ListenNode, context: ExecutionContext,
                       input_callback: Optional[Callable[[str], str]]) -> dict[str, Any]:
        """执行Listen语句"""
        if not input_callback:
            # 如果没有输入回调，返回等待状态
            return {
                "status": "waiting_input",
                "message": "等待用户输入",
                "variable": node.variable
            }
        
        # 调用输入回调获取用户输入
        user_input = input_callback("请输入：")
        
        # 如果没有输入（空字符串），返回等待状态，避免无限循环
        if not user_input or not user_input.strip():
            return {
                "status": "waiting_input",
                "message": "等待用户输入",
                "variable": node.variable
            }
        
        # 存储原始输入
        context.set_variable(node.variable, user_input)
        
        # 判断是否需要意图识别
        # 如果变量名是 user_input 或包含 "input"，通常需要意图识别
        # 如果变量名是 order_id、complaint_content、suggestion_content 等数据字段，通常不需要意图识别
        needs_intent_recognition = self._should_recognize_intent(node.variable, user_input)
        
        # 如果有意图识别器且需要识别，进行意图识别
        if self.intent_analyzer and needs_intent_recognition:
            try:
                intent_result = self.intent_analyzer(user_input)
                # 将意图识别结果存储到变量中
                for key, value in intent_result.items():
                    context.set_variable(key, value)
                
                # 如果识别到意图，存储到user_intent变量
                if "intent" in intent_result:
                    recognized_intent = intent_result["intent"]
                    context.set_variable("user_intent", recognized_intent)
                    # 调试信息：打印识别到的意图（可选，可以通过环境变量控制）
                    if os.getenv("DEBUG_INTENT", "").lower() == "true":
                        print(f"[DEBUG] 用户输入: '{user_input}' -> 识别意图: '{recognized_intent}' (置信度: {intent_result.get('confidence', 0.0):.2f})")
            except Exception as e:
                # 意图识别失败，继续执行
                context.set_variable("user_intent", "unknown")
                if os.getenv("DEBUG_INTENT", "").lower() == "true":
                    print(f"[DEBUG] 意图识别失败: {e}")
        else:
            # 不需要意图识别时，不要覆盖已有的 user_intent
            if context.get_variable("user_intent") is None:
                context.set_variable("user_intent", "unknown")
        
        return {
            "status": "running",
            "message": f"收到输入: {user_input}"
        }
    
    def _should_recognize_intent(self, variable_name: str, user_input: str) -> bool:
        """
        判断是否需要进行意图识别
        
        Args:
            variable_name: 变量名
            user_input: 用户输入
        
        Returns:
            是否需要意图识别
        """
        # 变量名包含 "input" 或 "intent" 的，通常需要意图识别
        if "input" in variable_name.lower() or "intent" in variable_name.lower():
            return True
        
        var_lower = variable_name.lower()

        # 变量名是数据字段的，通常不需要意图识别
        data_fields = {
            "order_id",
            "complaint_id",
            "complaint_content",
            "suggestion_content",
            "contact_info",
            "refund_reason",
            "refund_reason_code",
            "refund_reason_detail",
            "logistics_number",
            "confirm",
        }
        if var_lower in data_fields:
            # 对于数据字段，如果输入是纯数字，直接跳过意图识别
            if user_input.strip().isdigit():
                return False
            # 如果是退款原因等字段的文字描述，则可以尝试意图识别
            # 例如用户直接输入“质量问题”
            if var_lower.startswith("refund_reason"):
                return True
            return False
        
        # 如果输入是纯数字且很短（1-3位），可能是数据而不是意图
        if user_input.strip().isdigit() and len(user_input.strip()) <= 3:
            # 检查是否可能是菜单选项（1-9）
            if len(user_input.strip()) == 1 and user_input.strip() in "123456789":
                # 可能是菜单选项，需要意图识别
                return True
            # 其他短数字可能是数据（如订单号的一部分）
            return False
        
        # 默认情况下，如果变量名看起来像用户输入，进行意图识别
        # 否则不进行意图识别
        return "user" in variable_name.lower() or "input" in variable_name.lower()
    
    def _execute_branch(self, node: BranchNode, context: ExecutionContext) -> dict[str, Any]:
        """执行Branch语句"""
        # 解析条件表达式
        # 格式：variable == "value" 或 variable != "value"
        condition = node.condition
        
        # 使用正则表达式解析条件
        # 匹配：identifier operator value
        pattern = r'(\w+)\s*(==|!=)\s*(".*?"|\'.*?\'|\w+)'
        match = re.match(pattern, condition)
        
        if not match:
            raise InterpreterError(f"Invalid branch condition: {condition}")
        
        var_name = match.group(1)
        operator = match.group(2)
        value_str = match.group(3)
        
        # 获取变量值
        var_value = context.get_variable(var_name)
        
        # 解析比较值（去除引号）
        if value_str.startswith('"') and value_str.endswith('"'):
            compare_value = value_str[1:-1]
        elif value_str.startswith("'") and value_str.endswith("'"):
            compare_value = value_str[1:-1]
        else:
            # 可能是变量名或数字
            compare_value = context.get_variable(value_str)
            if compare_value is None:
                # 尝试作为数字
                try:
                    if '.' in value_str:
                        compare_value = float(value_str)
                    else:
                        compare_value = int(value_str)
                except ValueError:
                    compare_value = value_str
        
        # 执行比较
        if operator == "==":
            condition_met = str(var_value) == str(compare_value)
        elif operator == "!=":
            condition_met = str(var_value) != str(compare_value)
        else:
            raise InterpreterError(f"Unsupported operator: {operator}")
        
        # 如果条件满足，跳转到目标Step
        if condition_met:
            return {
                "status": "running",
                "next_step": node.target_step
            }
        
        # 条件不满足，继续执行下一条语句
        return None
    
    def _execute_set(self, node: SetNode, context: ExecutionContext) -> None:
        """执行Set语句"""
        # 如果值是变量名，需要获取变量值
        if isinstance(node.value, str) and context.get_variable(node.value) is not None:
            value = context.get_variable(node.value)
        else:
            value = node.value
        
        context.set_variable(node.variable, value)
        return None
    
    def _execute_end(self, node: EndNode, context: ExecutionContext) -> dict[str, Any]:
        """执行End语句"""
        return {
            "status": "finished",
            "message": "流程结束"
        }
    
    def _substitute_variables(self, text: str, context: ExecutionContext) -> str:
        """替换文本中的变量占位符"""
        # 简单的变量替换：${variable_name}
        pattern = r'\$\{(\w+)\}'
        
        def replace_var(match):
            var_name = match.group(1)
            value = context.get_variable(var_name)
            return str(value) if value is not None else match.group(0)
        
        return re.sub(pattern, replace_var, text)

