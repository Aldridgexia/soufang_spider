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
from xiaoqu_list import sorter, df_result_new
import gzip
from StringIO import StringIO

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

url_base = 'http://esf.hz.fang.com/house/'
query_param = {'c61-kw':''}
url_list = []
for name in sorter:
    name = name.encode('GB2312')
    query_param['c61-kw'] = name
    url_total = url_base + urlencode(query_param) + '/'
    url_list.append(url_total)
# print url_list


def get_target_link(url):
    s = requests.session()
    res = s.get(url, headers=headers, verify=False)
    soup = BS(res.text, 'lxml')
    print 'search page connect successfully!'
    target_link = ''
    try:
        target_link = soup.find('a',{'class':'blueword'})['href']
        print 'successfully get the target link!'
        return target_link
    except TypeError:
        target_link = ''
        print 'cannot find target link!'
    time.sleep(np.random.randint(1, 3))

# get_page(url_list[0])
url_list = map(get_target_link, url_list)
print url_list

basic_info_df = DataFrame(columns=[
    u'产权描述：', u'占地面积：', u'容 积 率：', u'小区地址：', u'建筑类别：', u'建筑结构：', u'建筑面积：',
    u'开 发 商：', u'当期户数：', u'总 户 数：', u'所属区域：', u'物 业 费：', u'物业办公电话：',
    u'物业类别：', u'竣工时间：', u'绿 化 率：', u'邮    编：', u'附加信息：', u'项目特色：'], index=[])


def get_basic_info(url, df=basic_info_df):
    # url = url_list[0]
    try:
        request = urllib2.Request(url, headers=headers)
        response = urllib2.urlopen(request)
        # 以下代码解决内容乱码问题
        buf = StringIO(response.read())
        gzip_f = gzip.GzipFile(fileobj=buf)
        content = gzip_f.read()
        content = content.decode('gbk')
        soup = BS(content, 'lxml')
        print 'basic info page connect successfully!'
        block = soup.find('dl', {'class':'lbox'})
        # print block
        basic_info_dict = {}
        items = block.findAll('dd')
        for item in items:
            if type(item.contents[1]) != bs4.element.Tag:
                basic_info_dict[item.strong.text] = item.contents[1]
            else:
                basic_info_dict[item.strong.text] = item.contents[1].text
        # print basic_info_dict
        basic_info_record = DataFrame(basic_info_dict, index=[np.random.randint(1, len(url_list) + 1)])
        df = pd.concat([df,basic_info_record], axis=0)
        # print df
        print 'basic info of this page has been saved!'
        return df
    except ValueError:
        pass
    # return basic_info_dict

# get_basic_info(url_list[0])

basic_info_df = reduce(lambda x,y: pd.concat([x,y],axis=0), map(get_basic_info, url_list))
basic_info_df.index = sorter
# print basic_info_df

# 添加容积率等字段
df_needed = df_result_new.copy()
df_needed['establish_time'] = np.zeros(len(df_needed))
df_needed['plot_ratio'] = np.zeros(len(df_needed))
df_needed['greening_rate'] = np.zeros(len(df_needed))

info_needed = basic_info_df[[u'竣工时间：', u'容 积 率：', u'绿 化 率：']]
for i in range(len(info_needed)):
    # print df_result_new[df_result_new['community_name'] == info_needed.index[i]]
    temp = df_needed[df_needed['community_name'] == info_needed.index[i]]  # .ix[15:]
    if temp.empty is not True:
        df_needed['establish_time'][df_needed['community_name'] == info_needed.index[i]] = info_needed.ix[i][u'竣工时间：']
        df_needed['plot_ratio'][df_needed['community_name'] == info_needed.index[i]] = info_needed.ix[i][u'容 积 率：']
        df_needed['greening_rate'][df_needed['community_name'] == info_needed.index[i]] = info_needed.ix[i][u'绿 化 率：']

print df_needed

# df_needed.to_csv('/Users/Aldridge/soufang_spider/final_info.csv', encoding='utf-8')

# 骆家庄西苑
# 桂花城
# 政新花园
# 三坝雅苑
