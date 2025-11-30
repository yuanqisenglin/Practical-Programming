# 退款处理专用场景脚本
# 专注于退款申请的流程处理

step start {
    speak "欢迎使用退款申请系统！"
    speak "我将引导您完成退款申请流程。"
    speak "首先，请输入您的订单号："
    listen order_id
    branch order_id != "" -> check_order
    speak "订单号不能为空，请重新输入。"
    branch last_input != "" -> start
    end
}

step check_order {
    speak "正在检查订单 ${order_id} 的退款资格..."
    set order_status = "检查中"
    speak "订单检查完成。"
    speak "订单号：${order_id}"
    speak "订单金额：￥299.00"
    speak "订单状态：已发货"
    speak "该订单符合退款条件。"
    speak "请选择退款原因："
    speak "1. 商品质量问题"
    speak "2. 商品与描述不符"
    speak "3. 不需要了"
    speak "4. 其他原因"
    listen refund_reason_code
    branch refund_reason_code == "1" -> refund_reason_detail
    branch refund_reason_code == "2" -> refund_reason_detail
    branch refund_reason_code == "3" -> refund_reason_detail
    branch refund_reason_code == "4" -> refund_reason_detail
    speak "请选择1-4中的选项。"
    branch last_input != "" -> check_order
    end
}

step refund_reason_detail {
    speak "请详细描述退款原因："
    listen refund_reason_detail
    speak "退款原因已记录：${refund_reason_detail}"
    speak "请选择退款方式："
    speak "1. 原路退回（退回原支付账户）"
    speak "2. 退回余额（退回账户余额）"
    listen refund_method
    branch refund_method == "1" -> confirm_refund
    branch refund_method == "2" -> confirm_refund
    speak "请选择1或2。"
    branch last_input != "" -> refund_reason_detail
    end
}

step confirm_refund {
    speak "请确认退款信息："
    speak "订单号：${order_id}"
    speak "退款金额：￥299.00"
    speak "退款原因：${refund_reason_detail}"
    speak "退款方式：${refund_method}"
    speak "确认提交退款申请？(yes/no)"
    listen confirm
    branch confirm == "yes" -> submit_refund
    branch confirm == "no" -> cancel_refund
    speak "请输入yes或no。"
    branch last_input != "" -> confirm_refund
    end
}

step submit_refund {
    speak "退款申请已提交！"
    speak "申请编号：REF20240115001"
    speak "我们会在1-3个工作日内审核您的退款申请。"
    speak "审核通过后，退款金额将在3-5个工作日内到账。"
    speak "您可以通过订单号查询退款进度。"
    speak "感谢您的使用！"
    end
}

step cancel_refund {
    speak "退款申请已取消。"
    speak "如有其他需要，请随时联系我们。"
    end
}

