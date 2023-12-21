import json
import os
from typing import *

import requests
from lark_oapi import BaseRequest, HttpMethod, RawResponse, JSON, UTF_8, logger

from util.AES import AESCipher
from util.Httputil import Http
from util.yundaModel import HttpResponse, BarCodeMessage, EncryptedRequestBoy, ImageMessage

url = "https://qihang.yundasys.com/"  # 启航生产环境
partnerCode = "qihang"  # 启航生产环境
key = "YvIOPlG2lrJGJ5ar"  # 启航生产环境

enterpartnerCode = "qihangjingang"  # 进港专用
enterkey = "mRu7Jfxf35qZhfit"  # 进港专用


# 条码分配查询
def query_bar_code_record(waybill_no):
    # 构造加密数据
    encrypted_data = AESCipher().encrypt(json.dumps({"waybillNo": waybill_no}), key)
    # 构造请求内容
    RequestBoy: EncryptedRequestBoy = EncryptedRequestBoy.builder() \
        .partnerCode(partnerCode) \
        .logisticsInterface(encrypted_data) \
        .build()
    # 构造请求对象
    request: BaseRequest = BaseRequest.builder() \
        .uri(url + "manager/out/distribute") \
        .http_method(HttpMethod.POST) \
        .body(RequestBoy.to_dict()) \
        .headers({"Content-Type": "application/json"}) \
        .build()
    # 发起请求
    resp: RawResponse = Http.execute(request)
    res: HttpResponse = JSON.unmarshal(str(resp.content, UTF_8), HttpResponse)
    if res.success:
        res.result = BarCodeMessage(res.result)
    else:
        logger.error(f"{str(request.http_method.name)} {request.uri} , "
                     f"headers: {JSON.marshal(request.headers)}, "
                     f"params: {JSON.marshal(request.queries)}, "
                     f"body: {str(request.body, UTF_8) if isinstance(request.body, bytes) else request.body},"
                     f"code: {res.code}, "
                     f"success: {res.success}, "
                     f"message: {res.message}")
    return res


# 发送进港留言
def send_incoming_message(content):
    # 构造加密数据
    encrypted_data = AESCipher().encrypt(json.dumps(content), enterkey)
    # 构造请求内容
    RequestBoy: EncryptedRequestBoy = EncryptedRequestBoy.builder() \
        .partnerCode(enterpartnerCode) \
        .logisticsInterface(encrypted_data) \
        .build()

    # 构造请求对象
    request: BaseRequest = BaseRequest.builder() \
        .uri(url + "manager/out/send/ServiceMessage") \
        .http_method(HttpMethod.POST) \
        .body(RequestBoy.to_dict()) \
        .headers({"Content-Type": "application/json"}) \
        .build()
    # 发起请求
    resp: RawResponse = Http.execute(request)
    res: HttpResponse = JSON.unmarshal(str(resp.content, UTF_8), HttpResponse)
    if not res.success:
        logger.error(f"{str(request.http_method.name)} {request.uri} , "
                     f"params: {JSON.marshal(request.queries)}, "
                     f"body: {str(request.body, UTF_8) if isinstance(request.body, bytes) else request.body},"
                     f"code: {res.code}, "
                     f"success: {res.success}, "
                     f"message: {res.message}")

    return res


def upload_image(content, file: IO[Any]):
    # 图片文件路径
    files = {'file': file}
    encrypted_data = AESCipher().encrypt(json.dumps(content), key)
    # 构造请求内容
    RequestBoy: EncryptedRequestBoy = EncryptedRequestBoy.builder() \
        .logisticsInterface(encrypted_data) \
        .partnerCode(partnerCode) \
        .build()
    # 发送POST请求
    response = requests.post(url + "manager/out/uplod/img", files=files, data=RequestBoy.to_dict())
    res: HttpResponse = JSON.unmarshal(str(response.content, UTF_8), HttpResponse)
    if res.success:
        res.result = ImageMessage(res.result)
    else:
        logger.error(
            f"code: {res.code}, "
            f"success: {res.success}, "
            f"message: {res.message}")
    return res


if __name__ == "__main__":
    if os.path.exists("E:\\桌面\\推广.jpg"):
        file = open("E:\\桌面\\推广.jpg", "rb")

        response: HttpResponse = upload_image({"uploadType": 1, "orderNo": "318793069369832", "outNo": "qihang"},
                                                file)

        print(response.result.fileName)
