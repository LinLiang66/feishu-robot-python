from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from jinja2 import Environment, FileSystemLoader

if __name__ == "__main__":
    # 加载 FTL 模板
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('templates/tmp.ftl')

    # 渲染模板
    rendered_template = template.render(no="12345", list=[
        {
            "scanTm": "2022-01-01 10:00:00",
            "scanType": "类型A",
            "trackRecord": "这是一条跟踪记录",
            "grpshipid": "大包号1",
            "frgtWgt": "10",
            "frgtVolWgt": "20"
        },
        {
            "scanTm": "2022-01-01 11:00:00",
            "scanType": "类型B",
            "trackRecord": "这是另一条跟踪记录",
            "grpshipid": "大包号2",
            "frgtWgt": "15",
            "frgtVolWgt": "25"
        }
    ])

    # 创建一个新的图片对象
    image = Image.new('RGB', (900, 600), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)

    # 设置字体和大小
    font = ImageFont.truetype('arial.ttf', size=20)

    # 在图片上绘制文本
    x, y = 10, 10
    for line in rendered_template.split('\n'):
        draw.text((x, y), line, font=font, fill=(0, 0, 0))
        y += 20
    # 保存图片
    image.save("E:\\桌面\\66777.jpg")
