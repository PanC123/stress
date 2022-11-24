import requests
import copy
import json
import re
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
"""
场景：上传，下载，混合压测后自动爬取数据并整理成报表所需的格式

自动生成图表限制：
1. 如果有重复的测试数据，需要删掉只保留一个报告
2. 每种类型都必须得有测试报告
"""

url = "http://127.0.0.1:5500/" # Jmeter报告访问根地址，结尾需要带斜杠
page = requests.get(url).text
pageSoup = BeautifulSoup(page, "lxml")

data_dict = {}
for link in pageSoup.find_all("a", attrs={"href": re.compile(r'm')}):
    sub_url = url + link.get('href')
    # 创建配置对象
    #options = webdriver.ChromeOptions()
    # 配置对象添加开启无界面模式的命令
    #options.add_argument('--headless')
    # 配置对象添加禁用gpu的命令
    #options.add_argument('--disable-gpu')
    # 实例化带有配置对象的driver对象
    #driver = webdriver.Chrome(options=options)
    driver = webdriver.PhantomJS(
        executable_path='/Users/pc/Documents/Python/phantomjs/bin/phantomjs',service_log_path=os.path.devnull)
    url_reponse = driver.get(sub_url)
    response_content = driver.page_source
    response_soup = BeautifulSoup(response_content, "lxml")
    table = response_soup.find_all("tbody", class_="tablesorter-no-sort")

    stress_info = sub_url.split("/")[3].split("_")
    file_size = stress_info[0].split("-")[0]
    # paralles = 10 * int(stress_info[0].split("-")[1])
    scene = stress_info[1]
    finish_time = stress_info[2]
    data_list = []
    for item in table[1].tr:
        data_list.append(item.get_text())
    data_list.append(file_size)
    data_list.append(scene)
    data_list.append(finish_time)
    print(str(data_list).lstrip('[').rstrip(']').replace('\'', ''))
    if file_size not in data_dict:
        data_dict[file_size] = {
            "xAxis": [],
            "upload_traffic": [],
            "download_traffic": [],
            "mix_traffic": [],
            "error_pct": [],
            "upload_rsp": [],
            "download_rsp": [],
            "mix_rsp": [],
            "upload_tps": [],
            "download_tps": [],
            "mix_tps": []
        }
    if data_list[1] not in data_dict[file_size]['xAxis']:
        data_dict[file_size]['xAxis'].append(data_list[1])
    if scene == "upload":
        data_dict[file_size]['upload_traffic'].append(
            round(float(data_list[12]) + float(data_list[13]), 1))
        data_dict[file_size]['upload_rsp'].append(data_list[4])
        data_dict[file_size]['upload_tps'].append(data_list[11])
        data_dict[file_size]['error_pct'].append(data_list[3].rstrip('%'))
    if scene == "download":
        data_dict[file_size]['download_traffic'].append(
            round(float(data_list[12]) + float(data_list[13]), 1))
        data_dict[file_size]['download_rsp'].append(data_list[4])
        data_dict[file_size]['download_tps'].append(data_list[11])

    if scene == "mix37":
        data_dict[file_size]['mix_traffic'].append(
            round(float(data_list[12]) + float(data_list[13]), 1))
        data_dict[file_size]['mix_rsp'].append(data_list[4])
        data_dict[file_size]['mix_tps'].append(data_list[11])

# 联动排序横坐标
data_dict[file_size]['xAxis'], data_dict[file_size]['error_pct'], data_dict[
    file_size]['upload_traffic'], data_dict[file_size][
        'upload_rsp'], data_dict[file_size]['upload_tps'], data_dict[
            file_size]['download_traffic'], data_dict[file_size][
                'download_rsp'], data_dict[file_size][
                    'download_tps'], data_dict[file_size][
                        'mix_traffic'], data_dict[file_size][
                            'mix_rsp'], data_dict[file_size]['mix_tps'] = (
                                list(t) for t in zip(*sorted(
                                    zip(
                                        data_dict[file_size]['xAxis'],
                                        data_dict[file_size]['error_pct'],
                                        data_dict[file_size]['upload_traffic'],
                                        data_dict[file_size]['upload_rsp'],
                                        data_dict[file_size]['upload_tps'],
                                        data_dict[file_size]
                                        ['download_traffic'],
                                        data_dict[file_size]['download_rsp'],
                                        data_dict[file_size]['download_tps'],
                                        data_dict[file_size]['mix_traffic'],
                                        data_dict[file_size]['mix_rsp'],
                                        data_dict[file_size]['mix_tps']))))

# 生成chart数据
chart_traffic = {
    "title": {"x": 'center',"y": '5px',"textAlign": 'left'},
    "xAxis": [
        {
            "type": "category",
            "axisPointer": {
                "type": "shadow",
            },
        },
    ],
    "type": "traffic",
    "series": [
        {
            "name": "上传",
            "type": "bar",
        },
        {
            "name": "下载",
            "type": "bar",
        },
        {
            "name": "混合",
            "type": "bar",
        },
        {
            "name": "错误率",
            "type": "line",
            "yAxisIndex": 1,
        },
    ]
}
chart_transaction={
        "title": {"x": 'center',"y": '5px',"textAlign": 'left'},
        "xAxis": [
          {
            
            "type": "category",
            "axisPointer": {"type": "shadow",},
          },
        ],
        "type": "transaction",
        "series": [
          {
            "name": "上传响应时间",
            "type": "bar",
          },
          {
            "name": "下载响应时间",
            "type": "bar",
          },
          {
            "name": "混合响应时间",
            "type": "bar",
          },
          {
            "name": "上传TPS",
            "type": "line",
            "yAxisIndex": 1,
          },
          {
            "name": "下载TPS",
            "type": "line",
            "yAxisIndex": 1,
          },
          {
            "name": "混合TPS",
            "type": "line",
            "yAxisIndex": 1,
          },
        ],
      }

echart_list = []
for file_size in data_dict:
    chart_traffic['title']['text'] = file_size + "文件-传输速率和错误率"
    chart_traffic['size'] = file_size
    chart_traffic['xAxis'][0]['data'] = data_dict[file_size]['xAxis']
    chart_traffic['series'][0]['data'] = data_dict[file_size]['upload_traffic']
    chart_traffic['series'][1]['data'] = data_dict[file_size]['download_traffic']
    chart_traffic['series'][2]['data'] = data_dict[file_size]['mix_traffic']
    chart_traffic['series'][3]['data'] = data_dict[file_size]['error_pct']

    chart_transaction['title']['text'] = file_size + "文件-响应时间和TPS"
    chart_transaction['size'] = file_size
    chart_transaction['xAxis'][0]['data'] = data_dict[file_size]['xAxis']
    chart_transaction['series'][0]['data'] = data_dict[file_size]['upload_rsp']
    chart_transaction['series'][1]['data'] = data_dict[file_size]['download_rsp']
    chart_transaction['series'][2]['data'] = data_dict[file_size]['mix_rsp']
    chart_transaction['series'][3]['data'] = data_dict[file_size]['upload_tps']
    chart_transaction['series'][4]['data'] = data_dict[file_size]['download_tps']
    chart_transaction['series'][5]['data'] = data_dict[file_size]['mix_tps']

    chart_traffic1 = copy.deepcopy(chart_traffic)
    chart_transaction1 = copy.deepcopy(chart_transaction)
    echart_list.append(chart_traffic1)
    echart_list.append(chart_transaction1)

# 按文件大小和类型排序图表
echart_list1 = sorted(echart_list, key = lambda i: (i['size'].rstrip('m'), i['type']))
## print(json.dumps(sorted(echart_list, key = lambda i: (i['size'].rstrip('m'), i['type'])), ensure_ascii=False))
fo = open("data.json", "w")

fo.write(json.dumps(echart_list1, ensure_ascii=False))
