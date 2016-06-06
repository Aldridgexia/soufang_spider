# -*- coding:utf-8 -*-
import pandas as pd 
from pandas import DataFrame

filepath = '/Users/Aldridge/soufang_spider/data_requirement.xls'
table = pd.read_excel(filepath, sheetname='Sheet1', header=None)
table.columns = ['community_name']
filepath2 = '/Users/Aldridge/soufang_spider/total_result_new.xlsx'
df_all = pd.read_excel(filepath2, index_col=0)
df_result = DataFrame({'community_name':'', 'floor_area':'', 'unit':'', 'avg_price':'', 'total_price':'', 'turnover_time':''}, index=[])
for cn, group in df_all.groupby('community_name'):
	if cn in list(table['community_name']):  # .ix[15:]
		df_result = pd.concat([df_result, group], axis=0)
df_result = df_result[['community_name', 'turnover_time', 'total_price', 'avg_price', 'unit', 'floor_area']]
# print df_result

table_list = table.values.tolist()
sorter = []
for item in table_list:
	sorter.append(item[0])
df_result['sorter'] = df_result['community_name']
df_result.sorter = df_result.sorter.astype('category')
df_result.sorter.cat.set_categories(sorter, inplace=True)
df_result_new = df_result.sort_values(['sorter'])
del df_result_new['sorter']

print df_result_new
