import json
from typing import *

from lark_oapi.core.construct import init


class WinCard(object):
    _types = {
        "card": str,
        "mate": bool,
        "continue_processing": bool,
    }

    def __init__(self, d=None):
        self.card: Optional[str] = None
        self.mate: Optional[bool] = False
        self.continue_processing: Optional[bool] = True
        init(self, d, self._types)

    @staticmethod
    def builder() -> "WinCardBuilder":
        return WinCardBuilder()

    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.dict, ensure_ascii=False)


class WinCardBuilder(object):
    def __init__(self) -> None:
        self._win_card = WinCard()

    def card(self, card: str) -> "WinCardBuilder":
        self._win_card.card = card
        return self

    def mate(self, mate: bool) -> "WinCardBuilder":
        self._win_card.mate = mate
        return self

    def continue_processing(self, continue_processing: bool) -> "WinCardBuilder":
        self._win_card.continue_processing = continue_processing
        return self

    def build(self) -> "WinCard":
        return self._win_card
