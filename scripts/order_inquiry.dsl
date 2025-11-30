# 订单查询专用场景脚本
# 专注于订单相关的查询和处理

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
    speak "2. 查看物流信息"
    speak "3. 申请退款"
    speak "4. 联系客服"
    listen user_input
    branch user_intent == "订单查询" -> order_detail
    branch user_intent == "物流查询" -> order_logistics
    branch user_intent == "退款申请" -> order_refund
    branch user_intent == "产品咨询" -> order_contact
    speak "请选择1-4中的选项。"
    branch last_input != "" -> verify_order
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
    speak "还有其他需要帮助的吗？"
    listen user_input
    branch user_intent == "物流查询" -> order_logistics
    branch user_intent == "退款申请" -> order_refund
    end
}

step order_logistics {
    speak "物流信息："
    speak "订单号：${order_id}"
    speak "快递公司：顺丰速运"
    speak "快递单号：SF1234567890"
    speak "物流状态：运输中"
    speak "当前位置：北京分拨中心"
    speak "预计送达时间：2024-01-18"
    speak "还有其他需要帮助的吗？"
    listen user_input
    branch user_intent == "订单查询" -> order_detail
    end
}

step order_refund {
    speak "退款申请："
    speak "订单号：${order_id}"
    speak "订单金额：￥299.00"
    speak "请输入退款原因："
    listen refund_reason
    speak "退款原因：${refund_reason}"
    speak "退款申请已提交，我们会在1-3个工作日内处理。"
    end
}

step order_contact {
    speak "如需联系客服，请拨打客服热线：400-123-4567"
    speak "客服工作时间：周一至周日 9:00-18:00"
    speak "您也可以在我们的官网上提交工单。"
    end
}

