import lark_oapi as lark


# 构建模型切换卡片
def model_select_card_build() -> str:
    card = {
        "elements": [
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "select_static",
                        "placeholder": {
                            "tag": "plain_text",
                            "content": ""
                        },
                        "value": {
                            "text": "domain_version"
                        },
                        "options": [
                            {
                                "text": {
                                    "tag": "plain_text",
                                    "content": "spark1.5-chat"
                                },
                                "value": "general"
                            },
                            {
                                "text": {
                                    "tag": "plain_text",
                                    "content": "spark2.1-chat"
                                },
                                "value": "generalv2"
                            },
                            {
                                "text": {
                                    "tag": "plain_text",
                                    "content": "spark3.1-chat"
                                },
                                "value": "generalv3"
                            }
                        ],
                        "confirm": {
                            "title": {
                                "tag": "plain_text",
                                "content": "您确定要更改模型吗？"
                            },
                            "text": {
                                "tag": "plain_text",
                                "content": "选择模型可以让AI更好地理解您的需求"
                            }
                        }
                    }
                ]
            },
            {
                "tag": "note",
                "elements": [
                    {
                        "tag": "plain_text",
                        "content": "🤖温馨提示：选择内置模型，让AI更好的理解您的需求。"
                    }
                ]
            }
        ],
        "header": {
            "template": "green",
            "title": {
                "content": "🚀 AI模型切换",
                "tag": "plain_text"
            }
        }
    }
    return lark.JSON.marshal(card)


# 构建发散切换卡片
def diverge_select_card_build() -> str:
    card = {
        "elements": [
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "select_static",
                        "placeholder": {
                            "tag": "plain_text",
                            "content": ""
                        },
                        "value": {
                            "text": "temperature"
                        },
                        "options": [
                            {
                                "text": {
                                    "tag": "plain_text",
                                    "content": "严谨"
                                },
                                "value": "1"
                            },
                            {
                                "text": {
                                    "tag": "plain_text",
                                    "content": "简洁"
                                },
                                "value": "0.75"
                            },
                            {
                                "text": {
                                    "tag": "plain_text",
                                    "content": "标准"
                                },
                                "value": "0.5"
                            },
                            {
                                "text": {
                                    "tag": "plain_text",
                                    "content": "发散"
                                },
                                "value": "0.25"
                            }
                        ],
                        "confirm": {
                            "title": {
                                "tag": "plain_text",
                                "content": "您确定要更改发散模式吗？"
                            },
                            "text": {
                                "tag": "plain_text",
                                "content": "选择内置模式，可以让AI更好地理解您的需求"
                            }
                        }
                    }
                ]
            },
            {
                "tag": "note",
                "elements": [
                    {
                        "tag": "plain_text",
                        "content": "🤖温馨提示：选择内置模型，让AI更好的理解您的需求。"
                    }
                ]
            }
        ],
        "header": {
            "template": "blue",
            "title": {
                "content": "🤖 发散模式选择",
                "tag": "plain_text"
            }
        }
    }
    return lark.JSON.marshal(card)


# 构建清空上下文卡片
def clear_card_build() -> str:
    card = {
        "elements": [
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": "立刻清除"
                        },
                        "type": "danger",
                        "value": {
                            "text": "clear"
                        },
                        "confirm": {
                            "title": {
                                "tag": "plain_text",
                                "content": "您确定要清除对话上下文吗"
                            },
                            "text": {
                                "tag": "plain_text",
                                "content": "请注意，这将开始一个全新的对话，您将无法利用之前话题的历史消息"
                            }
                        }
                    }
                ]
            },
            {
                "tag": "note",
                "elements": [
                    {
                        "tag": "plain_text",
                        "content": "🤖温馨提示：请注意，这将开始一个全新的对话，您将无法利用之前话题的历史信息"
                    }
                ]
            }
        ],
        "header": {
            "template": "indigo",
            "title": {
                "content": "🆑 机器人提醒",
                "tag": "plain_text"
            }
        }
    }
    return lark.JSON.marshal(card)


# 构建help卡片
def help_card_build() -> str:
    card = {
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": "👋 **你好呀，我是一款基于星火认知大模型技术的智能聊天机器人！**\n了解更多玩法技巧，请点击右侧「使用说明」查看👉"
                },
                "extra": {
                    "tag": "button",
                    "text": {
                        "tag": "lark_md",
                        "content": "使用说明"
                    },
                    "type": "primary",
                    "multi_url": {
                        "url": "https://ginvkqq2ftg.feishu.cn/docx/FVEpdmPzZo7KPaxAeKYcxNTEnSb?from=from_copylink",
                        "pc_url": "",
                        "android_url": "",
                        "ios_url": ""
                    }
                }
            },
            {
                "tag": "hr"
            },
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": " 🆑 **清除话题上下文**\n文本回复 清除 或 /clear"
                },
                "extra": {
                    "tag": "button",
                    "text": {
                        "tag": "lark_md",
                        "content": "立刻清除"
                    },
                    "type": "danger",
                    "confirm": {
                        "title": {
                            "tag": "plain_text",
                            "content": "您确定要清除对话上下文吗"
                        },
                        "text": {
                            "tag": "plain_text",
                            "content": "请注意，这将开始一个全新的对话，您将无法利用之前话题的历史消息"
                        }
                    },
                    "value": {
                        "text": "clear"
                    }
                }
            },
            {
                "tag": "hr"
            },
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": "🚀 **AI模型切换**\n文本回复 模型 或 /model"
                },
                "extra": {
                    "tag": "select_static",
                    "placeholder": {
                        "tag": "plain_text",
                        "content": ""
                    },
                    "value": {
                        "text": "domain_version"
                    },
                    "initial_option": "generalv3",
                    "options": [
                        {
                            "text": {
                                "tag": "plain_text",
                                "content": "spark1.5-chat"
                            },
                            "value": "general"
                        },
                        {
                            "text": {
                                "tag": "plain_text",
                                "content": "spark2.1-chat"
                            },
                            "value": "generalv2"
                        },
                        {
                            "text": {
                                "tag": "plain_text",
                                "content": "spark3.1-chat"
                            },
                            "value": "generalv3"
                        }
                    ],
                    "confirm": {
                        "title": {
                            "tag": "plain_text",
                            "content": "您确定要更改模型吗？"
                        },
                        "text": {
                            "tag": "plain_text",
                            "content": "选择模型可以让AI更好地理解您的需求"
                        }
                    }
                }
            },
            {
                "tag": "hr"
            },
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": "🤖 **发散模式选择**\n文本回复 发散模式 或 /ai_mode"
                },
                "extra": {
                    "tag": "select_static",
                    "placeholder": {
                        "tag": "plain_text",
                        "content": ""
                    },
                    "value": {
                        "text": "temperature"
                    },
                    "initial_option": "0.5",
                    "options": [
                        {
                            "text": {
                                "tag": "plain_text",
                                "content": "严谨"
                            },
                            "value": "1"
                        },
                        {
                            "text": {
                                "tag": "plain_text",
                                "content": "简洁"
                            },
                            "value": "0.75"
                        },
                        {
                            "text": {
                                "tag": "plain_text",
                                "content": "标准"
                            },
                            "value": "0.5"
                        },
                        {
                            "text": {
                                "tag": "plain_text",
                                "content": "发散"
                            },
                            "value": "0.25"
                        }
                    ],
                    "confirm": {
                        "title": {
                            "tag": "plain_text",
                            "content": "您确定要更改发散模式吗？"
                        },
                        "text": {
                            "tag": "plain_text",
                            "content": "选择内置模式，可以让AI更好地理解您的需求"
                        }
                    }
                }
            },
            {
                "tag": "hr"
            },
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": "🎒 需要更多帮助\n文本回复 帮助 或 /help"
                },
                "extra": {
                    "tag": "button",
                    "text": {
                        "tag": "lark_md",
                        "content": "意见反馈"
                    },
                    "type": "primary",
                    "multi_url": {
                        "url": "https://ginvkqq2ftg.feishu.cn/share/base/form/shrcnbIwSasRyMXXvCbTyDRr1xX",
                        "android_url": "",
                        "ios_url": "",
                        "pc_url": ""
                    }
                }
            }
        ],
        "header": {
            "template": "blue",
            "title": {
                "content": "🎒需要帮助吗？",
                "tag": "plain_text"
            }
        }
    }
    return lark.JSON.marshal(card)


# 构建通用机器人提醒卡片
def robot_reminder_card_build(header: str, content: str, note: str) -> str:
    card = {
        "elements": [
            {
                "tag": "markdown",
                "content": content
            },
            {
                "tag": "note",
                "elements": [
                    {
                        "tag": "plain_text",
                        "content": "🤖温馨提示✨✨：" + note
                    }
                ]
            }
        ],
        "header": {
            "template": "indigo",
            "title": {
                "content": header,
                "tag": "plain_text"
            }
        }
    }
    return lark.JSON.marshal(card)
