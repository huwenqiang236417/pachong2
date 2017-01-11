# -*- coding: UTF-8 -*-

import re
from cn2dig import cn2dig			# 文字转化数字函数（自定义）


class DataProcess():
	def __init__(self):
		# ==========初始化函数
		self.number_dict = {		# 汉字与数字字典
			'〇':'0',
			'零':'0',
			'一':'1',
			'二':'2',
			'两':'2',
			'三':'3',
			'四':'4',
			'五':'5',
			'六':'6',
			'七':'7',
			'八':'8',
			'九':'9',
			'十':'10',
			}
		self.area_dict = {			# 平方米、亩、顷字典
			'百':100,
			'千':1000,
			'万':10000,
			'亩':100,
			'顷':10000,
		}

	def YanglaoProcess(self, item):
		# ===========1.修改年月日格式
		pattern = re.compile('|'.join(self.number_dict.keys()))					# 定汉字pattern
		date = pattern.sub(lambda x: self.number_dict[x.group()], item['since'])# 根据pattern，将汉字转换成数字，例如：二零一一 =2011
		year = ''.join([date[i:i+4] if date[i:i+4].isdigit() and len(date[i:i+4])==4 else '' for i in range(0,len(date))])	# 从字段里获取连续4个数字，判断为年
		if year=='' and date!='':												# 如果year没有定成功，并且date原来不是空的，说明字段里的年是其他格式，需要再修改
			if '年' in date or '.' in date:										# 如果字段里有“年”或“.”则做分词
				y = date.split('年')
				y = date.split('.')[0] if len(y)==1 else y[0]
				if len(y)==2:													# 如果y的长度为2，说明二位数标识的年份，需要改成四位数，如：58年=1958
					year = '20'+y if y[0]=='0' else '19'+y
				elif len(y)==4:													# 如果y的长度为4，则year=y
					year = y
		item['since'] = year

		# ===========2.修改床位数格式
		item['bed'] = item['bed'].replace('张','')								# 从床位数字段里删除“张”字,用replace后面的值替代前面的。

		# ===========3.修改占地面积格式
		area = item['area']
		if area!='' and area.isdigit()==False:									# 如果面积不是空，并且不是数字，则进行格式化处理
			try:
				area = '1' + area if self.area_dict.has_key(area[0]) else area 	# 如果面积第一个字为“百、千、万”，则在“1”+area，如：百平米=1百平米
				num = ''.join([area[i] if self.number_dict.has_key(area[i]) or area[i].isdigit() or area[i]=='.' else ' ' for i in range(0,len(area))]).strip()
				# 从area字段里分出数字，如：共2万平米=2万
				num = cn2dig(num.split(' ')[0]) 								# 用cn2dig函数，汉字转换为数字，如：两千=2000
				for j in self.area_dict.keys():									
					num = num*self.area_dict[j] if j in area else num 			# 如果num有亩、顷等字，则num乘以对应字典值
				area = num
			except Exception, e:
				print e
		item['area'] = area

		# ===========4.修改设施格式
		facility = item['facility']
		item['facility'] = '' if facility=='设施暂无详细介绍，具体详情请致电咨询！' else facility.replace('设施','')

		# ===========5.修改服务内容格式
		service = item['service']
		item['service'] = '' if service=='服务内容暂无详细介绍，具体详情请致电咨询！' else service.replace('服务内容','')

		# ===========6.修改入住须知格式
		notice = item['notice']
		item['notice'] = '' if notice=='入住须知暂无详细介绍，具体详情请致电咨询！' else notice.replace('入住须知','')

		return item

if __name__=='__main__':
	datafix = Datafix()
	mysql = datafix.mysql()