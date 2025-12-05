# 售后投诉业务场景脚本
# 专注于售后服务和投诉处理相关的功能

step start {
    speak "欢迎使用售后投诉系统！"
    speak "感谢您的反馈，我们会认真对待每一条建议和投诉。"
    speak "请选择您要进行的操作："
    speak "1. 提交投诉"
    speak "2. 提交建议"
    speak "3. 查询投诉进度"
    speak "4. 返回主菜单"
    listen user_input
    branch user_input == "1" -> submit_complaint
    branch user_input == "2" -> submit_suggestion
    branch user_input == "3" -> query_complaint
    branch user_input == "4" -> start
    branch user_intent == "返回主菜单" -> start
    branch user_intent == "查询进度" -> query_complaint
    branch user_intent == "查询投诉" -> query_complaint
    branch user_intent == "提交建议" -> submit_suggestion
    branch user_intent == "提交投诉" -> submit_complaint
    branch user_intent == "投诉建议" -> submit_complaint
    speak "抱歉，我没有理解您的输入。请选择1-4中的选项。"
    speak "1. 提交投诉"
    speak "2. 提交建议"
    speak "3. 查询投诉进度"
    speak "4. 返回主菜单"
    listen user_input
    branch user_input == "1" -> submit_complaint
    branch user_input == "2" -> submit_suggestion
    branch user_input == "3" -> query_complaint
    branch user_input == "4" -> start
    branch user_intent == "返回主菜单" -> start
    branch user_intent == "查询进度" -> query_complaint
    branch user_intent == "查询投诉" -> query_complaint
    branch user_intent == "提交建议" -> submit_suggestion
    branch user_intent == "提交投诉" -> submit_complaint
    branch user_intent == "投诉建议" -> submit_complaint
    end
}

step submit_complaint {
    speak "请详细描述您要投诉的问题："
    listen complaint_content
    speak "请输入您的订单号（如有）："
    listen order_id
    speak "请输入您的联系方式："
    listen contact_info
    speak "您的投诉已提交："
    speak "投诉内容：${complaint_content}"
    speak "订单号：${order_id}"
    speak "联系方式：${contact_info}"
    speak "投诉编号：COMP20240115001"
    speak "我们会尽快处理您的问题，并在3个工作日内给您回复。"
    speak "还有其他需要帮助的吗？"
    speak "1. 提交新的投诉"
    speak "2. 查询投诉进度"
    speak "3. 返回主菜单"
    listen user_input
    branch user_input == "1" -> submit_complaint
    branch user_input == "2" -> query_complaint
    branch user_input == "3" -> start
    branch user_intent == "返回主菜单" -> start
    branch user_intent == "投诉建议" -> submit_complaint
    branch user_intent == "查询投诉" -> query_complaint
    branch user_intent == "查询进度" -> query_complaint
    end
}

step submit_suggestion {
    speak "感谢您为我们提供宝贵的建议！"
    speak "请详细描述您的建议："
    listen suggestion_content
    speak "您的建议已提交："
    speak "建议内容：${suggestion_content}"
    speak "建议编号：SUGG20240115001"
    speak "我们会认真考虑您的建议，感谢您的支持！"
    speak "还有其他需要帮助的吗？"
    speak "1. 提交新的建议"
    speak "2. 返回主菜单"
    listen user_input
    branch user_input == "1" -> submit_suggestion
    branch user_input == "2" -> start
    branch user_intent == "返回主菜单" -> start
    branch user_intent == "投诉建议" -> submit_suggestion
    speak "抱歉，我没有理解您的输入。请选择1或2。"
    speak "1. 提交新的建议"
    speak "2. 返回主菜单"
    listen user_input
    branch user_input == "1" -> submit_suggestion
    branch user_input == "2" -> start
    branch user_intent == "返回主菜单" -> start
    end
}

step query_complaint {
    speak "请输入您的投诉编号或订单号："
    listen complaint_id
    branch complaint_id != "" -> show_complaint_status
    speak "投诉编号或订单号不能为空，请重新输入。"
    branch last_input != "" -> query_complaint
    end
}

step show_complaint_status {
    speak "正在查询投诉进度..."
    speak "投诉编号：${complaint_id}"
    speak "投诉状态：处理中"
    speak "提交时间：2024-01-15 10:30:00"
    speak "预计处理完成时间：2024-01-18"
    speak "处理进度：已收到您的投诉，正在核实处理中。"
    speak "还有其他需要帮助的吗？"
    speak "1. 查询其他投诉"
    speak "2. 返回主菜单"
    listen user_input
    branch user_input == "1" -> query_complaint
    branch user_input == "2" -> start
    branch user_intent == "返回主菜单" -> start
    branch user_intent == "查询进度" -> query_complaint
    branch user_intent == "查询投诉" -> query_complaint
    branch user_intent == "投诉建议" -> query_complaint
    speak "抱歉，我没有理解您的输入。请选择1或2。"
    speak "1. 查询其他投诉"
    speak "2. 返回主菜单"
    listen user_input
    branch user_input == "1" -> query_complaint
    branch user_input == "2" -> start
    branch user_intent == "返回主菜单" -> start
    branch user_intent == "查询进度" -> query_complaint
    branch user_intent == "查询投诉" -> query_complaint
    end
}

