# -*- coding:utf-8 -*-
import requests
import numpy as np
import pandas as pd 
from pandas import DataFrame 
from urlparse import urlsplit
from bs4 import BeautifulSoup as BS 
import re
import time
from get_school_deal_link import school_deal_link_dict, school_deal_link_df

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

time_start = time.time()

# 存放全部爬取内容的DataFrame
df_all = DataFrame({
	'community_name':'', 
	u'floor_area(㎡)':'', 
	'unit':'', 
	u'avg_price(元/㎡)':'', 
	u'total_price(万/套)':'', 
	'turnover_time':'',
	'district': '',
	'school_name': ''}, index=[])

for base_url in school_deal_link_dict.values():
	# 获取交易所属城区和学校
	district = None
	school_name = None
	district = school_deal_link_df[school_deal_link_df['deal_link'] == base_url]['district']
	district = district.to_dict().values()[0]
	school_name = school_deal_link_df[school_deal_link_df['deal_link'] == base_url]['school_name']
	school_name = school_name.to_dict().values()[0]
	try:
		# base_url = 'http://esf.hz.fang.com/school/4106/deal/#deal'
		base_session = requests.session()
		base_res = base_session.get(base_url,headers=headers, verify=False)
		base_soup = BS(base_res.text, 'lxml')
		print(base_url + ' connect successfully!')
		try:
			total_page = base_soup.find('div',{'class':'fanye gray6 mt20'}).find('span',{'class':'txt'}).get_text()
			total_page = re.findall(r'(\w*[0-9]+)\w*', total_page)
			total_page = total_page[0]
			# print type(total_page[0])
			url_base = base_url[:-5]
			f = lambda x: url_base + str(x)
			pages = [f(x) for x in range(1, int(total_page) + 1)]
			# print pages
		except AttributeError:
			pages = []
			print('Cannot find any deal!')
		# result DataFrame lists below
		df_in_page = DataFrame({
			'community_name':'', 
			u'floor_area(㎡)':'', 
			'unit':'', 
			u'avg_price(元/㎡)':'', 
			u'total_price(万/套)':'', 
			'turnover_time':'',
			'district': '',
			'school_name': ''}, index=[0])

		def code_trans(input):
			input = input.encode('raw_unicode_escape')
			return input.decode('raw_unicode_escape')

		# def square_meter_trans(input):
		# 	square_meter_unicode = u'\u33a1'
		# 	input = input[:-1] + square_meter_unicode
		# 	return input

		# 获取每一页的全部成交记录
		def getRecord(url):
			s = requests.session()
			res = s.get(url, headers=headers, verify=False)
			soup = BS(res.text, 'lxml')  # 离奇！这里必须使用text 而非 content，否则无法获取全部内容
			# print soup.prettify()
			records = soup.findAll('div',{'class':'cjjl_con'})
			page_num = urlsplit(url).path.split('/')[-1]
			print 'processing page %s...' % page_num
			records_num = 0 + 20 * (int(page_num) - 1)
			for rec in records:
				# print r.get_text()
				record_dict = {
					'community_name':'',
					u'floor_area(㎡)':'',
					'unit':'',
					u'avg_price(元/㎡)':'',
					u'total_price(万/套)':'',
					'turnover_time':'',
					'district': '',
					'school_name': ''
				}
				record_dict['community_name'] = rec.find('li',{'class':'lione'}).get_text()
				record_dict[u'floor_area(㎡)'] = rec.find('li',{'class':'litwo'}).get_text()
				# 去除单位：㎡
				record_dict[u'floor_area(㎡)'] = record_dict[u'floor_area(㎡)'][:-1]
				record_dict['unit'] = rec.find('li',{'class':'lithree'}).get_text()
				record_dict[u'avg_price(元/㎡)'] = rec.find('li',{'class':'lifour'}).get_text()
				# 去除单位：元/㎡
				record_dict[u'avg_price(元/㎡)'] = record_dict[u'avg_price(元/㎡)'][:-3]
				# print record_dict[u'avg_price(元/㎡)']
				record_dict[u'total_price(万/套)'] = rec.find('li',{'class':'lifive'}).get_text()
				# 去除单位：万/套
				record_dict[u'total_price(万/套)'] = record_dict[u'total_price(万/套)'][:-3]
				record_dict['turnover_time'] = rec.find('li',{'class':'liseven'}).get_text()
				record_dict['district'] = district
				record_dict['school_name'] = school_name
				map(code_trans, record_dict.values())
				# print record_dict
				df_in_page.ix[records_num] = record_dict
				records_num += 1
			print 'successfully saved all deals in page %s!' % page_num
			if int(page_num) % 3 == 0:
				time.sleep(np.random.randint(1,4))
			# df_in_page[u'avg_price(元/㎡)'] = map(square_meter_trans, df_in_page[u'avg_price(元/㎡)'])
			# df_in_page[u'floor_area(㎡)'] = map(square_meter_trans, df_in_page[u'floor_area(㎡)'])

		map(getRecord, pages)
		df_all = pd.concat([df_all, df_in_page], axis=0)
		time.sleep(np.random.randint(1,5))
	except requests.exceptions.ConnectionError:
		print('Opps! Connection error!')
		print df_all
		# df_all.to_csv('/Users/Aldridge/soufang_spider/total_result.csv', encoding='utf-8')

print df_all
time_end = time.time()
print 'total processing time: %fs' % (time_end - time_start)
df_all.to_csv('/Users/Aldridge/soufang_spider/enhanced_total_result.csv', encoding='utf-8')
