# 客服场景脚本
# 支持订单查询、退款申请、物流查询等常见客服功能

step start {
    speak "欢迎使用智能客服系统！我是您的专属客服助手。"
    speak "我可以帮助您处理以下业务："
    speak "1. 订单查询"
    speak "2. 退款申请"
    speak "3. 物流查询"
    speak "4. 产品咨询"
    speak "5. 投诉建议"
    speak "请告诉我您需要什么帮助？"
    listen user_input
    branch user_intent == "订单查询" -> query_order
    branch user_intent == "退款申请" -> refund_process
    branch user_intent == "物流查询" -> logistics_query
    branch user_intent == "产品咨询" -> product_inquiry
    branch user_intent == "投诉建议" -> complaint_suggestion
    speak "抱歉，我没有理解您的需求。请重新描述一下您的问题。"
    branch last_input != "" -> start
    end
}

step query_order {
    speak "好的，我来帮您查询订单信息。"
    speak "请输入您的订单号："
    listen order_id
    set order_status = "查询中"
    speak "正在为您查询订单号为 ${order_id} 的订单信息..."
    speak "订单查询功能正在开发中，请稍后再试。"
    speak "还有其他需要帮助的吗？"
    listen user_input
    branch user_intent == "订单查询" -> query_order
    branch user_intent == "退款申请" -> refund_process
    branch user_intent == "物流查询" -> logistics_query
    end
}

step refund_process {
    speak "好的，我来帮您处理退款申请。"
    speak "请输入您要退款的订单号："
    listen refund_order_id
    speak "请输入退款原因："
    listen refund_reason
    speak "您的退款申请已提交："
    speak "订单号：${refund_order_id}"
    speak "退款原因：${refund_reason}"
    speak "我们会在1-3个工作日内处理您的退款申请，请耐心等待。"
    speak "退款金额将原路返回到您的支付账户。"
    speak "还有其他需要帮助的吗？"
    listen user_input
    branch user_intent == "订单查询" -> query_order
    branch user_intent == "退款申请" -> refund_process
    end
}

step logistics_query {
    speak "好的，我来帮您查询物流信息。"
    speak "请输入您的订单号或快递单号："
    listen tracking_number
    speak "正在为您查询物流信息..."
    speak "物流查询功能正在开发中，请稍后再试。"
    speak "您的快递单号是：${tracking_number}"
    speak "还有其他需要帮助的吗？"
    listen user_input
    branch user_intent == "订单查询" -> query_order
    branch user_intent == "物流查询" -> logistics_query
    end
}

step product_inquiry {
    speak "好的，我来为您介绍产品信息。"
    speak "请告诉我您想了解哪个产品？"
    listen product_name
    speak "关于 ${product_name} 的产品信息："
    speak "产品咨询功能正在开发中，请稍后再试。"
    speak "您可以访问我们的官网查看详细产品信息。"
    speak "还有其他需要帮助的吗？"
    listen user_input
    branch user_intent == "产品咨询" -> product_inquiry
    branch user_intent == "订单查询" -> query_order
    end
}

step complaint_suggestion {
    speak "感谢您的反馈，我们会认真对待每一条建议和投诉。"
    speak "请详细描述您的问题或建议："
    listen complaint_content
    speak "您的反馈已记录："
    speak "${complaint_content}"
    speak "我们会尽快处理您的问题，并在3个工作日内给您回复。"
    speak "感谢您的理解与支持！"
    speak "还有其他需要帮助的吗？"
    listen user_input
    branch user_intent == "投诉建议" -> complaint_suggestion
    end
}

