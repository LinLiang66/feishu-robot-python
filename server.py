#!/usr/bin/env python3.8


import asyncio
import importlib
import json
import logging
import os
import time

import lark_oapi
import requests
from asgiref.wsgi import WsgiToAsgi
from dotenv import load_dotenv, find_dotenv
from flask import Flask, jsonify
from lark_oapi.adapter.flask import *
from flask_caching import Cache
import SparkApi
from api import reply_message, build_card, get_current_time, do_interactive_card, is_within_five_seconds

from event import MessageReceiveEvent, UrlVerificationEvent, EventManager
from model import Card
from serverPiluin import message_handle_process

config = {
    "DEBUG": True,  # some Flask specific configs
    "CACHE_TYPE": "redis",  # Flask-Caching related configs
    "CACHE_REDIS_HOST": '101.227.48.127',
    "CACHE_REDIS_PORT": 6379,
    "CACHE_REDIS_PASSWORD": 'Lin927919732',
    "CACHE_REDIS_DB": 0,

}

# load env parameters form file named .env
load_dotenv(find_dotenv())

app = Flask(__name__)
asgi_app = WsgiToAsgi(app)
app.config.from_mapping(config)
cache = Cache(app)

config_module = importlib.import_module("config")
config_instance = config_module.Config()

print(config_instance.setting1)  # 输出 "value1"
print(config_instance.setting2)  # 输出 "value2"

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
    # cache.set(req_data.event.sender.sender_id.open_id, text_content, timeout=18)
    # 进入消息处理流程，并获取回复内容
    handle_content = message_handle_process(text_content)
    # 命中预设流程，进行回复
    if handle_content.mate:
        card_content = handle_content.card
        reply_message(app_id, message_id, card_content, "interactive")
    # 命中无需继续往下处理，直接返回
    if not handle_content.continue_processing:
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
    event_handler, event = event_manager.get_handler_with_event(VERIFICATION_TOKEN, ENCRYPT_KEY)
    if cache.get(":message_event:"+event.header.event_id) is None:
        cache.set(":message_event:"+event.header.event_id, "Message has been handle", timeout=25200)
        return event_handler(event)
    return jsonify({"success": False, "message": "Message has been handle!！", "code": 200,
                    "timestamp": int(time.time() * 1000)})


@app.route("/card", methods=["POST"])
async def card():
    dict_data = request.get_json()
    callback_type = dict_data.get("type")
    # only verification data has callback_type, else is event
    if callback_type == "url_verification":
        # url verification, just need return challenge
        if dict_data.get("token") != VERIFICATION_TOKEN:
            raise Exception("VERIFICATION_TOKEN is invalid")
        return jsonify({"challenge": dict_data.get("challenge")})

    data = Card(dict_data)
    if cache.get(":card_event:"+data.open_message_id) is None:
        cache.set(":card_event:"+data.open_message_id, "Event has been handle", timeout=25200)
        resp = do_interactive_card(data)
        return resp
    return jsonify({"success": False, "message": "Message has been handle!！", "code": 200,
                    "timestamp": int(time.time() * 1000)})


if __name__ == "__main__":
    # init()
    app.run(host="0.0.0.0", port=8081, debug=False)
