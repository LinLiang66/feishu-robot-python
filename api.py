import datetime
import json
import re
import time
import uuid

import lark_oapi as lark

from lark_oapi.api.im.v1 import *

from exts import cache
from model import Card, AppCache, PrivacyCardMessageRequest, PrivacyCardMessageRequestBody
from redisServer import redis
from serverPiluin import card_handle_process


# 获取现行时间 yyyy-MM-dd HH:mm:ss格式
def get_current_time():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


# 判断指定时间与现行时间是否超过五秒
def is_within_five_seconds(timestamp) -> bool:
    current_time = int(time.time() * 1000)
    time_difference = current_time - int(timestamp)
    return time_difference <= 5000


# 根据APP_ID获取APP_SECRET
def get_app_secret(appid):
    appCacheJson = cache.get(":robot_app_key:" + appid)
    if appCacheJson:
        return AppCache(appCacheJson).app_secret
    return None


# 上传图片
def _upload_image(app_id: str) -> str:
    # 创建client
    client = lark.Client.builder() \
        .app_id(app_id) \
        .app_secret(get_app_secret(app_id)) \
        .log_level(lark.LogLevel.ERROR) \
        .build()

    file = open("alert.png", "rb")
    request = CreateImageRequest.builder() \
        .request_body(CreateImageRequestBody.builder()
                      .image_type("message")
                      .image(file)
                      .build()) \
        .build()

    response = client.im.v1.image.create(request)

    if not response.success():
        raise Exception(
            f"client.im.v1.image.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")

    return response.data.image_key


# 获取会话信息
def get_chat_info(chat_id: str, app_id: str) -> GetChatResponseBody:
    # 创建client
    client = lark.Client.builder() \
        .app_id(app_id) \
        .app_secret(get_app_secret(app_id)) \
        .log_level(lark.LogLevel.ERROR) \
        .build()

    request = GetChatRequest.builder() \
        .chat_id(chat_id) \
        .build()

    response = client.im.v1.chat.get(request)

    if not response.success():
        raise Exception(
            f"client.im.v1.chat.get failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")

    return response.data


# 更新会话名称
def update_chat_name(chat_id: str, chat_name: str, app_id: str):
    # 创建client
    client = lark.Client.builder() \
        .app_id(app_id) \
        .app_secret(get_app_secret(app_id)) \
        .log_level(lark.LogLevel.ERROR) \
        .build()

    request: UpdateChatRequest = UpdateChatRequest.builder() \
        .chat_id(chat_id) \
        .request_body(UpdateChatRequestBody.builder()
                      .name(chat_name)
                      .build()) \
        .build()

    response: UpdateChatResponse = client.im.v1.chat.update(request)

    if not response.success():
        raise Exception(
            f"client.im.v1.chat.update failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")


# 处理消息回调
def do_p2_im_message_receive_v1(data: P2ImMessageReceiveV1, ) -> None:
    app_id = data.header.app_id
    # 创建client
    client = lark.Client.builder() \
        .app_id(app_id) \
        .app_secret(get_app_secret(app_id)) \
        .log_level(lark.LogLevel.ERROR) \
        .build()

    msg = data.event.message
    if "/solve" in msg.content:
        request = CreateMessageRequest.builder() \
            .receive_id_type("chat_id") \
            .request_body(CreateMessageRequestBody.builder()
                          .receive_id(msg.chat_id)
                          .msg_type("text")
                          .content("{\"text\":\"问题已解决，辛苦了!\"}")
                          .build()) \
            .build()

        response = client.im.v1.chat.create(request)

        if not response.success():
            raise Exception(
                f"client.im.v1.chat.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")

        # 获取会话信息
        chat_info = get_chat_info(msg.chat_id, app_id)
        name = chat_info.name
        if name.startswith("[跟进中]"):
            name = "[已解决]" + name[5:]
        elif not name.startswith("[已解决]"):
            name = "[已解决]" + name

        # 更新会话名称
        update_chat_name(msg.chat_id, name, app_id)


def get_message(app_id: str, message_id: str) -> GetMessageResponse:
    # 创建client
    client = lark.Client.builder() \
        .app_id(app_id) \
        .app_secret(get_app_secret(app_id)) \
        .log_level(lark.LogLevel.ERROR) \
        .build()

    # 构造请求对象
    request: GetMessageRequest = GetMessageRequest.builder() \
        .message_id(message_id) \
        .build()

    # 发起请求
    response: GetMessageResponse = client.im.v1.message.get(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.im.v1.message.get failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
        return response

    return response


def get_text_from_json(json_str):
    data = json.loads(json_str)
    elements = data["elements"]
    first_element = elements[0]
    third_member = first_element[2]
    text = third_member["text"]
    return text


# 处理卡片回调
def do_interactive_card(data: Card) -> Any:
    cache.set(":card_event:" + data.open_message_id, "Event has been handle", timeout=25200)
    # 进入消息处理流程，并获取回复内容
    handle_content = card_handle_process(data)
    # 命中预设流程，进行回复
    if handle_content.mate:
        return handle_content.card
    return lark.JSON.marshal({"success": False, "message": "本事件未被定义！", "code": 200})


def updateTextCard(app_id, message_id, content) -> bool:
    # 创建client
    client = lark.Client.builder() \
        .app_id(app_id) \
        .app_secret(get_app_secret(app_id)) \
        .log_level(lark.LogLevel.ERROR) \
        .build()

    # 构造请求对象
    request: PatchMessageRequest = PatchMessageRequest.builder() \
        .message_id(message_id) \
        .request_body(PatchMessageRequestBody.builder()
                      .content(content)
                      .build()) \
        .build()

    # 发起请求
    response: PatchMessageResponse = client.im.v1.message.patch(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.im.v1.message.patch failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")

    return response.success()


# 通用发送消息
def send_message(app_id: str, receive_id_type: str, receive_id: str, msg_type: str, content: str) -> bool:
    # 创建client
    client = lark.Client.builder() \
        .app_id(app_id) \
        .app_secret(get_app_secret(app_id)) \
        .log_level(lark.LogLevel.ERROR) \
        .build()

    # 构造请求对象
    request: CreateMessageRequest = CreateMessageRequest.builder() \
        .receive_id_type(receive_id_type) \
        .request_body(CreateMessageRequestBody.builder()
                      .receive_id(receive_id)
                      .msg_type(msg_type)
                      .content(content)
                      .uuid(str(uuid.uuid4()))
                      .build()) \
        .build()

    # 发起请求
    response: CreateMessageResponse = client.im.v1.message.create(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.im.v1.message.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
        return response.success()

    # 处理业务结果
    return response.success()


# 通用发送消息
def send_privacy_card_message(app_id: str, chat_id: str, user_id: str, open_id: str,  msg_type: str,
                              content: str) -> bool:
    # 创建client
    client = lark.Client.builder() \
        .app_id(app_id) \
        .app_secret(get_app_secret(app_id)) \
        .log_level(lark.LogLevel.ERROR) \
        .build()

    # 构造请求对象
    request: PrivacyCardMessageRequest = PrivacyCardMessageRequest.builder() \
        .request_body(PrivacyCardMessageRequestBody.builder() \
                      .chat_id(chat_id) \
                      .user_id(user_id) \
                      .open_id(open_id) \
                      .msg_type(msg_type)
                      .card(json.loads(content))
                      .build()) \
        .build()

    # 发起请求
    response: CreateMessageResponse = client.im.v1.message.create(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.im.v1.message.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
        return response.success()

    # 处理业务结果
    return response.success()


# 通用回复消息
def reply_message(app_id: str, message_id: str, content: str, msg_type: str) -> ReplyMessageResponse:
    # 创建client
    client = lark.Client.builder() \
        .app_id(app_id) \
        .app_secret(get_app_secret(app_id)) \
        .log_level(lark.LogLevel.ERROR) \
        .build()

    # 构造请求对象
    request: ReplyMessageRequest = ReplyMessageRequest.builder() \
        .message_id(message_id) \
        .request_body(ReplyMessageRequestBody.builder()
                      .content(content)
                      .msg_type(msg_type)
                      .uuid(str(uuid.uuid4()))
                      .build()) \
        .build()
    # 发起请求
    response: ReplyMessageResponse = client.im.v1.message.reply(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.im.v1.message.reply failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
        return response

    # 处理业务结果

    return response


# 构建卡片
def build_card(header: str, time: str, content: str, end: bool, robot: bool) -> str:
    if content:
        content = re.sub(r'(?m)^(.*)$', r'**\1**', content)
    elif robot:
        card = {
            "elements": [
                {
                    "tag": "markdown",
                    "content": content,
                    "text_align": "left"
                },
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": "🤖能力来源:小肉"
                        }
                    ]
                },
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": "正在思考，请稍等..."

                        }
                    ]
                }
            ]
        }

        return lark.JSON.marshal(card)

    if robot:
        if end:
            note = "🤖温馨提示✨✨：输入<帮助> 或 /help 即可获取帮助菜单"
        else:
            note = "正在处理中，请稍等..."

        card = {
            "elements": [
                {
                    "tag": "markdown",
                    "content": content,
                    "text_align": "left"
                },
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": "🤖能力来源:小肉"
                        }
                    ]
                },
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": note

                        }
                    ]
                }
            ]
        }

        return lark.JSON.marshal(card)

    if end:
        card = {
            "elements": [
                {
                    "tag": "column_set",
                    "flex_mode": "none",
                    "background_style": "default",
                    "columns": [
                        {
                            "tag": "column",
                            "width": "weighted",
                            "weight": 1,
                            "vertical_align": "top",
                            "elements": [
                                {
                                    "tag": "div",
                                    "text": {
                                        "content": "**🕐 完成时间：**\n" + time,
                                        "tag": "lark_md"
                                    }
                                },
                                {
                                    "tag": "markdown",
                                    "content": content,
                                    "text_align": "left"
                                }
                            ]
                        }
                    ]
                },
                {
                    "tag": "column_set",
                    "flex_mode": "none",
                    "background_style": "default",
                    "columns": []
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "div",
                    "fields": [
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": "**📝已处理完成，祝您生活愉快**"
                            }
                        }
                    ]
                },
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": "🤖能力来源:小肉"
                        }
                    ]
                }
            ],
            "header": {
                "template": "violet",
                "title": {
                    "content": header,
                    "tag": "plain_text"
                }
            }
        }

        return lark.JSON.marshal(card)

    card = {
        "elements": [
            {
                "tag": "column_set",
                "flex_mode": "none",
                "background_style": "default",
                "columns": [
                    {
                        "tag": "column",
                        "width": "weighted",
                        "weight": 1,
                        "vertical_align": "top",
                        "elements": [
                            {
                                "tag": "div",
                                "text": {
                                    "content": "**🕐 响应时间：**\n" + time,
                                    "tag": "lark_md"
                                }
                            },
                            {
                                "tag": "markdown",
                                "content": content,
                                "text_align": "left"
                            }
                        ]
                    }
                ]
            },
            {
                "tag": "column_set",
                "flex_mode": "none",
                "background_style": "default",
                "columns": []
            },
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": "赞一下"
                        },
                        "type": "primary",
                        "value": {
                            "success": True
                        }
                    },
                    {
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": "踩一下"
                        },
                        "type": "danger",
                        "value": {
                            "success": False
                        }
                    }
                ]
            },
            {
                "tag": "hr"
            },
            {
                "tag": "note",
                "elements": [
                    {
                        "tag": "plain_text",
                        "content": "🤖能力来源:小肉"
                    }
                ]
            }
        ],
        "header": {
            "template": "violet",
            "title": {
                "content": header,
                "tag": "plain_text"
            }
        }
    }

    return lark.JSON.marshal(card)


# length = 0

def getText(user_id, role, content):
    text = redis.get(":message_context:" + user_id)
    if text is None:
        text = []
    jsoncon = {"role": role, "content": content}
    text.append(jsoncon)
    return text


def getlength(text):
    length = 0
    for content in text:
        temp = content["content"]
        leng = len(temp)
        length += leng
    return length


def checklen(user_id, text):
    while getlength(text) > 8000:
        del text[0]
    redis.set(":message_context:" + user_id, text)
    return text
