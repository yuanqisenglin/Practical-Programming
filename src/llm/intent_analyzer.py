"""
意图识别接口
调用大语言模型API进行用户输入的意图识别
"""

from typing import Dict, Any, Optional
import json
import os


class IntentAnalyzer:
    """意图识别器：使用LLM API进行意图识别"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化意图识别器
        
        Args:
            api_key: API密钥，如果为None则从环境变量OPENAI_API_KEY获取
            model: 使用的模型名称（默认：gpt-3.5-turbo，DeepSeek使用：deepseek-chat）
            base_url: API基础URL（用于兼容其他OpenAI兼容的API，DeepSeek使用：https://api.deepseek.com）
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        
        # 如果没有指定base_url，根据API key判断是否为DeepSeek
        if not self.base_url and self.api_key and self.api_key.startswith("sk-"):
            # DeepSeek的API key通常以sk-开头，但我们需要通过base_url来区分
            # 这里默认使用OpenAI，如果需要DeepSeek，用户需要显式指定base_url
            pass
        
        # 设置默认模型
        if model:
            self.model = model
        elif self.base_url and "deepseek" in self.base_url.lower():
            self.model = "deepseek-chat"  # DeepSeek默认模型
        else:
            self.model = "gpt-3.5-turbo"  # OpenAI默认模型
        
        if not self.api_key:
            raise ValueError("API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        # 延迟导入openai，避免在没有安装时出错
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        except ImportError:
            raise ImportError("openai package is required. Install it with: pip install openai")
    
    def analyze(self, user_input: str, intents: Optional[list] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        分析用户输入的意图
        
        Args:
            user_input: 用户输入的自然语言文本
            intents: 可选的意图列表，用于指导模型识别
            context: 可选的上下文信息（如当前菜单选项）
        
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
        prompt = self._build_prompt(user_input, intents, context)
        
        try:
            # 构建系统提示词
            system_content = """你是一个专业的意图识别助手。请仔细分析用户的输入，识别用户的真实意图。

重要规则：
1. 如果用户输入是单个数字（如"1"、"2"），请根据当前菜单选项识别对应的意图
2. 如果用户输入是文字，请根据文字内容识别意图
3. 特别注意：
   - '退出'、'退出去'、'主菜单'、'返回'、'返回主菜单'等都应该识别为'返回主菜单'意图
   - '查看订单'、'订单详情'、'详情'等应该识别为'查看订单详情'意图
   - 数字"1"通常对应"查看订单详情"或第一个菜单选项
   - 数字"2"通常对应"返回主菜单"或第二个菜单选项

请以JSON格式返回结果，格式：{"intent": "意图名称", "confidence": 0.0-1.0, "entities": {}}"""
            
            # 调用LLM API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # 降低温度，提高准确性
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
    
    def _build_prompt(self, user_input: str, intents: Optional[list] = None, context: Optional[Dict[str, Any]] = None) -> str:
        """构建提示词"""
        prompt = f"用户输入：{user_input}\n\n"
        
        # 添加上下文信息（如菜单选项）
        if context and "menu_options" in context:
            prompt += "当前菜单选项：\n"
            for option in context["menu_options"]:
                prompt += f"  {option}\n"
            prompt += "\n"
            prompt += "注意：如果用户输入的是数字（如'1'、'2'），请根据菜单选项对应关系识别意图。\n\n"
        
        if intents:
            prompt += f"可能的意图列表：{', '.join(intents)}\n\n"
        
        # 添加常见意图的说明
        prompt += """常见意图说明：
- "返回主菜单"：包括"返回"、"主菜单"、"菜单"、"退出"、"退出去"、"返回主菜单"等，或菜单选项中的"返回主菜单"对应的数字
- "查看订单详情"：包括"查看"、"详情"、"订单详情"、"查看订单"等，或菜单选项中的"查看订单详情"对应的数字（通常是"1"）
- "订单查询"：包括"订单"、"查询订单"、"订单号"等
- "退款申请"：包括"退款"、"退货"、"申请退款"等
- "物流查询"：包括"物流"、"快递"、"查询物流"等
- "产品咨询"：包括"咨询"、"产品"、"客服"等

重要提示：
- 如果用户输入是单个数字（如"1"、"2"），请根据当前菜单选项识别对应的意图
- 如果用户输入是文字，请根据文字内容识别意图
- 如果无法确定意图，请将intent设置为"unknown"

请分析用户的意图，并以JSON格式返回结果。格式如下：
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
            "订单查询": ["订单", "查询", "订单号", "订单状态", "详情", "查看订单", "订单详情", "查询订单", "订单信息"],
            "退款申请": ["退款", "退货", "申请退款", "申请", "退款", "退货", "申请退款"],
            "物流查询": ["物流查询", "查询物流", "物流跟踪", "快递查询", "快递物流"],
            "产品咨询": ["产品", "商品", "咨询", "介绍", "客服", "联系", "联系客服", "帮助", "产品咨询"],
            "投诉建议": ["投诉建议", "意见", "不满"],
            "提交投诉": ["提交投诉", "我要投诉", "投诉问题", "我要提交投诉"],
            "提交建议": ["提交建议", "我要建议", "提建议", "反馈建议"],
            "查询投诉": ["查询投诉", "投诉查询"],
            "查询进度": ["查询进度", "进度查询", "投诉进度", "处理进度", "投诉状态"],
            # 通用操作
            "返回主菜单": ["返回", "主菜单", "菜单", "退出", "退出去", "退出系统", "返回主菜单", "回到主菜单", "回到菜单", "返回菜单", "回主菜单"],
            "查看订单详情": ["查看", "订单详情", "详情", "查看订单详情", "订单信息", "查看详情"],
            "查看物流信息": ["查看物流信息", "查看物流", "物流轨迹", "详细物流", "物流信息", "查看物流详情"],
            "重新查询": ["重新查询", "再查", "重新查询物流"],
            "重新申请": ["重新申请", "再申请", "重新申请退款"],
            "原路退回": ["原路", "原路退回", "原路返回", "退回原支付账户"],
            "退回余额": ["退回余额", "余额", "退回账户余额"],
            # 退款原因相关
            "商品质量问题": ["质量问题", "商品质量", "质量", "质量问题", "商品质量问题"],
            "商品与描述不符": ["描述不符", "与描述不符", "不符", "描述", "商品与描述不符"],
            "不需要了": ["不需要", "不需要了", "不想要"],
            "其他原因": ["其他", "其他原因", "其他退款原因"]
        }
    
    def analyze(self, user_input: str, intents: Optional[list] = None) -> Dict[str, Any]:
        """模拟意图识别"""
        user_input_lower = user_input.lower()
        
        # 查找匹配的意图
        # 使用更精确的匹配：优先匹配更具体的意图
        # 按意图的优先级排序（更具体的在前）
        intent_priority = [
            "返回主菜单",  # 操作类意图，优先匹配
            "查看订单详情",
            "物流查询",       # 业务类意图优先于查看物流信息
            "查看物流信息",
            "订单查询",       # 订单查询优先于重新查询
            "退款申请",       # 退款申请优先于重新申请
            "重新查询",
            "重新申请",
            "商品质量问题",  # 退款原因，优先匹配
            "商品与描述不符",
            "不需要了",
            "其他原因",
            "查询进度",  # 售后投诉相关，优先匹配查询类
            "查询投诉",
            "提交投诉",  # 提交类意图
            "提交建议",
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
                    # 对于数字关键词，需要精确匹配（避免 "22" 匹配到 "2"）
                    if keyword.isdigit():
                        if user_input_lower == keyword or user_input_lower.strip() == keyword:
                            matched_intent = intent
                            confidence = 0.9
                            break
                    else:
                        # 对于文字关键词，使用包含匹配
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
                        # 对于数字关键词，需要精确匹配
                        if keyword.isdigit():
                            if user_input_lower == keyword or user_input_lower.strip() == keyword:
                                matched_intent = intent
                                confidence = 0.9
                                break
                        else:
                            # 对于文字关键词，使用包含匹配
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

