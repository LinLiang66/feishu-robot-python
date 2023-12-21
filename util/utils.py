from lark_oapi import logger

from util.yundaModel import HttpResponse
from util.yundaApi import query_bar_code_record


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


if __name__ == "__main__":
    response: HttpResponse = query_bar_code_record("433624511290817")

    print(response.to_dict())
    if response.success:
        print(response.result.mailNo)

    else:
        logger.error(f"method:query_bar_code_record , "
                     f"code: {response.code}, "
                     f"success: {response.success}, "
                     f"message: {response.message}")
