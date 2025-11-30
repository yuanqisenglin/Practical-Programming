# 快速开始指南

## 1. 安装依赖

```bash
pip install -r requirements.txt
```

注意：如果只使用模拟LLM（不调用真实API），可以跳过安装openai包。

## 2. 运行示例

### 方式1：使用命令行

```bash
# 订单查询场景
python src/main.py --script scripts/order_inquiry.dsl --mock

# 退款申请场景
python src/main.py --script scripts/refund_application.dsl --mock

# 物流跟踪场景
python src/main.py --script scripts/logistics_tracking.dsl --mock

# 售后投诉场景
python src/main.py --script scripts/after_sales_complaint.dsl --mock
```

### 方式2：使用快速运行脚本

```bash
python run_example.py
```

## 3. 交互示例

运行程序后，您会看到：

```
============================================================
智能客服Agent系统
============================================================
输入 'quit' 或 'exit' 退出

系统: 欢迎使用订单查询系统！
系统: 请输入您的订单号：

您: 1234567890

系统: 正在验证订单号 1234567890...
系统: 订单验证成功！
系统: 订单号：1234567890
系统: 订单状态：已确认
系统: 订单金额：￥299.00
系统: 下单时间：2024-01-15 10:30:00
系统: 您想要进行什么操作？
系统: 1. 查看订单详情
系统: 2. 返回主菜单
```

## 4. 运行测试

```bash
python tests/run_tests.py
```

## 5. 使用真实LLM API（可选）

如果需要使用真实的LLM API进行意图识别：

1. 获取API密钥（如OpenAI API Key）
2. 设置环境变量：
   ```bash
   set OPENAI_API_KEY=your_api_key_here
   ```
3. 运行程序（不使用--mock参数）：
   ```bash
   python src/main.py --script scripts/order_inquiry.dsl
   ```

## 6. 创建自定义脚本

1. 参考`scripts/`目录下的示例脚本
2. 按照`docs/DSL语法规范.md`编写您的脚本
3. 运行您的脚本：
   ```bash
   python src/main.py --script your_script.dsl --mock
   ```

## 7. 常见问题

### Q: 提示"无法初始化LLM接口"
A: 这是正常的，系统会自动切换到模拟模式。如果想使用真实API，请配置API密钥。

### Q: 意图识别不准确
A: 在模拟模式下，意图识别基于关键词匹配，可能不够准确。使用真实LLM API可以获得更好的效果。

### Q: 如何退出程序？
A: 输入`quit`、`exit`或`q`，或按`Ctrl+C`。

