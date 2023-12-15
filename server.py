#!/usr/bin/env python3.8


import os
import logging
import time

import lark_oapi
from lark_oapi import AESCipher
from lark_oapi.adapter.flask import *
import requests
import asyncio
from asgiref.wsgi import WsgiToAsgi
import SparkApi
from api import reply_message, build_card, get_current_time, do_interactive_card, is_within_five_seconds, contains_help, \
    help_card

from event import MessageReceiveEvent, UrlVerificationEvent, EventManager, InvalidEventException
from flask import Flask, jsonify
from dotenv import load_dotenv, find_dotenv
import json

from model import Card

# load env parameters form file named .env
load_dotenv(find_dotenv())

app = Flask(__name__)
asgi_app = WsgiToAsgi(app)

# load from env
APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")
VERIFICATION_TOKEN = os.getenv("VERIFICATION_TOKEN")
ENCRYPT_KEY = os.getenv("ENCRYPT_KEY")
LARK_HOST = os.getenv("LARK_HOST")
event_manager = EventManager()

# 注册卡片回调
card_handler = lark_oapi.CardActionHandler.builder(ENCRYPT_KEY, VERIFICATION_TOKEN, lark_oapi.LogLevel.DEBUG) \
    .register(do_interactive_card) \
    .build()


async def background_worker(app_id: str, message_id: str, message) -> None:
    SparkApi.sendMessage(app_id, message_id, message)
    pass


@event_manager.register("url_verification")
def request_url_verify_handler(req_data: UrlVerificationEvent):
    # url verification, just need return challenge
    if req_data.event.token != VERIFICATION_TOKEN:
        raise Exception("VERIFICATION_TOKEN is invalid")
    return jsonify({"challenge": req_data.event.challenge})


@event_manager.register("im.message.receive_v1")
def message_receive_event_handler(req_data: MessageReceiveEvent):
    message = req_data.event.message

    if message.message_type != "text":
        logging.warn("Other types of messages have not been processed yet")
        return jsonify()
    app_id = req_data.header.app_id

    message_id = req_data.event.message.message_id

    data = json.loads(message.content)
    # echo text message
    text_content = data["text"]
    if contains_help(text_content):
        # 构造首次响应卡片
        card_content = help_card()
        # 回复空卡片消息，并拿到新的message_id
        reply_message(app_id, message_id, card_content, "interactive")
        return jsonify()

    # 构造首次响应卡片
    card_content = build_card("处理结果", get_current_time(), "", False, True)
    # 回复空卡片消息，并拿到新的message_id
    message_boy = reply_message(app_id, message_id, card_content, "interactive")
    if message_boy.success():
        # 异步调用大模型实现打字机问答功能
        asyncio.create_task(background_worker(app_id, message_boy.data.message_id, text_content))

    return jsonify()


@app.errorhandler
def msg_error_handler(ex):
    logging.error(ex)
    response = jsonify(message=str(ex))
    response.status_code = (
        ex.response.status_code if isinstance(ex, requests.HTTPError) else 500
    )
    return response


@app.route("/", methods=["POST"])
async def callback_event_handler():
    dict_data = json.loads(request.data)

    dict_data = event_manager._decrypt_data(ENCRYPT_KEY, dict_data)
    # get create_time
    create_time = dict_data.get("event").get("message").get("create_time")
    if not is_within_five_seconds(create_time):
        message = {
            "message": "request has exceeded the valid processing time.",
            "success": False,
            "timestamp": int(time.time() * 1000)
        }
        return lark_oapi.JSON.marshal(message)
    event_handler, event = event_manager.get_handler_and_event(dict_data, VERIFICATION_TOKEN, ENCRYPT_KEY)

    # event_handler, event = event_manager.get_handler_with_event(VERIFICATION_TOKEN, ENCRYPT_KEY)

    return event_handler(event)


@app.route("/card", methods=["POST"])
async def card():
    print(request.data)  # 输出：False
    data = Card(request.get_json())
    resp = do_interactive_card(data)
    return resp


if __name__ == "__main__":
    # init()
    app.run(host="0.0.0.0", port=8081, debug=False)
