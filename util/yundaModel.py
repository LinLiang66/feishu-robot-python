
from typing import *

from lark_oapi import init


# Http请求回参
class HttpResponse(object):
    _types = {}

    def __init__(self, d=None) -> None:
        self.success: Optional[bool] = None
        self.message: Optional[str] = None
        self.code: Optional[int] = None
        self.timestamp: Optional[int] = None
        self.result: Optional[object] = None
        init(self, d, self._types)

    def to_dict(self):
        return {
            'success': self.success,
            'message': self.message,
            'code': self.code,
            'timestamp': self.timestamp,
            'result': self.result,
        }


# 上传图片返回信息
class ImageMessage(object):
    _types = {}

    def __init__(self, d=None) -> None:
        self.fileName: Optional[str] = None
        self.filePath: Optional[str] = None
        self.newFileName: Optional[str] = None
        self.visitPath: Optional[str] = None
        self.xieTongFilePath: Optional[str] = None
        init(self, d, self._types)

    def to_dict(self):
        return {
            'fileName': self.fileName,
            'filePath': self.filePath,
            'newFileName': self.newFileName,
            'visitPath': self.visitPath,
            'xieTongFilePath': self.xieTongFilePath,
        }


# 条码分配信息
class BarCodeMessage(object):
    _types = {}

    def __init__(self, d=None) -> None:
        self.mailNo: Optional[str] = None
        self.customerID: Optional[str] = None
        self.oneTierBranchCode: Optional[str] = None
        self.twoTierBranchCode: Optional[str] = None
        self.twoTierCodeName: Optional[str] = None
        self.twoTierCodeBranchCode: Optional[str] = None
        self.customerName: Optional[str] = None
        self.oneTierBranchName: Optional[str] = None
        self.twoTierBranchName: Optional[str] = None
        init(self, d, self._types)

    def to_dict(self):
        return {
            'mailNo': self.mailNo,
            'customerID': self.customerID,
            'oneTierBranchCode': self.oneTierBranchCode,
            'twoTierBranchCode': self.twoTierBranchCode,
            'twoTierCodeName': self.twoTierCodeName,
            'twoTierCodeBranchCode': self.twoTierCodeBranchCode,
            'customerName': self.customerName,
            'oneTierBranchName': self.oneTierBranchName,
            'twoTierBranchName': self.twoTierBranchName,
        }


# 留言实体
class ServiceMessage(object):
    _types = {}

    def __init__(self, d=None):
        self.jgReceiveSite: Optional[str] = None
        self.jgPublishSite: Optional[str] = None
        self.newReceiverAddress: Optional[str] = None
        self.newReceiverPhone: Optional[str] = None
        self.newReceiverName: Optional[str] = None
        self.visitPath: Optional[str] = None
        self.fileName: Optional[str] = None
        self.filePath: Optional[str] = None
        self.xieTongFilePath: Optional[str] = None
        self.goodsName: Optional[str] = None
        self.goodsValue: Optional[str] = None
        self.processorId: Optional[str] = None
        self.outNo: Optional[str] = None
        self.createMobile: Optional[str] = None
        self.createBy: Optional[str] = None
        self.createId: Optional[str] = None
        self.problemContent: Optional[str] = None
        self.workExpressType: Optional[str] = None
        self.orderNo: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "ServiceMessageBuilder":
        return ServiceMessageBuilder()

    def to_dict(self):
        return {
            'orderNo': self.orderNo,
            'workExpressType': self.workExpressType,
            'problemContent': self.problemContent,
            'createId': self.createId,
            'createBy': self.createBy,
            'createMobile': self.createMobile,
            'outNo': self.outNo,
            'processorId': self.processorId,
            'goodsValue': self.goodsValue,
            'goodsName': self.goodsName,
            'xieTongFilePath': self.xieTongFilePath,
            'filePath': self.filePath,
            'fileName': self.fileName,
            'visitPath': self.visitPath,
            'newReceiverName': self.newReceiverName,
            'newReceiverPhone': self.newReceiverPhone,
            'newReceiverAddress': self.newReceiverAddress,
            'jgPublishSite': self.jgPublishSite,
            'jgReceiveSite': self.jgReceiveSite,
        }


class ServiceMessageBuilder(object):
    def __init__(self) -> None:
        self._service_message = ServiceMessage()

    def orderNo(self, orderNo: str) -> "ServiceMessageBuilder":
        self._service_message.orderNo = orderNo
        return self

    def workExpressType(self, workExpressType: str) -> "ServiceMessageBuilder":
        self._service_message.workExpressType = workExpressType
        return self

    def problemContent(self, problemContent: str) -> "ServiceMessageBuilder":
        self._service_message.problemContent = problemContent
        return self

    def createId(self, createId: str) -> "ServiceMessageBuilder":
        self._service_message.createId = createId
        return self

    def createBy(self, createBy: str) -> "ServiceMessageBuilder":
        self._service_message.createBy = createBy
        return self

    def createMobile(self, createMobile: str) -> "ServiceMessageBuilder":
        self._service_message.createMobile = createMobile
        return self

    def outNo(self, outNo: str) -> "ServiceMessageBuilder":
        self._service_message.outNo = outNo
        return self

    def processorId(self, processorId: str) -> "ServiceMessageBuilder":
        self._service_message.processorId = processorId
        return self

    def goodsValue(self, goodsValue: str) -> "ServiceMessageBuilder":
        self._service_message.goodsValue = goodsValue
        return self

    def goodsName(self, goodsName: str) -> "ServiceMessageBuilder":
        self._service_message.goodsName = goodsName
        return self

    def xieTongFilePath(self, xieTongFilePath: str) -> "ServiceMessageBuilder":
        self._service_message.xieTongFilePath = xieTongFilePath
        return self

    def filePath(self, filePath: str) -> "ServiceMessageBuilder":
        self._service_message.filePath = filePath
        return self

    def fileName(self, fileName: str) -> "ServiceMessageBuilder":
        self._service_message.fileName = fileName
        return self

    def visitPath(self, visitPath: str) -> "ServiceMessageBuilder":
        self._service_message.visitPath = visitPath
        return self

    def newReceiverName(self, newReceiverName: str) -> "ServiceMessageBuilder":
        self._service_message.newReceiverName = newReceiverName
        return self

    def newReceiverPhone(self, newReceiverPhone: str) -> "ServiceMessageBuilder":
        self._service_message.newReceiverPhone = newReceiverPhone
        return self

    def newReceiverAddress(self, newReceiverAddress: str) -> "ServiceMessageBuilder":
        self._service_message.newReceiverAddress = newReceiverAddress
        return self

    def jgPublishSite(self, jgPublishSite: str) -> "ServiceMessageBuilder":
        self._service_message.jgPublishSite = jgPublishSite
        return self

    def jgReceiveSite(self, jgReceiveSite: str) -> "ServiceMessageBuilder":
        self._service_message.jgReceiveSite = jgReceiveSite
        return self

    def build(self) -> "ServiceMessage":
        return self._service_message


# 加密请求内容
class EncryptedRequestBoy(object):
    _types = {
        "logisticsInterface": str,
        "partnerCode": str,
    }

    def __init__(self, d=None):
        self.logisticsInterface: Optional[str] = None
        self.partnerCode: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "EncryptedRequestBoyBuilder":
        return EncryptedRequestBoyBuilder()

    def to_dict(self):
        return {
            'logisticsInterface': self.logisticsInterface,
            'partnerCode': self.partnerCode,

        }


class EncryptedRequestBoyBuilder(object):
    def __init__(self) -> None:
        self._encrypted_request_boy = EncryptedRequestBoy()

    def logisticsInterface(self, logisticsInterface: bool) -> "EncryptedRequestBoyBuilder":
        self._encrypted_request_boy.logisticsInterface = logisticsInterface
        return self

    def partnerCode(self, partnerCode: str) -> "EncryptedRequestBoyBuilder":
        self._encrypted_request_boy.partnerCode = partnerCode
        return self

    def build(self) -> "EncryptedRequestBoy":
        return self._encrypted_request_boy
