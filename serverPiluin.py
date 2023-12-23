import json
import os
import uuid
from typing import Any

from lark_oapi.api.im.v1 import GetMessageResourceResponse

from api import get_message, get_text_from_json, get_current_time, get_message_file, get_user
from cardBuild import *
from event import MessageReceiveEvent
from exts import cache
from model import Card, WinCard
from util.redisServer import redis
from util.regularApi import matches_orderNo, group_by_remark
from util.yundaApi import upload_image, query_expressTrack, send_incoming_message
from util.yundaModel import ServiceMessage, RemarkBoy, HttpResponse


# 消息意图处理程序

# 理赔专用
def handle_process_claim(req_data: MessageReceiveEvent, text_content, image_key):
    if req_data.event.message.chat_id != "oc_007e96b83d71e19ebeea04af92e15bd4":
        return WinCard.builder() \
            .card(build_card("处理结果", get_current_time(), "未授权", False, False)) \
            .mate(False) \
            .privacy(False) \
            .continue_processing(False) \
            .text_content(text_content) \
            .image_key(image_key) \
            .build()

    reply_content = "运单号不能为空"
    message_id = req_data.event.message.message_id
    user_id = req_data.event.sender.sender_id.user_id
    app_id = req_data.header.app_id
    has_matches, matchesNo, matches = matches_orderNo(text_content)
    if has_matches:
        fileNames = []
        filePaths = []
        newFileNames = []
        visitPaths = []
        xieTongFilePaths = []
        fileName = None
        filePath = None
        newFileName = None
        visitPath = None
        xieTongFilePath = None
        remark_boy_list = []
        for image in image_key:
            # start_time = time.time()  # 记录开始时间
            response: GetMessageResourceResponse = get_message_file(app_id, message_id, image, "image")
            if response.success():

                file_path = os.getcwd() + "\\tempfile\\" + str(uuid.uuid4()).replace("-", "") + ".png"
                with open(file_path, "wb") as file:
                    file.write(response.file.read())
                res: HttpResponse = upload_image(
                    {"uploadType": 2, "orderNo": matches[0], "outNo": "qihang"},
                    open(file_path, 'rb'))
                if res.success:
                    fileNames.append(res.result.fileName)
                    filePaths.append(res.result.filePath)
                    newFileNames.append(res.result.newFileName)
                    visitPaths.append(res.result.visitPath)
                    xieTongFilePaths.append(res.result.xieTongFilePath)
                os.remove(file_path)
            # end_time = time.time()  # 记录结束时间
            # elapsed_time = end_time - start_time  # 计算耗时
            # print("上传图片子程序执行耗时：", elapsed_time, "秒")
        if len(fileNames) > 0:
            fileName = ','.join(fileNames)
            filePath = ','.join(filePaths)
            newFileName = ','.join(newFileNames)
            visitPath = ','.join(visitPaths)
            xieTongFilePath = ','.join(xieTongFilePaths)
        user = get_user(app_id, user_id)
        userName = "蔺亮"
        if user.success:
            userName = user.data.user.name
        for match in matches:
            expressTrack, expressTrackNo = query_expressTrack(match)
            if expressTrack.success and expressTrackNo > 0:
                if len(expressTrack.result[expressTrackNo - 1].nxtScanSite) > 5:
                    jgReceiveSite = expressTrack.result[expressTrackNo - 1].nxtScanSite
                else:
                    jgReceiveSite = expressTrack.result[expressTrackNo - 1].scanSite

                if match[:2] == "46":
                    problemContent = "贵公司您好：您有一票网络平台B投诉单已经超时溢出，单号为：【 " + match + (
                        "】，客户至今未收到快递，为了避免客户在拼多多平台产生二次申诉（100元"
                        "/票），对贵司造成更大的经济损失，此件总部已按遗失件面向收件人进行理赔。如有疑问可钉钉联系：刘新育")
                else:
                    problemContent = "贵公司您好：您有一票网络平台B投诉单已经超时溢出，单号为：【 " + match + (
                        "】客户至今未收到快递，为了避免客户在平台产生二次申诉（100"
                        "元/票），对贵司造成更大的经济损失，此件总部已按遗失件面向收件人进行理赔。如有疑问可钉钉联系：刘新育")
                Message = ServiceMessage.builder() \
                    .orderNo(match) \
                    .fileName(fileName) \
                    .xieTongFilePath(xieTongFilePath) \
                    .filePath(filePath) \
                    .visitPath(visitPath) \
                    .createBy(userName) \
                    .newFileName(newFileName) \
                    .createId("1651555067645681666") \
                    .createMobile("13158626321") \
                    .workExpressType("222") \
                    .outNo("qihangjingang") \
                    .problemContent(problemContent) \
                    .jgPublishSite("999111") \
                    .jgReceiveSite(jgReceiveSite) \
                    .build()
                res = send_incoming_message(Message.to_dict())
                if res.success:
                    remark_boy_list.append(RemarkBoy.builder() \
                                           .orderNo(match) \
                                           .remark("以上单号的理赔信息已同步网点") \
                                           .build()
                                           )
                else:
                    remark_boy_list.append(RemarkBoy.builder() \
                                           .orderNo(match) \
                                           .remark("以上单号的理赔信息同步网点失败：" + res.message) \
                                           .build())
            else:
                remark_boy_list.append(RemarkBoy.builder() \
                                       .orderNo(match) \
                                       .remark("以上单号的理赔信息同步网点失败：物流轨迹不能为空") \
                                       .build())
        reply_content = group_by_remark(remark_boy_list)

    return WinCard.builder() \
        .card(build_card("处理结果", get_current_time(), reply_content, False, False)) \
        .mate(True) \
        .privacy(False) \
        .continue_processing(False) \
        .text_content(text_content) \
        .image_key(image_key) \
        .build()


# 帮助|help
def handle_help(req_data: MessageReceiveEvent, text_content, image_key) -> WinCard:
    return WinCard.builder() \
        .card(help_card_build(req_data.event.sender.sender_id.user_id)) \
        .mate(True) \
        .continue_processing(False) \
        .text_content(text_content) \
        .image_key(image_key) \
        .build()


# 清除|clear
def handle_clear(req_data: MessageReceiveEvent, text_content, image_key) -> WinCard:
    return WinCard.builder() \
        .card(clear_card_build()) \
        .mate(True) \
        .continue_processing(False) \
        .text_content(text_content) \
        .image_key(image_key) \
        .build()


# 模型|model
def handle_model(req_data: MessageReceiveEvent, text_content, image_key) -> WinCard:
    return WinCard.builder() \
        .card(model_select_card_build(req_data.event.sender.sender_id.user_id)) \
        .mate(True) \
        .continue_processing(False) \
        .text_content(text_content) \
        .image_key(image_key) \
        .build()


# 发散模式|ai_mode
def handle_diverge(req_data: MessageReceiveEvent, text_content, image_key) -> WinCard:
    return WinCard.builder() \
        .card(diverge_select_card_build(req_data.event.sender.sender_id.user_id)) \
        .mate(True) \
        .continue_processing(False) \
        .text_content(text_content) \
        .image_key(image_key) \
        .build()


# 卡片事件回调处理程序
# 清除|clear
def card_clear(data: Card) -> WinCard:
    redis.delete(":message_context:" + data.user_id)
    return WinCard.builder() \
        .card(robot_reminder_card_build("🆑 机器人提醒",
                                        "已删除此话题的上下文信息",
                                        "我们可以开始一个全新的话题，继续找我聊天吧")) \
        .mate(True) \
        .continue_processing(False) \
        .build()


# 点赞
def card_praise(data: Card) -> WinCard:
    redis.delete(":message_context:" + data.user_id)
    # if data.action.value.get("success"):
    messagedata = get_message(data.app_id, data.open_message_id)
    # if messagedata.success():
    text_content = get_text_from_json(messagedata.data.items[0].body.content)
    return WinCard.builder() \
        .card(build_card("🎉 处理结果",
                         get_current_time(),
                         text_content, True, False)) \
        .mate(True) \
        .continue_processing(False) \
        .build()


# 模型|model
def card_model(data: Card) -> WinCard:
    user_id = data.user_id
    model_type = data.action.option
    robot_spark_url = ""
    model_type_name = ""
    if model_type == "general":
        model_type_name = "spark1.5-chat"
        robot_spark_url = "ws://spark-api.xf-yun.com/v1.1/chat"
    elif model_type == "generalv2":
        model_type_name = "spark2.1-chat"
        robot_spark_url = "ws://spark-api.xf-yun.com/v2.1/chat"
    elif model_type == "generalv3":
        model_type_name = "spark3.1-chat"
        robot_spark_url = "ws://spark-api.xf-yun.com/v3.1/chat"
    robot_user_model = get_robot_user_model(user_id)
    robot_user_model.robot_domain = model_type
    robot_user_model.robot_spark_url = robot_spark_url
    cache.set(":robot_user_model:" + user_id, robot_user_model.to_dict())
    return WinCard.builder() \
        .card(robot_reminder_card_build("🚀 机器人提醒",
                                        "已选择模型：**" + model_type_name + "**",
                                        "输入<发散模式> 或 /ai_mode 即可选择发散模式")) \
        .mate(True) \
        .continue_processing(False) \
        .build()


# 发散模式|ai_mode
def card_diverge(data: Card) -> WinCard:
    diverge_type = data.action.option
    user_id = data.user_id
    diverge_type_name = ""
    if diverge_type == "1.0":
        diverge_type_name = "严谨"
    elif diverge_type == "0.75":
        diverge_type_name = "简洁"
    elif diverge_type == "0.5":
        diverge_type_name = "标准"
    elif diverge_type == "0.25":
        diverge_type_name = "发散"
    robot_user_model = get_robot_user_model(user_id)
    robot_user_model.robot_temperature = float(diverge_type)
    cache.set(":robot_user_model:" + user_id, robot_user_model.to_dict())
    return WinCard.builder() \
        .card(robot_reminder_card_build("🤖 机器人提醒",
                                        "已选择发散模式为：**" + diverge_type_name + "**",
                                        "输入<模型> 或 model 即可切换AI模型")) \
        .mate(True) \
        .continue_processing(False) \
        .build()


message_intents = [
    (r'理赔专用', handle_process_claim),
    (r'帮助|help', handle_help),
    (r'清除|clear', handle_clear),
    (r'模型|model', handle_model),
    (r'发散模式|ai_mode', handle_diverge),
]

card_event_intents = [
    (r'praise', card_praise),
    (r'clear', card_clear),
    (r'domain_version', card_model),
    (r'temperature', card_diverge),
]


# 消息意图处理
def message_handle_process(req_data: MessageReceiveEvent) -> WinCard:
    text_content = ""
    image_key = []
    data = json.loads(req_data.event.message.content)
    if req_data.event.message.message_type == "post":
        for datacontent in data["content"]:
            for content in datacontent:
                if content["tag"] == "text":
                    text_content += content["text"]
                elif content["tag"] == "img":
                    image_key.append(content["image_key"])
    elif req_data.event.message.message_type == "text":
        text_content = data["text"]
    card_result = WinCard()
    for pattern, handler in message_intents:
        if re.search(pattern, text_content):
            return handler(req_data, text_content, image_key)
    return card_result


# 处理卡片回调
def do_interactive_card(data: Card) -> Any:
    cache.set(":card_event:" + data.open_message_id, "Event has been handle", timeout=25200)
    # 进入消息处理流程，并获取回复内容
    handle_content = card_handle_process(data)
    # 命中预设流程，进行回复
    if handle_content.mate:
        return handle_content.card
    return lark.JSON.marshal({"success": False, "message": "本事件未被定义！", "code": 200})


def card_handle_process(data: Card) -> WinCard:
    content = data.action.value.get("text")
    card_result = WinCard()
    for pattern, handler in card_event_intents:
        if re.search(pattern, content):
            return handler(data)
    return card_result
