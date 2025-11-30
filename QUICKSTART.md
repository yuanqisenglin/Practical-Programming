# 快速开始指南

## 1. 安装依赖

```bash
pip install -r requirements.txt
```

注意：如果只使用模拟LLM（不调用真实API），可以跳过安装openai包。

## 2. 运行示例

### 方式1：使用命令行

```bash
# 使用模拟LLM（推荐用于测试）
python src/main.py --script scripts/customer_service.dsl --mock
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

系统: 欢迎使用智能客服系统！我是您的专属客服助手。
系统: 我可以帮助您处理以下业务：
系统: 1. 订单查询
系统: 2. 退款申请
系统: 3. 物流查询
系统: 4. 产品咨询
系统: 5. 投诉建议
系统: 请告诉我您需要什么帮助？

您: 我想查询订单

系统: 好的，我来帮您查询订单信息。
系统: 请输入您的订单号：

您: 1234567890

系统: 正在为您查询订单号为 1234567890 的订单信息...
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
   python src/main.py --script scripts/customer_service.dsl
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

