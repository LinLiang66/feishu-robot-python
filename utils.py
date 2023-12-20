import base64
import json
from typing import TypeVar

from lark_oapi import BaseRequest, RawResponse, JSON, UTF_8, logger, HttpMethod
from requests_toolbelt import MultipartEncoder

import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from model import HttpResponse



class Obj(dict):
    def __init__(self, d):
        super().__init__()
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
                setattr(self, a, [Obj(x) if isinstance(x, dict) else x for x in b])
            else:
                setattr(self, a, Obj(b) if isinstance(b, dict) else b)


def dict_2_obj(d: dict):
    return Obj(d)









class Http(object):

    @staticmethod
    def execute(req: BaseRequest) -> RawResponse:
        data = req.body
        if data is not None and not isinstance(data, MultipartEncoder):
            data = JSON.marshal(req.body).encode(UTF_8)

        response = requests.request(
            str(req.http_method.name),
            req.uri,
            headers=req.headers,
            params=req.queries,
            data=data,
            timeout=None,
        )

        logger.debug(f"{str(req.http_method.name)} {req.uri} {response.status_code}, "
                     f"headers: {JSON.marshal(req.headers)}, "
                     f"params: {JSON.marshal(req.queries)}, "
                     f"body: {str(data, UTF_8) if isinstance(data, bytes) else data}")

        resp = RawResponse()
        resp.status_code = response.status_code
        resp.headers = dict(response.headers)
        resp.content = response.content

        return resp


class AESCipher:
    def __init__(self):
        self.aes_key = None

    @staticmethod
    def encrypt(content, aes_key):
        if not content:
            print("AES encrypt: the content is null!")
            return None
        if len(aes_key) == 16:
            try:
                cipher = AES.new(aes_key.encode(), AES.MODE_ECB)
                encrypted = cipher.encrypt(pad(content.encode(), AES.block_size))
                return base64.b64encode(encrypted).decode()
            except Exception as e:
                print("AES encrypt exception:", e)
                raise RuntimeError(e)
        else:
            print("AES encrypt: the aesKey is null or error!")
            return None

    @staticmethod
    def decrypt(content, aes_key):
        if not content:
            print("AES decrypt: the content is null!")
            return None
        if len(aes_key) == 16:
            try:
                cipher = AES.new(aes_key.encode(), AES.MODE_ECB)
                decrypted = unpad(cipher.decrypt(base64.b64decode(content)), AES.block_size)
                return decrypted.decode()
            except Exception as e:
                print("AES decrypt exception:", e)
                raise RuntimeError(e)
        else:
            print("AES decrypt: the aesKey is null or error!")
            return None


def distribute(waybill_no):
    body = {"waybillNo": waybill_no}
    aes_cipher = AESCipher()
    encrypted_data = aes_cipher.encrypt(json.dumps(body), "YvIOPlG2lrJGJ5ar")
    boy = {"logisticsInterface": encrypted_data, "partnerCode": "qihang"}

    # 构造请求对象
    request: BaseRequest = BaseRequest.builder() \
        .uri("https://qihang.yundasys.com/" + "manager/out/distribute") \
        .http_method(HttpMethod.POST) \
        .body(boy) \
        .headers({"Content-Type": "application/json"}) \
        .build()

    # 发起请求
    # resp: RawResponse = Http.execute(request)

    # print(resp.content)
    # 反序列化
    # response: HttpResponse = HttpResponse(str(resp.content, UTF_8))

    return Http.execute(request)


if __name__ == "__main__":
    BarCodeMessage = TypeVar('BarCodeMessage')
    response: RawResponse = distribute("433624511290817")

    print(str(response.content, UTF_8))

    res: HttpResponse[BarCodeMessage] = JSON.unmarshal(str(response.content, UTF_8), HttpResponse[BarCodeMessage])
    # res: HttpResponse(d=barcode_message) = JSON.unmarshal(str(response.content, UTF_8), HttpResponse)
    print(res.to_dict())
    print(res.result)
