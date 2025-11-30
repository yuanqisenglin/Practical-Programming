# 订单查询业务场景脚本
# 专注于订单查询相关的功能

step start {
    speak "欢迎使用订单查询系统！"
    speak "请输入您的订单号："
    listen order_id
    branch order_id != "" -> verify_order
    speak "订单号不能为空，请重新输入。"
    branch last_input != "" -> start
    end
}

step verify_order {
    speak "正在验证订单号 ${order_id}..."
    set order_status = "验证中"
    speak "订单验证成功！"
    speak "订单号：${order_id}"
    speak "订单状态：已确认"
    speak "订单金额：￥299.00"
    speak "下单时间：2024-01-15 10:30:00"
    speak "您想要进行什么操作？"
    speak "1. 查看订单详情"
    speak "2. 返回主菜单"
    listen user_input
    branch user_input == "1" -> order_detail
    branch user_input == "2" -> start
    branch user_intent == "查看订单详情" -> order_detail
    branch user_intent == "返回主菜单" -> start
    branch user_intent == "订单查询" -> order_detail
    speak "抱歉，我没有理解您的输入。请选择1或2。"
    speak "1. 查看订单详情"
    speak "2. 返回主菜单"
    listen user_input
    branch user_input == "1" -> order_detail
    branch user_input == "2" -> start
    branch user_intent == "查看订单详情" -> order_detail
    branch user_intent == "返回主菜单" -> start
    branch user_intent == "订单查询" -> order_detail
    end
}

step order_detail {
    speak "订单详情："
    speak "订单号：${order_id}"
    speak "商品名称：智能手表"
    speak "商品数量：1"
    speak "商品单价：￥299.00"
    speak "订单总价：￥299.00"
    speak "收货地址：北京市朝阳区xxx街道xxx号"
    speak "联系电话：138****8888"
    speak "订单状态：已发货"
    speak "支付方式：支付宝"
    speak "支付时间：2024-01-15 10:35:00"
    speak "还有其他需要帮助的吗？"
    speak "1. 查看订单详情"
    speak "2. 返回主菜单"
    listen user_input
    branch user_input == "1" -> order_detail
    branch user_input == "2" -> start
    branch user_intent == "查看订单详情" -> order_detail
    branch user_intent == "返回主菜单" -> start
    branch user_intent == "订单查询" -> order_detail
    speak "抱歉，我没有理解您的输入。请选择1或2。"
    speak "1. 查看订单详情"
    speak "2. 返回主菜单"
    listen user_input
    branch user_input == "1" -> order_detail
    branch user_input == "2" -> start
    branch user_intent == "查看订单详情" -> order_detail
    branch user_intent == "返回主菜单" -> start
    branch user_intent == "订单查询" -> order_detail
    end
}
