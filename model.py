import json
from typing import Dict, Optional, Any

from lark_oapi.core.construct import init
from lark_oapi.core.model import RawRequest


class Action(object):
    _types = {}

    def __init__(self, d=None) -> None:
        self.value: Dict[str, Any] = {}
        self.tag: Optional[str] = None
        self.option: Optional[str] = None
        self.timezone: Optional[str] = None
        init(self, d, self._types)


# 互动卡片回调
class Card(object):
    _types = {
        "action": Action
    }

    def __init__(self, d=None) -> None:
        self.app_id: Optional[str] = None
        self.open_id: Optional[str] = None
        self.user_id: Optional[str] = None
        self.tenant_key: Optional[str] = None
        self.open_message_id: Optional[str] = None
        self.open_chat_id: Optional[str] = None
        self.token: Optional[str] = None
        self.challenge: Optional[str] = None
        self.type: Optional[str] = None
        self.action: Optional[Action] = None
        self.raw: Optional[RawRequest] = None
        init(self, d, self._types)


# APP缓存
class AppCache(object):
    _types = {}

    def __init__(self, d=None) -> None:
        self.open_id: Optional[str] = None
        self.appid: Optional[str] = None
        self.app_secret: Optional[str] = None
        self.app_role_type: Optional[float] = 0
        self.verification_token: Optional[str] = None
        self.encrypt_key: Optional[str] = None
        self.robot_appid: Optional[str] = None
        self.robot_api_secret: Optional[str] = None
        self.robot_api_key: Optional[str] = None
        self.robot_domain: Optional[str] = None
        self.robot_spark_url: Optional[str] = None
        self.robot_temperature: Optional[float] = 0.5
        init(self, d, self._types)

    @staticmethod
    def builder() -> "AppCacheBuilder":
        return AppCacheBuilder()

    def to_dict(self):
        return {
            'open_id': self.open_id,
            'appid': self.appid,
            'app_secret': self.app_secret,
            'app_role_type': self.app_role_type,
            'verification_token': self.verification_token,
            'encrypt_key': self.encrypt_key,
            'robot_appid': self.robot_appid,
            'robot_api_secret': self.robot_api_secret,
            'robot_api_key': self.robot_api_key,
            'robot_domain': self.robot_domain,
            'robot_spark_url': self.robot_spark_url,
            'robot_temperature': self.robot_temperature,
        }


class AppCacheBuilder(object):
    def __init__(self) -> None:
        self._app_cache = AppCache()

    def open_id(self, open_id: str) -> "AppCacheBuilder":
        self._app_cache.open_id = open_id
        return self

    def appid(self, appid: str) -> "AppCacheBuilder":
        self._app_cache.appid = appid
        return self

    def app_secret(self, app_secret: str) -> "AppCacheBuilder":
        self._app_cache.app_secret = app_secret
        return self

    def app_role_type(self, app_role_type: float) -> "AppCacheBuilder":
        self._app_cache.app_role_type = app_role_type
        return self

    def verification_token(self, verification_token: str) -> "AppCacheBuilder":
        self._app_cache.verification_token = verification_token
        return self

    def encrypt_key(self, encrypt_key: str) -> "AppCacheBuilder":
        self._app_cache.encrypt_key = encrypt_key
        return self

    def robot_appid(self, robot_appid: str) -> "AppCacheBuilder":
        self._app_cache.robot_appid = robot_appid
        return self

    def robot_api_secret(self, robot_api_secret: str) -> "AppCacheBuilder":
        self._app_cache.robot_api_secret = robot_api_secret
        return self

    def robot_api_key(self, robot_api_key: str) -> "AppCacheBuilder":
        self._app_cache.robot_api_key = robot_api_key
        return self

    def robot_domain(self, robot_domain: str) -> "AppCacheBuilder":
        self._app_cache.robot_domain = robot_domain
        return self

    def robot_spark_url(self, robot_spark_url: str) -> "AppCacheBuilder":
        self._app_cache.robot_spark_url = robot_spark_url
        return self

    def robot_temperature(self, robot_temperature: float) -> "AppCacheBuilder":
        self._app_cache.robot_temperature = robot_temperature
        return self

    def build(self) -> "AppCache":
        return self._app_cache
