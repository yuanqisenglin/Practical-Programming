# 基于DSL的多业务场景Agent系统

## 项目简介

本项目实现了一个基于领域特定语言（DSL）的智能客服机器人系统，能够通过自定义脚本语言描述不同业务场景的应答逻辑，并集成大语言模型API进行意图识别。

## 项目结构

```
Practical-Programming/
├── src/                    # 源代码目录
│   ├── dsl/               # DSL相关模块
│   │   ├── lexer.py       # 词法分析器
│   │   ├── parser.py      # 语法分析器
│   │   ├── interpreter.py # 解释器
│   │   └── ast.py         # 抽象语法树节点定义
│   ├── llm/               # LLM接口模块
│   │   └── intent_analyzer.py  # 意图识别接口
│   ├── runtime/           # 运行时环境
│   │   └── execution_context.py  # 执行上下文管理
│   └── main.py            # 主程序入口
├── scripts/               # DSL脚本范例
│   ├── order_inquiry.dsl          # 订单查询业务场景
│   ├── refund_application.dsl     # 退款申请业务场景
│   ├── logistics_tracking.dsl     # 物流跟踪业务场景
│   └── after_sales_complaint.dsl  # 售后投诉业务场景
├── tests/                 # 测试代码
│   ├── test_lexer.py
│   ├── test_parser.py
│   ├── test_interpreter.py
│   └── test_data/        # 测试数据
├── docs/                  # 文档目录
└── requirements.txt       # 依赖包

```

## DSL语法规范

### 基本语法

1. **Step定义**: `step <step_name> { ... }`
2. **Speak语句**: `speak "<message>"`
3. **Listen语句**: `listen <variable_name>`
4. **Branch语句**: `branch <condition> -> <step_name>`
5. **Set语句**: `set <variable> = <value>`
6. **End语句**: `end`

### 示例脚本

```dsl
step start {
    speak "欢迎使用客服系统，请问有什么可以帮助您的？"
    listen user_input
    branch user_intent == "订单查询" -> query_order
    branch user_intent == "退款申请" -> refund_process
    speak "抱歉，我没有理解您的需求。"
    end
}

step query_order {
    speak "请输入您的订单号："
    listen order_id
    set order_status = "查询中"
    speak "正在为您查询订单信息..."
    end
}
```

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行程序

```bash
# 订单查询场景
python src/main.py --script scripts/order_inquiry.dsl --mock

# 退款申请场景
python src/main.py --script scripts/refund_application.dsl --mock

# 物流跟踪场景
python src/main.py --script scripts/logistics_tracking.dsl --mock

# 售后投诉场景
python src/main.py --script scripts/after_sales_complaint.dsl --mock

# 使用真实LLM API（需要配置API密钥）
python src/main.py --script scripts/order_inquiry.dsl --api-key your_api_key

# 使用 DeepSeek API（推荐方式）
python src/main.py --script scripts/order_inquiry.dsl \
    --api-key sk-78c61c5b0f1347ccb4508f7bb6cb216d \
    --base-url https://api.deepseek.com \
    --model deepseek-chat

# 或者使用快速启动脚本（已配置 DeepSeek API）
python run_with_deepseek.py --script scripts/order_inquiry.dsl
python run_with_deepseek.py --script scripts/logistics_tracking.dsl
python run_with_deepseek.py --script scripts/refund_application.dsl
python run_with_deepseek.py --script scripts/after_sales_complaint.dsl
```

### 运行测试

```bash
python tests/run_tests.py
```

### 调试模式

系统支持调试模式，可以查看意图识别的详细过程：

**启用意图识别调试模式：**

```bash
# Windows
set DEBUG_INTENT=true
python src/main.py --script scripts/order_inquiry.dsl
python src/main.py --script scripts/logistics_tracking.dsl
python src/main.py --script scripts/refund_application.dsl
python src/main.py --script scripts/after_sales_complaint.dsl

# Linux/Mac
export DEBUG_INTENT=true
python src/main.py --script scripts/order_inquiry.dsl
python src/main.py --script scripts/logistics_tracking.dsl
python src/main.py --script scripts/refund_application.dsl
python src/main.py --script scripts/after_sales_complaint.dsl
```

启用调试模式后，系统会输出以下信息：
- 用户输入内容
- 识别到的意图名称
- 意图识别的置信度
- 意图识别失败时的错误信息

**示例输出：**
```
[DEBUG] 用户输入: '返回主菜单' -> 识别意图: '返回主菜单' (置信度: 0.90)
[DEBUG] 用户输入: '退出去' -> 识别意图: '返回主菜单' (置信度: 0.85)
```

**关闭调试模式：**

```bash
# Windows
set DEBUG_INTENT=
# 或者不设置该环境变量

# Linux/Mac
unset DEBUG_INTENT
# 或者不设置该环境变量
```

## 功能特性

- ✅ 自定义DSL语法，灵活描述业务逻辑
- ✅ 词法分析和语法分析，构建AST
- ✅ 解释器执行引擎，支持条件分支和变量操作
- ✅ LLM意图识别集成，支持OpenAI API和DeepSeek API
- ✅ 多线程支持，每个用户独立执行上下文
- ✅ 调试模式支持，可查看意图识别过程
- ✅ 完整的测试覆盖
- ✅ 多个业务场景示例脚本

## 开发环境

- Python 3.8+
- Git版本管理
- OpenAI API（可选，用于真实意图识别）

## 文档

详细文档请参考`docs/`目录：
- [DSL语法规范](docs/DSL语法规范.md)
- [使用指南](docs/使用指南.md)

## 项目结构说明

- `src/dsl/`: DSL核心模块（词法分析、语法分析、解释器）
- `src/llm/`: LLM意图识别接口
- `src/runtime/`: 运行时环境管理
- `scripts/`: DSL脚本范例
- `tests/`: 单元测试
- `docs/`: 项目文档

## 许可证

MIT License

