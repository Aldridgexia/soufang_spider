# -*- coding:utf-8 -*-
import requests
import urllib2
from urllib import urlencode
import numpy as np
import pandas as pd
from pandas import DataFrame
import bs4
from bs4 import BeautifulSoup as BS 
import time
import gzip
from StringIO import StringIO
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import *

headers = {
    "User-Agent":'',
    "accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "accept-encoding":"gzip, deflate, sdch",
    "accept-language":"zh-CN,zh;q=0.8,en;q=0.6",
    "referer":"https://www.quantnet.com/tracker/",
    "upgrade-insecure-requests":"1",
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

url_base = 'http://esf.hz.fang.com/house/'
query_param = {'c61-kw':''}
url_list = []
for xiaoqu in xiaoqu_list:
    xiaoqu = xiaoqu.encode('GB2312')
    query_param['c61-kw'] = xiaoqu
    url_whole = url_base + urlencode(query_param) + '/'
    url_list.append(url_whole)    


def get_target_link(url):
    s = requests.session()
    res = s.get(url, headers=headers, verify=False)
    soup = BS(res.text, 'lxml')
    print 'search page connect successfully!'
    target_link = ''
    try:
        target_link = soup.find('a',{'class':'iconXQ ml10'})['href']
    except TypeError:
        target_link = ''
        print 'cannot find target link!'
    # print target_link['href']
    if target_link:
        print 'successfully get the target link!'
        return target_link
    else:
        print 'cannot find the target link!'
    time.sleep(np.random.randint(1, 3))

# get_page(url_list[0])
url_list = map(get_target_link, url_list)
print url_list


def get_trans_info(url):
    s = requests.session()
    res1 = s.get(url, headers=headers, verify=False)
    soup1 = BS(res1.text, 'lxml')
    info_url = soup1.find('iframe')['src']
    driver = webdriver.PhantomJS(executable_path='/Users/Aldridge/phantomjs-2.1.1-macosx/bin/phantomjs')
    driver.get(info_url)
    jiejing = driver.find_element_by_id('b1')
    time.sleep(1.5)
    jiejing.click()
    # trans_info_block_elem = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_id('btnBus'))
    # trans_info_block_elem.click()
    soup2 = BS(driver.page_source, 'lxml')
    # res2 = s.get(info_url, headers=headers, verify=False)
    # soup2 = BS(res2.text, 'lxml')
    div_bus = soup2.find('div', {'id':'divbus'})
    print div_bus
