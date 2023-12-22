import re
from collections import defaultdict

from util.yundaModel import RemarkBoy

# 韵达运单号表达式
yd_orderNo_pattern = (r"((50|53|57|58|68|80|88)([0-9]{11})|((1[0-9]0)|609|209|316|769|779|429)([0-9]{10})|(7746|6666)("
                      r"[0-9]{9})|(32|43|44|45|46|47|48|57|53|66|52)([0-9]{13})|("
                      r"428|312|313|314|315|317|318|319|429|609|209|316|769)([0-9]{12})|(YD)([0-9]{13}|[0-9]{15}))")


# 正则匹配韵达运单号
def matches_orderNo(text):
    # 使用re.compile()编译正则表达式以提高效率
    regex = re.compile(yd_orderNo_pattern)
    # 使用finditer()方法查找所有匹配项
    matches = set()
    for match in regex.finditer(text):
        # 获取匹配项的字符串形式
        match_str = match.group(0)
        # 将匹配项添加到集合中（集合自动去除重复项）
        matches.add(match_str)
    # 判断是否找到任何匹配项
    matchesNo = len(matches)
    has_matches = matchesNo > 0
    return has_matches, matchesNo, list(matches)


# 正则判断是否匹配
def match_expression(content, expression):
    pattern = re.compile(expression)
    return bool(pattern.search(content))


# 分组获取回复内容
def group_by_remark(remark_boy_list: list[RemarkBoy]):
    send_content = []
    remark_dict = defaultdict(list)
    for remark_boy in remark_boy_list:
        remark = remark_boy.remark
        remark_dict[remark].append(remark_boy)

    unique_remarks = list(remark_dict.keys())
    for remark in unique_remarks:
        datums = remark_dict[remark]
        for datum in datums:
            send_content.append(datum.orderNo)
        send_content.append(remark)

    return '\n'.join(send_content)


if __name__ == "__main__":
    text = ("Here are some test numbers: 5012345678901, 5312345678901, 5712345678901, 5812345678901, 6812345678901, "
            "8012345678901, 8812345678901, 100123456789, 60912345678, 20912345678, 31612345678, 76912345678, "
            "77912345678, 42912345678, 77461234567, 66661234567, 321234567890123, 431234567890123, 441234567890123, "
            "451234567890123, 461234567890123, 471234567890123, 481234567890123, 571234567890123, 531234567890123, "
            "661234567890123, 521234567890123, 428123456789012, 312123456789012, 313123456789012, 314123456789012, "
            "315123456789012, 317123456789012, 318123456789012, 319123456789012, 429123456789012, 609123456789012, "
            "209123456789012, 316123456789012, 769123456789012, 463296188359759 YD123456789013, YD123456789015")

    has_matches, matchesNo, matches = matches_orderNo(text)
    if has_matches:
        print("Found matches:" + str(matchesNo))
        for match in matches:
            print(match)
    else:
        print("No matches found.")
