# 物流跟踪业务场景脚本
# 专注于物流查询和跟踪相关的功能

step start {
    speak "欢迎使用物流跟踪系统！"
    speak "请输入您的订单号或快递单号："
    listen tracking_number
    branch tracking_number != "" -> query_logistics
    speak "订单号或快递单号不能为空，请重新输入。"
    branch last_input != "" -> start
    end
}

step query_logistics {
    speak "正在为您查询物流信息..."
    set logistics_status = "查询中"
    speak "物流信息查询成功！"
    speak "订单号/快递单号：${tracking_number}"
    speak "快递公司：顺丰速运"
    speak "快递单号：SF1234567890"
    speak "物流状态：运输中"
    speak "当前位置：北京分拨中心"
    speak "预计送达时间：2024-01-18"
    speak "您想要进行什么操作？"
    speak "1. 查看详细物流轨迹"
    speak "2. 重新查询物流"
    speak "3. 返回主菜单"
    listen user_input
    branch user_input == "1" -> logistics_timeline
    branch user_input == "2" -> start
    branch user_input == "3" -> start
    branch user_intent == "查看物流信息" -> logistics_timeline
    branch user_intent == "重新查询" -> start
    branch user_intent == "返回主菜单" -> start
    branch user_intent == "物流查询" -> logistics_timeline
    end
}

step logistics_timeline {
    speak "详细物流轨迹："
    speak "2024-01-15 10:30:00 - 订单已发货"
    speak "2024-01-15 14:20:00 - 已到达北京分拨中心"
    speak "2024-01-16 09:15:00 - 正在运输中"
    speak "2024-01-17 16:45:00 - 已到达目的地分拨中心"
    speak "预计2024-01-18送达"
    speak "还有其他需要帮助的吗？"
    speak "1. 查看详细物流轨迹"
    speak "2. 重新查询物流"
    speak "3. 返回主菜单"
    listen user_input
    branch user_input == "1" -> logistics_timeline
    branch user_input == "2" -> start
    branch user_input == "3" -> start
    branch user_intent == "查看物流信息" -> logistics_timeline
    branch user_intent == "重新查询" -> start
    branch user_intent == "返回主菜单" -> start
    branch user_intent == "物流查询" -> logistics_timeline
    end
}

