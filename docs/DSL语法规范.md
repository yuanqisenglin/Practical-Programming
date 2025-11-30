# DSL语法规范文档

## 1. 概述

本DSL（领域特定语言）用于描述智能客服机器人的自动应答逻辑。通过编写DSL脚本，可以定义不同业务场景下的对话流程、条件分支和变量操作。

## 2. 基本语法元素

### 2.1 关键字

- `step`: 定义执行步骤
- `speak`: 输出话术
- `listen`: 接收用户输入
- `branch`: 条件分支
- `set`: 设置变量
- `end`: 结束流程

### 2.2 标识符

- 变量名和Step名称使用字母、数字和下划线组成
- 不能以数字开头
- 大小写敏感

### 2.3 字面量

- **字符串**: 使用双引号或单引号包围，支持转义字符（`\n`, `\t`, `\\`）
- **数字**: 整数或浮点数

### 2.4 运算符

- `==`: 等于比较
- `!=`: 不等于比较
- `=`: 赋值
- `->`: 跳转箭头

## 3. 语句定义

### 3.1 Step定义

```
step <step_name> {
    <statements>
}
```

**说明**:
- `step_name`: Step的名称，必须是有效的标识符
- `statements`: Step内包含的语句列表
- 每个脚本必须至少包含一个Step
- 建议第一个Step命名为`start`作为入口点

**示例**:
```
step start {
    speak "欢迎使用客服系统"
    end
}
```

### 3.2 Speak语句

```
speak "<message>"
```

**说明**:
- 输出话术给用户
- `message`中可以包含变量占位符`${variable_name}`
- 变量占位符会在执行时被替换为实际值

**示例**:
```
speak "您好，${name}，欢迎使用我们的服务！"
```

### 3.3 Listen语句

```
listen <variable_name>
```

**说明**:
- 接收用户输入
- 将用户输入存储到指定的变量中
- 如果配置了意图识别器，会自动进行意图识别并将结果存储到`user_intent`变量

**示例**:
```
listen user_input
```

### 3.4 Branch语句

```
branch <condition> -> <target_step>
```

**说明**:
- 根据条件决定是否跳转到目标Step
- `condition`: 条件表达式，格式为`variable operator value`
  - 支持运算符：`==`（等于）、`!=`（不等于）
  - `value`可以是字符串、数字或变量名
- 如果条件为真，跳转到`target_step`；否则继续执行下一条语句

**示例**:
```
branch user_intent == "订单查询" -> query_order
branch count != 0 -> process_data
```

### 3.5 Set语句

```
set <variable> = <value>
```

**说明**:
- 设置变量的值
- `variable`: 变量名
- `value`: 可以是字符串、数字或变量名（引用其他变量的值）

**示例**:
```
set count = 10
set message = "hello"
set total = count
```

### 3.6 End语句

```
end
```

**说明**:
- 结束当前流程的执行
- 执行到`end`语句后，Agent将停止处理

## 4. 注释

使用`#`开头的行表示注释，注释会被词法分析器忽略。

**示例**:
```
# 这是一个注释
step start {
    speak "hello"  # 行内注释
}
```

## 5. 变量系统

### 5.1 变量命名

- 变量名必须是有效的标识符
- 大小写敏感
- 建议使用有意义的变量名

### 5.2 变量作用域

- 变量在用户会话期间有效
- 每个用户有独立的变量表
- 变量可以在不同Step之间共享

### 5.3 特殊变量

- `user_intent`: 由意图识别器自动设置，表示识别到的用户意图
- `last_input`: 最后一次用户输入的内容

## 6. 执行流程

1. 脚本从`start` Step开始执行（如果没有`start`，则从第一个Step开始）
2. 按顺序执行Step内的语句
3. 遇到`speak`语句，输出话术
4. 遇到`listen`语句，等待用户输入并进行意图识别
5. 遇到`branch`语句，根据条件决定是否跳转
6. 遇到`set`语句，设置变量值
7. 遇到`end`语句，结束执行
8. 如果跳转到其他Step，从目标Step开始执行

## 7. 完整示例

```
# 客服系统脚本示例

step start {
    speak "欢迎使用智能客服系统！"
    speak "我可以帮助您处理以下业务："
    speak "1. 订单查询"
    speak "2. 退款申请"
    speak "请告诉我您需要什么帮助？"
    listen user_input
    branch user_intent == "订单查询" -> query_order
    branch user_intent == "退款申请" -> refund_process
    speak "抱歉，我没有理解您的需求。"
    end
}

step query_order {
    speak "好的，我来帮您查询订单信息。"
    speak "请输入您的订单号："
    listen order_id
    speak "正在为您查询订单号为 ${order_id} 的订单信息..."
    end
}

step refund_process {
    speak "好的，我来帮您处理退款申请。"
    speak "请输入您要退款的订单号："
    listen refund_order_id
    speak "您的退款申请已提交，订单号：${refund_order_id}"
    end
}
```

## 8. 最佳实践

1. **Step命名**: 使用有意义的Step名称，如`query_order`、`refund_process`
2. **变量命名**: 使用清晰的变量名，如`order_id`、`user_input`
3. **错误处理**: 在关键分支添加默认处理逻辑
4. **注释**: 为复杂的业务逻辑添加注释说明
5. **模块化**: 将不同的业务场景拆分到不同的Step中

## 9. 限制和注意事项

1. 不支持循环语句（for、while）
2. 不支持函数定义
3. 条件表达式仅支持简单的比较操作
4. 变量类型是动态的，无需声明
5. 字符串比较是大小写敏感的

