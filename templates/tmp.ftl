<html lang="cn">
<head>
    <meta charset="utf-8">
    <style>
        body, html {
            height: 100%;
            width: 100%;
            min-height: 500px;
            min-width: 1000px;
            margin: 0;
            padding: 0
        }

        body {
            position: relative;
            font-family: "Helvetica Neue", Helvetica, Arial, "Times New Roman", "Microsoft YaHei", "Hiragino Sans GB", "Heiti SC", "WenQuanYi Micro Hei", sans-serif
        }

        ::-webkit-scrollbar {
            width: 10px;
            height: 4px
        }

        ::-webkit-scrollbar-thumb {
            background: rgba(0, 0, 0, 0.4)
        }

        ::-webkit-scrollbar-thumb:hover {
            background: rgba(0, 0, 0, 0.8)
        }

        .v-align-container > * {
            position: absolute;
            top: 50%;
            transform: translateY(-50%)
        }

        .h-align-container > * {
            position: absolute;
            left: 50%;
            transform: translateX(-50%)
        }

        .both-align-container > * {
            position: absolute;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%)
        }

        .inputs > textarea {
            width: 100%;
            min-height: 100%;
            outline: 0;
            line-height: 25px;
            font-size: 20px;
            background: rgba(0, 0, 0, 0);
            border: 0;
            padding: 0 10px;
            overflow: hidden;
            margin: 0;
            box-sizing: border-box;
            resize: none;
            display: block
        }

        table {
            border-collapse: collapse;
            width: 100%;
            color: #333
        }

        table, th, td {
            border: 2px solid #ededed
        }

        th {
            background-color: #f2f2f2;
            font-weight: bold;
            font-size: 15px
        }

        td {
            font-size: 13px
        }

        th, td {
            vertical-align: middle;
            padding: 4px 6px;
            border: 1px solid #ededed
        }

        tbody > tr:nth-child(odd) {
            background-color: #fff
        }


        .center {
            text-align: center;
        }

    </style>
</head>

<body>
<div>
    <div style="width: 900px">
        <div>
            <span style="font-size: 20px;">跟踪记录:  </span>
            <span style="font-size: 20px; color: #4849AF">${no!""}</span>
        </div>
        <table style="margin: 8px" width='100%'>
            <tr>
                <th width="12%">扫描时间</th>
                <th WIDTH="10%">扫描类型</th>
                <th WIDTH="58%">跟踪记录</th>
                <th WIDTH="10%">大包号</th>
                <th WIDTH="10%">称重重量(千克)</th>
                <th WIDTH="10%">计泡重量(千克)</th>
            </tr>
            <#list list as item>
                <tr>
                    <td>${item.scanTm!""}</td>
                    <td>${item.scanType!""}</td>
                    <td>${item.trackRecord!""}</td>
                    <td class="center">${item.grpshipid!""}</td>
                    <td class="center">${item.frgtWgt!""}</td>
                    <td class="center">${item.frgtVolWgt!""}</td>
                </tr>
            </#list>
        </table>

    </div>
</div>
</body>
</html>
