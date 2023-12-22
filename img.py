import json

import matplotlib.pyplot as plt
import pandas as pd
from jinja2 import Template

# JSON数据
json_data = '''
[
    {"name": "蔺亮", "age": 20, "score": 90},
    {"name": "李四", "age": 22, "score": 85},
    {"name": "王五", "age": 24, "score": 88}
]
'''

# FTL模板
ftl_template = '''
<table>
    <thead>
        <tr>
            <th style="background-color: {{ header_color }};">姓名</th>
            <th style="background-color: {{ header_color }};">年龄</th>
            <th style="background-color: {{ header_color }};">分数</th>
        </tr>
    </thead>
    <tbody>
        {% for row in data %}
        <tr>
            <td>{{ row.name }}</td>
            <td>{{ row.age }}</td>
            <td>{{ row.score }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
'''

# 使用pandas读取JSON数据
data = json.loads(json_data)
df = pd.DataFrame(data)

# 使用jinja2渲染FTL模板
template = Template(ftl_template)
rendered_html = template.render(data=df.to_dict(orient='records'), header_color='yellow')

# 使用matplotlib绘制表格并保存为图片
fig, ax = plt.subplots()
ax.axis('off')
ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')
plt.savefig('table.png')

# 显示图片（可选）
img = plt.imread('table.png')
plt.imshow(img)
plt.show()
