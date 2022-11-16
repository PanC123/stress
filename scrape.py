import requests
import re
from bs4 import BeautifulSoup, SoupStrainer
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains


url = "http://127.0.0.1:5500"
page = requests.get(url).text
pageSoup = BeautifulSoup(page, "lxml")
for link in pageSoup.find_all("a",attrs={'class': "icon icon-directory","title": re.compile(r'm')}):
    sub_url = url + link.get('href')
    print(sub_url)
    # 创建配置对象
    #options = webdriver.ChromeOptions()
    # 配置对象添加开启无界面模式的命令
    #options.add_argument('--headless')
    # 配置对象添加禁用gpu的命令
    #options.add_argument('--disable-gpu')
    # 实例化带有配置对象的driver对象
    #driver = webdriver.Chrome(options=options)
    driver = webdriver.PhantomJS(executable_path='/Users/pc/Documents/Python/phantomjs/bin/phantomjs')
    url_chronobiology = driver.get(sub_url)
    chronobiology_content = driver.page_source
    chronobiology_soup = BeautifulSoup(chronobiology_content, "lxml")
    table = chronobiology_soup.find_all("tbody", class_="tablesorter-no-sort")

    stress_info = sub_url.split("/")[3].split("_")
    file_size = stress_info[0].split("-")[0]
    # paralles = 10 * int(stress_info[0].split("-")[1])
    scene = stress_info[1]
    finish_time = stress_info[2]

    data_list = []
    data_list.append(file_size)
    data_list.append(scene)
    data_list.append(finish_time)

    for item in table[1].tr: 
        data_list.append(item.get_text())

    print(data_list)
