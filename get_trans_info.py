# -*- coding:utf-8 -*-
import requests
import numpy as np
import pandas as pd
from pandas import DataFrame
from bs4 import BeautifulSoup as BS 
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import *
from selenium.webdriver.common.keys import Keys
import re

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
# driver = webdriver.PhantomJS(executable_path='/Users/Aldridge/phantomjs-2.1.1-macosx/bin/phantomjs')

# 函数主体部分，测试用
def get_trans_info(url):
	# url = 'http://wendingyuanyj.fang.com/xiangqing/'
	url = 'http://jinchenzhiguangwk.fang.com/xiangqing/'
	s = requests.session()
	res1 = s.get(url, headers=headers, verify=False)
	soup1 = BS(res1.text, 'lxml')
	info_url = soup1.find('iframe')['src']
	# print info_url
	driver = webdriver.PhantomJS(executable_path='/Users/Aldridge/phantomjs-2.1.1-macosx/bin/phantomjs')
	driver.get(info_url)
	ditu_elem = WebDriverWait(driver, 5).until(lambda driver: driver.find_element_by_id('b2'))
	time.sleep(8)
	ditu_elem.click()
	# divbus_elem = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_id('divbus'))
	# divbus_elem.send_keys(Keys.TAB)
	# divbus_elem.click()
	driver.execute_script("document.getElementById('divbus').style.display='block';")
	WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_tag_name('tbody'))
	# time.sleep(4)
	soup2 = BS(driver.page_source, 'lxml')
	div_bus = soup2.find('div', {'id':'divbus'})
	# print 'successfully find div_bus!'
	print div_bus

	# 存储站台和距离信息的容器
	trans_info_df = DataFrame(columns=['line_num', 'distance'], index=[0])
	temp_dict = {'line_num':'', 'distance':''}
	tr_num = 0
	for tr in div_bus.table.tbody:
		# print tr
		temp_dict['line_num'] = tr.th.text
		temp_dict['distance'] = tr.td.text
		have_metro = False
		print temp_dict
		match_distance = re.findall(r'\d+', temp_dict['distance'])
		pattern = re.compile(u'【地铁】')
		match_metro = re.search(pattern, temp_dict['line_num'])
		if match_metro and (int(match_distance[0]) <= 1000):
			have_metro = True
			print 'have metro!'
		print match_distance[0]
		if int(match_distance[0]) <= 500:
			print 'got one!'
			match_line = re.findall(r'\d+', temp_dict['line_num'])
			# print len(set(match_line))
			temp_dict['line_num'] = len(set(match_line))
			print temp_dict
			trans_info_df.ix[tr_num] = temp_dict
			tr_num += 1
		else:
			print 'not this one!'
			pass

	bus_station_num = len(trans_info_df)
	bus_line_num = trans_info_df['line_num'].sum()
	print trans_info_df
	print bus_station_num
	print bus_line_num
	print have_metro

get_trans_info('http://jinchenzhiguangwk.fang.com/xiangqing/')
