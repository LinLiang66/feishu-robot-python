#!/usr/bin/env python3.8

import os
import logging

import lark_oapi
from lark_oapi.adapter.flask import *
import requests

from api import reply_message, build_card, get_current_time, do_interactive_card

from event import MessageReceiveEvent, UrlVerificationEvent, EventManager
from flask import Flask, jsonify
from dotenv import load_dotenv, find_dotenv
import json

from model import Card

# load env parameters form file named .env
load_dotenv(find_dotenv())

app = Flask(__name__)

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

    text_content = data["text"]
    # echo text message
    card_content = build_card("处理结果", get_current_time(), text_content,False)
    reply_message(app_id, message_id, card_content, "interactive")

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
def callback_event_handler():
    # init callback instance and handle
    event_handler, event = event_manager.get_handler_with_event(VERIFICATION_TOKEN, ENCRYPT_KEY)
    return event_handler(event)


@app.route("/card", methods=["POST"])
def card():
    data = Card(request.get_json())
    resp = do_interactive_card(data)
    return resp


if __name__ == "__main__":
    # init()
    app.run(host="0.0.0.0", port=8081, debug=False)
