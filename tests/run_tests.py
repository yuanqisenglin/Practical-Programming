"""
运行所有测试
"""

import unittest
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_all_tests():
    """运行所有测试"""
    # 发现并加载所有测试
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加各个测试模块
    suite.addTests(loader.loadTestsFromName('test_lexer'))
    suite.addTests(loader.loadTestsFromName('test_parser'))
    suite.addTests(loader.loadTestsFromName('test_interpreter'))
    suite.addTests(loader.loadTestsFromName('test_intent_analyzer'))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回测试结果
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)

