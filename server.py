#!/usr/bin/env python3.8


import asyncio
import json
import logging
import time

import requests
from asgiref.wsgi import WsgiToAsgi
from dotenv import load_dotenv, find_dotenv
from flask import Flask, jsonify
from lark_oapi.adapter.flask import *

import SparkApi
from api import reply_message, get_current_time, send_privacy_card_message
from cardBuild import help_card_build, build_card
from event import MessageReceiveEvent, UrlVerificationEvent, EventManager, MemberDeletedReceiveEvent, \
    MemberAddedReceiveEvent
from exts import cache
from model import Card, AppCache
from serverPiluin import message_handle_process, do_interactive_card

# load env parameters form file named .env
load_dotenv(find_dotenv())

app = Flask(__name__)
asgi_app = WsgiToAsgi(app)

cache.init_app(app)

event_manager = EventManager()


# 异步调用讯飞星火认知大模型
async def async_iFlytek_sendMessage(app_id: str, message_id: str, user_id: str, message) -> None:
    SparkApi.sendMessage(app_id, message_id, user_id, message)


# 异步处理用户进群事件
async def async_member_added_event_handler(req_data: MemberAddedReceiveEvent):
    app_id = req_data.header.app_id
    chat_id = req_data.event.chat_id
    users = req_data.event.users
    for user in users:
        send_privacy_card_message(app_id, chat_id, user.user_id.user_id, user.user_id.open_id, "interactive",
                                  help_card_build(user.user_id.user_id))


@event_manager.register("url_verification")
def request_url_verify_handler(req_data: UrlVerificationEvent):
    return jsonify({"challenge": req_data.event.challenge})


@event_manager.register("im.chat.member.user.added_v1")
def member_added_receive_event_handler(req_data: MemberAddedReceiveEvent):
    asyncio.create_task(
        async_member_added_event_handler(req_data))
    return jsonify()


@event_manager.register("im.chat.member.user.deleted_v1")
def member_deleted_receive_event_handler(req_data: MemberDeletedReceiveEvent):
    return jsonify()


@event_manager.register("im.message.receive_v1")
def message_receive_event_handler(req_data: MessageReceiveEvent):
    message_id = req_data.event.message.message_id
    user_id = req_data.event.sender.sender_id.user_id
    if cache.get(":message_event:" + message_id):
        return jsonify({"success": False, "message": "Message has been handle", "code": 200,
                        "timestamp": int(time.time() * 1000)})
    cache.set(":message_event:" + message_id, "Message has been handle", timeout=25200)
    app_id = req_data.header.app_id
    message = req_data.event.message
    if message.message_type == "text" or message.message_type == "post":
        # 进入消息处理流程，并获取回复内容
        handle_content = message_handle_process(req_data)
        # 命中预设场景流程，进行回复，分单聊、群聊
        if handle_content.mate:
            card_content = handle_content.card
            if req_data.event.message.chat_type == "group":
                if handle_content.privacy:
                    send_privacy_card_message(app_id, req_data.event.message.chat_id,
                                              req_data.event.sender.sender_id.user_id,
                                              req_data.event.sender.sender_id.open_id, "interactive",
                                              card_content)
                else:
                    reply_message(app_id, message_id, card_content, "interactive")
            elif req_data.event.message.chat_type == "p2p":
                reply_message(app_id, message_id, card_content, "interactive")

        # 命中无需继续往下处理，直接返回
        if not handle_content.continue_processing:
            return jsonify()
        # 构造首次响应卡片
        card_content = build_card("处理结果", get_current_time(), "", False, True)
        # 回复空卡片消息，并拿到新的message_id
        message_boy = reply_message(app_id, message_id, card_content, "interactive")
        if message_boy.success():
            text_content = handle_content.text_content
            if text_content is None:
                data = json.loads(req_data.event.message.content)
                if req_data.event.message.message_type == "post":
                    image_key = []
                    for datacontent in data["content"]:
                        for content in datacontent:
                            if content["tag"] == "text":
                                text_content += content["text"]
                            elif content["tag"] == "img":
                                image_key.append(content["image_key"])
                elif req_data.event.message.message_type == "text":
                    text_content = data["text"]

            # 异步调用大模型实现打字机问答功能
            asyncio.create_task(
                async_iFlytek_sendMessage(app_id, message_boy.data.message_id, user_id,
                                          text_content))
        return jsonify()
    else:
        logging.error("Other types of messages have not been processed yet")
        return jsonify()


@app.errorhandler
def msg_error_handler(ex):
    logging.error(ex)
    response = jsonify(message=str(ex))
    response.status_code = (
        ex.response.status_code if isinstance(ex, requests.HTTPError) else 500
    )
    return response


@app.route("/webhook/event/<appid>", methods=["POST"])
async def callback_event_handlerv2(appid):
    if appid is None:
        return jsonify({"success": False, "message": "APPID Cannot be empty", "code": 200,
                        "timestamp": int(time.time() * 1000)})
    appCacheJson = cache.get(":robot_app_key:" + appid)
    if appCacheJson is None:
        return jsonify({"success": False, "message": "APPID is invalid", "code": 200,
                        "timestamp": int(time.time() * 1000)})
    appCache = AppCache(appCacheJson)
    event_handler, event = event_manager.get_handler_with_event(appCache.verification_token, appCache.encrypt_key)
    return event_handler(event)


@app.route("/webhook/card/<appid>", methods=["POST"])
async def cardv2(appid):
    if appid is None:
        return jsonify({"success": False, "message": "APPID Cannot be empty", "code": 200,
                        "timestamp": int(time.time() * 1000)})
    appCacheJson = cache.get(":robot_app_key:" + appid)
    if appCacheJson is None:
        return jsonify({"success": False, "message": "APPID is invalid", "code": 200,
                        "timestamp": int(time.time() * 1000)})
    appCache = AppCache(appCacheJson)
    dict_data = request.get_json()
    callback_type = dict_data.get("type")
    # only verification data has callback_type, else is event
    if callback_type == "url_verification":
        # url verification, just need return challenge
        if dict_data.get("token") != appCache.verification_token:
            raise Exception("VERIFICATION_TOKEN is invalid")
        return jsonify({"challenge": dict_data.get("challenge")})

    data = Card(dict_data)

    if cache.get(":card_event:" + data.open_message_id) is None:
        resp = do_interactive_card(data)
        return resp
    return jsonify({"success": False, "message": "Event has been handle", "code": 200,
                    "timestamp": int(time.time() * 1000)})


if __name__ == "__main__":
    # key = AppCache.builder() \
    #     .appid("cli_a50d7635f8bb9010b77111") \
    #     .app_secret("HUZ7Ea0eVDrUAfwW2Kgi2fttmwl4U17z57711") \
    #     .app_role_type(1) \
    #     .encrypt_key("gez70dUsVLgkR8saxWlPldRGfnS0I817p71117") \
    #     .verification_token("u4sUMaG3uWxZIa1eNPccQmgCFBuepXLop711117") \
    #     .robot_appid("f4131171c24") \
    #     .robot_api_secret("ZjZhNGM3YzkwY1zJhYzIwYjUxYjk311ZDMx77") \
    #     .robot_api_key("7506058015c6e519111737087ec504f600d77") \
    #     .robot_domain("generalv3") \
    #     .robot_spark_url("ws://spark-api.xf-yun.com/v3.1/chat") \
    #     .robot_temperature(1) \
    #     .build()
    # cache.set(":robot_app_key:" + key.appid, key.to_dict())
    # print(cache.get(":robot_app_key:" + key.appid))
    app.run(host="0.0.0.0", port=8081, debug=False)
