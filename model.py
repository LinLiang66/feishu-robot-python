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


class AppCache(object):
    _types = {}

    def __init__(self, d=None) -> None:
        self.appid: Optional[str] = None
        self.app_secret: Optional[str] = None
        self.verification_token: Optional[str] = None
        self.encrypt_key: Optional[str] = None
        self.robot_appid: Optional[str] = None
        self.robot_api_secret: Optional[str] = None
        self.robot_api_key: Optional[str] = None
        self.robot_domain: Optional[str] = None
        self.robot_spark_url: Optional[str] = None
        self.robot_temperature: Optional[float] = 0.5

        init(self, d, self._types)
