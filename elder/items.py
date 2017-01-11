# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class ElderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class YaofangItem(scrapy.Item):
	name = scrapy.Field()
	address = scrapy.Field()
	xuke = scrapy.Field()

class YanglaoItem(scrapy.Item):
	name = scrapy.Field()				#名称		
	address = scrapy.Field()			#地址
	since = scrapy.Field()			#使用时间
	bed = scrapy.Field()				#床位
	max_charge = scrapy.Field()			#max_收费
	min_charge = scrapy.Field()			#min_收费
	organization = scrapy.Field() 		#机构性质
	area = scrapy.Field()				#占地面积
	target = scrapy.Field()				#收住对象
	facility = scrapy.Field()			#设施
	transport = scrapy.Field()			#交通
	category  = scrapy.Field()			#机构类型
	service = scrapy.Field()			#服务内容
	notice = scrapy.Field()				#入住要求
	website = scrapy.Field()			#网址
	post = scrapy.Field()				#邮编
	intro = scrapy.Field()				#简介
	province = scrapy.Field()			#省
	city = scrapy.Field()				#市
	district = scrapy.Field()			#县

class BaikeItem(scrapy.Item):
	chinese = scrapy.Field()			#中文名称
	english = scrapy.Field()			#英文名称
	category = scrapy.Field()			#行政区类别
	belong_to = scrapy.Field()			#所属地区
	administer_area = scrapy.Field()	#下辖地区
	government_resident = scrapy.Field()#政府驻地
	phone = scrapy.Field()				#电话区号
	post = scrapy.Field()				#邮政区码
	geography = scrapy.Field()			#地理位置
	area = scrapy.Field()				#面积
	population = scrapy.Field()			#人口
	language = scrapy.Field()			#方言
	weather = scrapy.Field()			#气候条件
	famous_place = scrapy.Field()		#著名景点
	airport = scrapy.Field()			#机场
	train_station = scrapy.Field()		#火车站
	functional_divition = scrapy.Field()#功能划分
	income = scrapy.Field()				#收入
	main_id = scrapy.Field()			#省市县表中的id号

class HospItem(scrapy.Item):
	name = scrapy.Field()
	address = scrapy.Field()
	tel = scrapy.Field()
	about = scrapy.Field()
	description = scrapy.Field()
	website = scrapy.Field()
	degree = scrapy.Field()
	province = scrapy.Field()
	city = scrapy.Field()
	district = scrapy.Field()

# class HospDepartmentItem(scrapy.Item):
# 	hosp_name = scrapy.Field()
# 	department = scrapy.Field()
# 	sub_department = scrapy.Field()
# 	worker = scrapy.Field()

class HospDoctorItem(scrapy.Item):
	hosp_name = scrapy.Field()
	department = scrapy.Field()
	sub_department = scrapy.Field()
	name = scrapy.Field()
	profession = scrapy.Field()
	fields = scrapy.Field()
	specialty = scrapy.Field()
	about = scrapy.Field()
	group = scrapy.Field()
	schedule = scrapy.Field()
	pro_schedule = scrapy.Field()
	register = scrapy.Field()
	picture = scrapy.Field()
	mobile = scrapy.Field()
	video = scrapy.Field()

class TestItem(scrapy.Item):
	name = scrapy.Field()
	address = scrapy.Field()