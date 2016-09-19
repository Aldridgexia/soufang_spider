# -*- coding:utf-8 -*-
import requests
import numpy as np
from bs4 import BeautifulSoup as BS
from pandas import DataFrame
import pandas as pd
pd.set_option('expand_frame_repr', False)

headers = {
	"User-Agent":'',
	"accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
	"accept-encoding":"gzip, deflate, sdch",
	"accept-language":"zh-CN,zh;q=0.8,en;q=0.6",
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

# 五个主城区各自拥有的学校页面链接
# 上城区
link_shangcheng = 'http://esf.hz.fang.com/school-a0149/'
# 下城区
link_xiacheng = 'http://esf.hz.fang.com/school-a0150/'
# 西湖区
link_xihu = 'http://esf.hz.fang.com/school-a0151/'
# 拱墅区
link_gongshu = 'http://esf.hz.fang.com/school-a0152/'
# 江干区
link_jianggan = 'http://esf.hz.fang.com/school-a0153/'
# 五个城区名称用编号0到4表示
chengqu_name_dict = {
	0: u'上城区', 1: u'下城区', 2: u'西湖区', 3: u'拱墅区', 4: u'江干区'
}

# 存放爬取结果的容器
school_deal_link_dict = {}
school_deal_link_df = DataFrame(columns=['district', 'school_name', 'deal_link'])

# 获取学校成交记录页面链接的函数
def getSchoolDealLink(url, school_deal_link_dict):
	base_session = requests.session()
	base_res = base_session.get(url,headers=headers, verify=False)
	base_soup = BS(base_res.text, 'lxml')
	print('Deal page connects successfully!')
	next_page = base_soup.find('a', {'id':'PageControl1_hlk_next'})
	if next_page:
		next_page = next_page['href']
		next_page_link = 'http://esf.hz.fang.com/' + next_page
		# print next_page_link
		# 递归调用自身，获取全部链接
		getSchoolDealLink(next_page_link, school_deal_link_dict)
	school_list = base_soup.find('div',{'class':'schoollist'})
	schools = school_list.findAll('dl')
	link_base = 'http://esf.hz.fang.com'
	for school in schools:
		school_name = school.find('p',{'class':'title'}).a.get_text()
		link_middle = school.find('p',{'class':'title'}).a['href'][:-4]
		link_complete = link_base + link_middle + '/deal/#deal'
		# print link_complete
		school_deal_link_dict[school_name] = link_complete
	return school_deal_link_dict

# 获取各个城区全部学校的独立链接
for i in xrange(149, 154):
	url = 'http://esf.hz.fang.com/school-a0%i/' % i
	temp_dict = {}
	temp_df = DataFrame(columns=['district', 'school_name', 'deal_link'])
	temp_dict = getSchoolDealLink(url, temp_dict)
	temp_df['school_name'] = temp_dict.keys()
	temp_df['deal_link'] = temp_dict.values()
	temp_df['district'] = chengqu_name_dict[i - 149]
	school_deal_link_df = pd.concat([school_deal_link_df, temp_df], axis=0)
	school_deal_link_dict.update(temp_dict)

# 测试
# for key in school_deal_link_dict.keys():
# 	print key

# for value in school_deal_link_dict.values():
# 	print value

# print school_deal_link_df
