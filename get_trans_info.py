# -*- coding:utf-8 -*-
import requests
import numpy as np
import pandas as pd
from pandas import DataFrame
from bs4 import BeautifulSoup as BS 
import time
from urllib import urlencode
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
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

'''
xiaoqu_names = pd.read_csv('enhanced_total_result.csv', usecols=[2])
xiaoqu_names = xiaoqu_names['community_name'].unique()
xiaoqu_names = xiaoqu_names.tolist()
# print len(xiaoqu_names)

url_base = 'http://esf.hz.fang.com/house/'
query_param = {'c61-kw':''}
url_list = []
for name in xiaoqu_names:
	# print name
	try:
		name = name.decode('utf-8')
		name = name.encode('GB2312')
		query_param['c61-kw'] = name
		url_total = url_base + urlencode(query_param) + '/'
		url_list.append(url_total)
	except AttributeError as e:
		# url_list.append('')
		print name
# print url_list


def get_target_link(url):
    s = requests.session()
    res = s.get(url, headers=headers, verify=False)
    soup = BS(res.text, 'lxml')
    # print 'search page connect successfully!'
    target_link = ''
    try:
        target_link = soup.find('a',{'class':'blueword'})['href']
        print target_link
        if target_link[-4:] == 'com/':
        	target_link = target_link + 'xiangqing/'
        elif target_link[-4:] == 'esf/':
        	target_link = target_link[:-4] + 'xiangqing/'
        else:
        	target_link = target_link[:-6] + 'xiangqing/'
        print 'successfully get the target link!'
        return target_link
    except TypeError as e:
    	print e
        target_link = ''
        print 'cannot find target link!'
    time.sleep(np.random.randint(1, 3))

# 将url_list 中的小区搜索页链接转化成小区主页链接
url_list = map(get_target_link, url_list)
print url_list
'''

# 函数主体部分，测试用
def get_trans_info(url):
	s = requests.session()
	res1 = s.get(url, headers=headers, verify=False)
	soup1 = BS(res1.text, 'lxml')
	info_url = soup1.find('iframe')['src']
	# print info_url
	driver = webdriver.PhantomJS(executable_path='/Users/Aldridge/phantomjs-2.1.1-macosx/bin/phantomjs')
	driver.get(info_url)
	# 需要模拟光标移动到『地图』元素上方可捕捉div_bus 内容
	ditu_elem = WebDriverWait(driver, 15).until(lambda driver: driver.find_element_by_id('b2'))
	hover = ActionChains(driver).move_to_element(ditu_elem)
	hover.perform()
	soup2 = BS(driver.page_source, 'lxml')
	div_bus = soup2.find('div', {'id':'divbus'})
	# print div_bus

	# 存储站台和距离信息的容器
	trans_info_df = DataFrame(columns=['line_num', 'distance'], index=[0])
	temp_dict = {'line_num':'', 'distance':''}
	tr_num = 0
	try:
		have_metro = False
		for tr in div_bus.table.tbody:
			# print tr
			temp_dict['line_num'] = tr.th.text
			temp_dict['distance'] = tr.td.text
			# print temp_dict
			match_distance = re.findall(r'\d+', temp_dict['distance'])
			pattern = re.compile(u'【地铁】')
			match_metro = re.search(pattern, temp_dict['line_num'])
			if match_metro and (int(match_distance[0]) <= 1000):
				have_metro = True
				print 'have metro!'
				print match_distance[0]
			elif (int(match_distance[0]) <= 500):
				print 'got one!'
				match_line = re.findall(r'\d+', temp_dict['line_num'])
				# print len(set(match_line))
				temp_dict['line_num'] = len(set(match_line))
				# print temp_dict
				trans_info_df.ix[tr_num] = temp_dict
				tr_num += 1
			else:
				print 'not this one!'
				pass
	except AttributeError:
		print 'fail to find trans info!'
		print info_url

	bus_station_num = len(trans_info_df)
	bus_line_num = trans_info_df['line_num'].sum()
	# print trans_info_df
	# print bus_station_num
	# print bus_line_num
	# print have_metro
	trans_needed_df = DataFrame(columns=['station_num', 'line_num', 'metro'], index=[0])
	trans_needed_df['station_num'][0] = bus_station_num
	trans_needed_df['line_num'][0] = bus_line_num
	trans_needed_df['metro'] = have_metro
	print trans_needed_df
	return trans_needed_df

# get_trans_info('http://jinchenzhiguangwk.fang.com/xiangqing/')
# get_trans_info('http://wendingyuanyj.fang.com/xiangqing/')

trans_info_total_df = reduce(lambda x,y: pd.concat([x,y],axis=0), map(get_trans_info, url_list))
print trans_info_total_df
