# -*- coding:utf-8 -*-
import requests
import numpy as np
from bs4 import BeautifulSoup as BS 

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

# 获取学校列表页当中每个学校的独立页面链接
url1 = 'http://esf.hz.fang.com/school-a0151/i31/'
url2 = 'http://esf.hz.fang.com/school-a0151/i32/'


def getSchoolLink(url):
	base_session = requests.session()
	base_res = base_session.get(url,headers=headers, verify=False)
	base_soup = BS(base_res.text, 'lxml')
	print('Connect successfully!')
	school_list = base_soup.find('div',{'class':'schoollist'})
	schools = school_list.findAll('dl')
	link_base = 'http://esf.hz.fang.com'
	school_link_dict = {}
	for school in schools:
		school_name = school.find('p',{'class':'title'}).a.get_text()
		link_middle = school.find('p',{'class':'title'}).a['href'][:-4]
		link_complete = link_base + link_middle + '/deal/#deal'
		# print link_complete
		school_link_dict[school_name] = link_complete
	return school_link_dict

schoolDict1 = getSchoolLink(url1)
schoolDict2 = getSchoolLink(url2)
del schoolDict2[u'大禹路小学甲来路校区']
# print schoolDict1
