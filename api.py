import datetime
import json
import uuid

import lark_oapi as lark

from lark_oapi.api.im.v1 import *

from model import Card


# 获取现行时间 yyyy-MM-dd HH:mm:ss格式
def get_current_time():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


# 根据APP_ID获取APP_SECRET
def get_app_secret(send_appid):
    app_secrets = {
        "cli_a5f2a42a243f100b": "zBBkBSVaLQV1Es8LYarDmeaRfKhp5reQ"
    }
    return app_secrets.get(send_appid)


# 上传图片
def _upload_image(app_id: str) -> str:
    # 创建client
    client = lark.Client.builder() \
        .app_id(app_id) \
        .app_secret(get_app_secret(app_id)) \
        .log_level(lark.LogLevel.DEBUG) \
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
        .log_level(lark.LogLevel.DEBUG) \
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
        .log_level(lark.LogLevel.DEBUG) \
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
        .log_level(lark.LogLevel.DEBUG) \
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


# 处理卡片回调
def do_interactive_card(data: Card) -> Any:
    if data.action.value.get("success"):
        return build_card("🎉 谢谢您的肯定是服务的动力", "", "👀 👀 祝您生活愉快！", True)
    return build_card("抱歉给您带来不便，我将继续改进", "", "👀 👀 祝您生活愉快！", True)

# 通用发送消息
def send_message(app_id: str, receive_id_type: str, receive_id: str, msg_type: str, content: str) -> None:
    # 创建client
    client = lark.Client.builder() \
        .app_id(app_id) \
        .app_secret(get_app_secret(app_id)) \
        .log_level(lark.LogLevel.DEBUG) \
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


# 通用回复消息
def reply_message(app_id: str, message_id: str, content: str, msg_type: str) -> None:
    # 创建client
    client = lark.Client.builder() \
        .app_id(app_id) \
        .app_secret(get_app_secret(app_id)) \
        .log_level(lark.LogLevel.DEBUG) \
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
        return

    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))
    return lark.JSON.marshal(response.data, indent=4)


# 构建卡片
def build_card(header: str, time: str, content: str, end: bool) -> str:
    if end:
        card = {
            "elements": [
                {
                    "tag": "markdown",
                    "content": header
                }
            ],
            "header": {
                "title": {
                    "content": content,
                    "tag": "plain_text"
                },
                "template": "carmine"
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
                                "content": "** " + content + "**",
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
                        "tag": "img",
                        "img_key": "img_v3_0264_e0eced13-050f-4636-994d-4dea32a6669g",
                        "alt": {
                            "tag": "plain_text",
                            "content": ""
                        }
                    },
                    {
                        "tag": "plain_text",
                        "content": "能力来源:小肉"
                    },
                    {
                        "tag": "img",
                        "img_key": "img_v3_0264_e0eced13-050f-4636-994d-4dea32a6669g",
                        "alt": {
                            "tag": "plain_text",
                            "content": ""
                        },
                        "mode": "fit_horizontal",
                        "preview": True
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
