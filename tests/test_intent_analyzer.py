"""
意图识别器测试
"""

import unittest
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm.intent_analyzer import MockIntentAnalyzer


class TestIntentAnalyzer(unittest.TestCase):
    """意图识别器测试类"""
    
    def setUp(self):
        """设置测试环境"""
        self.analyzer = MockIntentAnalyzer()
    
    def test_analyze_order_query(self):
        """测试订单查询意图识别"""
        result = self.analyzer.analyze("我想查询订单")
        self.assertEqual(result["intent"], "订单查询")
        self.assertGreater(result["confidence"], 0.0)
    
    def test_analyze_refund(self):
        """测试退款申请意图识别"""
        result = self.analyzer.analyze("我要申请退款")
        self.assertEqual(result["intent"], "退款申请")
    
    def test_analyze_logistics(self):
        """测试物流查询意图识别"""
        result = self.analyzer.analyze("查询快递物流")
        self.assertEqual(result["intent"], "物流查询")
    
    def test_analyze_unknown(self):
        """测试未知意图"""
        result = self.analyzer.analyze("随便说点什么")
        self.assertEqual(result["intent"], "unknown")
    
    def test_result_format(self):
        """测试结果格式"""
        result = self.analyzer.analyze("查询订单")
        
        self.assertIn("intent", result)
        self.assertIn("confidence", result)
        self.assertIn("entities", result)
        self.assertIn("raw_response", result)
        
        self.assertIsInstance(result["intent"], str)
        self.assertIsInstance(result["confidence"], float)
        self.assertGreaterEqual(result["confidence"], 0.0)
        self.assertLessEqual(result["confidence"], 1.0)


if __name__ == '__main__':
    unittest.main()

