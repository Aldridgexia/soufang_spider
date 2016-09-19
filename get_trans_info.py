# -*- coding:utf-8 -*-
# 获取小区的交通情况

import re
import requests
import time
import numpy as np
import pandas as pd
from pandas import DataFrame
from bs4 import BeautifulSoup as BS
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import *
from from_xiaoqu_name_to_xiangqing_url import xiangqing_url_list, xiaoqu_names
from requests.exceptions import MissingSchema

headers = {
    "User-Agent":'',
    "accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "accept-encoding":"gzip, deflate, sdch",
    "accept-language":"zh-CN,zh;q=0.8,en;q=0.6",
    "upgrade-insecure-requests":"1",
    "connection":"keep-alive",
}
usr_agents = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:22.0) Gecko/20100101 Firefox/22.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0",
]
judge_num = np.random.randint(0,5)
headers["User-Agent"] = usr_agents[judge_num]

driver = webdriver.PhantomJS(executable_path='/Users/Aldridge/phantomjs-2.1.1-macosx/bin/phantomjs')
driver.set_window_size(1124, 850)

# 函数主体部分，测试用
def get_trans_info(url):
    if url == '':
        trans_needed_df = DataFrame(columns=['station_num', 'line_num', 'metro'], index=[0])
        return trans_needed_df
    try:
        res1 = requests.get(url, headers=headers, verify=False)
    except MissingSchema as e:
        print e
        trans_needed_df = DataFrame(columns=['station_num', 'line_num', 'metro'], index=[0])
        return trans_needed_df
    soup1 = BS(res1.text, 'lxml')
    # print soup1.prettify()
    info_url = soup1.find_all('iframe')[1]['src']
    # print info_url
    # driver = webdriver.PhantomJS(executable_path='/Users/Aldridge/phantomjs-2.1.1-macosx/bin/phantomjs')
    driver.get(info_url)
    # 需要模拟光标移动到『地图』元素上方可捕捉div_bus 内容
    ditu_elem = WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_id('b2'))
    hover = ActionChains(driver).move_to_element(ditu_elem)
    hover.perform()
    jiaotong_elem = WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_id('btnBus'))
    jiaotong_elem.click()
    try:
        WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_class_name('tab'))
    except TimeoutException as e:
        print e
        trans_needed_df = DataFrame(columns=['station_num', 'line_num', 'metro'], index=[0])
        return trans_needed_df
    # time.sleep(5)
    soup2 = BS(driver.page_source, 'lxml')
    # print soup2.prettify()
    div_bus = soup2.find('div', {'id':'divbus'})
    # print div_bus

    try:
        station_num = 0
        line_num = 0
        total_line = []
        have_metro = False
        for tr in div_bus.table.tbody:
            # print tr
            line_info = tr.th.text
            dis_info = tr.td.text
            # print temp_dict
            match_distance = re.findall(r'\d+', dis_info)
            pattern = re.compile(u'【地铁】')
            match_metro = re.search(pattern, line_info)
            if (match_metro):
                if(int(match_distance[0]) <= 1000):
                    have_metro = True
                    print 'have metro!'
                    print match_distance[0]
                else:
                    pass
            elif (int(match_distance[0]) <= 500):
                print 'got one bus line!'
                match_line = re.findall(r'\d+', line_info)
                # print len(set(match_line))
                # line_num += len(set(match_line))
                total_line += match_line
                station_num += 1
            else:
                print 'not this one!'
                pass
        line_num = len(set(total_line))
    except AttributeError:
        print 'fail to find trans info!'
        print info_url

    trans_info_df = DataFrame(columns=['station_num', 'line_num', 'metro'])
    trans_info_df['station_num'] = [station_num]
    trans_info_df['line_num'] = [line_num]
    trans_info_df['metro'] = [have_metro]
    print trans_info_df
    return trans_info_df

# get_trans_info('http://jinchenzhiguangwk.fang.com/xiangqing/')
# get_trans_info('http://wendingyuanyj.fang.com/xiangqing/')

trans_info_total_df = reduce(lambda x,y: pd.concat([x,y],axis=0), map(get_trans_info, xiangqing_url_list))
print trans_info_total_df
