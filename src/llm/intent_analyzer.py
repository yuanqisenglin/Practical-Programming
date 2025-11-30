"""
意图识别接口
调用大语言模型API进行用户输入的意图识别
"""

from typing import Dict, Any, Optional
import json
import os


class IntentAnalyzer:
    """意图识别器：使用LLM API进行意图识别"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo", base_url: Optional[str] = None):
        """
        初始化意图识别器
        
        Args:
            api_key: API密钥，如果为None则从环境变量OPENAI_API_KEY获取
            model: 使用的模型名称
            base_url: API基础URL（用于兼容其他OpenAI兼容的API）
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        
        if not self.api_key:
            raise ValueError("API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        # 延迟导入openai，避免在没有安装时出错
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        except ImportError:
            raise ImportError("openai package is required. Install it with: pip install openai")
    
    def analyze(self, user_input: str, intents: Optional[list] = None) -> Dict[str, Any]:
        """
        分析用户输入的意图
        
        Args:
            user_input: 用户输入的自然语言文本
            intents: 可选的意图列表，用于指导模型识别
        
        Returns:
            包含意图识别结果的字典：
            {
                "intent": "意图名称",
                "confidence": 0.0-1.0,
                "entities": {...},  # 提取的实体信息
                "raw_response": "原始响应"
            }
        """
        # 构建提示词
        prompt = self._build_prompt(user_input, intents)
        
        try:
            # 调用LLM API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的意图识别助手。请分析用户的输入，识别用户的意图，并以JSON格式返回结果。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            # 解析响应
            content = response.choices[0].message.content.strip()
            
            # 尝试解析JSON
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                # 如果无法解析JSON，尝试提取意图
                result = self._extract_intent_from_text(content, intents)
            
            # 标准化结果格式
            return self._normalize_result(result, user_input, content)
        
        except Exception as e:
            # API调用失败，返回默认结果
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "entities": {},
                "raw_response": str(e),
                "error": str(e)
            }
    
    def _build_prompt(self, user_input: str, intents: Optional[list] = None) -> str:
        """构建提示词"""
        prompt = f"用户输入：{user_input}\n\n"
        
        if intents:
            prompt += f"可能的意图列表：{', '.join(intents)}\n\n"
        
        prompt += """请分析用户的意图，并以JSON格式返回结果。格式如下：
{
    "intent": "意图名称",
    "confidence": 0.0-1.0之间的浮点数,
    "entities": {
        "key": "value"
    }
}

如果无法确定意图，请将intent设置为"unknown"。"""
        
        return prompt
    
    def _extract_intent_from_text(self, text: str, intents: Optional[list] = None) -> Dict[str, Any]:
        """从文本中提取意图（当JSON解析失败时的备用方法）"""
        result = {
            "intent": "unknown",
            "confidence": 0.5,
            "entities": {}
        }
        
        # 简单的关键词匹配
        if intents:
            text_lower = text.lower()
            for intent in intents:
                if intent.lower() in text_lower:
                    result["intent"] = intent
                    result["confidence"] = 0.7
                    break
        
        return result
    
    def _normalize_result(self, result: Dict[str, Any], user_input: str, raw_response: str) -> Dict[str, Any]:
        """标准化结果格式"""
        normalized = {
            "intent": result.get("intent", "unknown"),
            "confidence": float(result.get("confidence", 0.5)),
            "entities": result.get("entities", {}),
            "raw_response": raw_response
        }
        
        # 确保intent是字符串
        if not isinstance(normalized["intent"], str):
            normalized["intent"] = str(normalized["intent"])
        
        # 确保confidence在0-1之间
        normalized["confidence"] = max(0.0, min(1.0, normalized["confidence"]))
        
        return normalized


class MockIntentAnalyzer:
    """模拟意图识别器：用于测试，不调用真实API"""
    
    def __init__(self):
        # 简单的关键词到意图的映射
        self.intent_keywords = {
            "订单查询": ["订单", "查询", "订单号", "订单状态"],
            "退款申请": ["退款", "退货", "申请退款"],
            "物流查询": ["物流", "快递", "配送", "运输"],
            "产品咨询": ["产品", "商品", "咨询", "介绍"],
            "投诉建议": ["投诉", "建议", "意见", "不满"]
        }
    
    def analyze(self, user_input: str, intents: Optional[list] = None) -> Dict[str, Any]:
        """模拟意图识别"""
        user_input_lower = user_input.lower()
        
        # 查找匹配的意图
        # 使用更精确的匹配：优先匹配更具体的意图
        # 按意图的优先级排序（更具体的在前）
        intent_priority = [
            "物流查询",  # 更具体，优先匹配
            "退款申请",
            "订单查询",
            "产品咨询",
            "投诉建议"
        ]
        
        matched_intent = "unknown"
        confidence = 0.0
        
        # 按优先级顺序匹配
        for intent in intent_priority:
            if intent in self.intent_keywords:
                keywords = self.intent_keywords[intent]
                for keyword in keywords:
                    if keyword in user_input_lower:
                        matched_intent = intent
                        confidence = 0.8
                        break
                if matched_intent != "unknown":
                    break
        
        # 如果按优先级没匹配到，再遍历所有意图
        if matched_intent == "unknown":
            for intent, keywords in self.intent_keywords.items():
                if intent not in intent_priority:  # 跳过已检查的
                    for keyword in keywords:
                        if keyword in user_input_lower:
                            matched_intent = intent
                            confidence = 0.8
                            break
                    if matched_intent != "unknown":
                        break
        
        return {
            "intent": matched_intent,
            "confidence": confidence,
            "entities": {},
            "raw_response": f"Mock analysis for: {user_input}"
        }

