# -*- coding: utf-8 -*-
import scrapy
from elder.items import YaofangItem						# scrapy的items函数（YiyuanItem）
from elder.data_process import DataProcess 				# 数据格式化函数（自定义）
from scrapy.conf import settings 						# scrapy的设置函数
from datetime import datetime							# 日期模块
import MySQLdb as mdb 									# Mysql数据库模块


class YaofangSpider(scrapy.Spider):
	name = "yaofang"									# 爬虫名
	allowed_domains = ["yaofangwang.com"]				# 可访问域名，定义域名后爬虫只访问该域名下的网址
	start_urls = (
		'http://www.yaofangwang.com/yaodian/',			# 初始化URL
	)
	custom_settings = {
		'ITEM_PIPELINES' : {
			'elder.pipelines.CrawlerStorePipeline':100,	# 开通CrawlerStorePipeline
			},
	}

	def __init__(self):
		# ==========初始化函数
		now = datetime.now()										# 获取当前日期
		today = str(now.year) + str(now.month).zfill(2) + str(now.day).zfill(2)		# 将日期转换为字段形式，如：20160101
		con = mdb.connect(host=settings['MYSQL_HOST'], user=settings['MYSQL_USER'], passwd=settings['MYSQL_PASS'], db=settings['MYSQL_DB'],charset='utf8');
		cur = con.cursor()											# 创建数据库连接，定义连接指针
		cur.execute("""DROP TABLE IF EXISTS `yaofang_%s`;""" % today)	# 建立新表，如果存在，则删除；
		cur.execute("""
			CREATE TABLE `yaofang_%s`  (
			  `id` int(11) NOT NULL AUTO_INCREMENT,
			  `名称` varchar(1000) DEFAULT NULL,
			  `地址` varchar(1000) DEFAULT NULL,
			  `经营许可` varchar(100) DEFAULT NULL
			  PRIMARY KEY (`id`)
			) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
			""" % today)										# 新建表yaofang_
		con.close()


		self.lis = ['address','tel','website','about'] #定义两个表，用来存入待爬取数据；



	def start_requests(self):
		for i in range(1,44):
			url = 'http://www.yaofangwang.com/yaodian/shops-40-0-%s.html' % i  #循环请求按页码区分的地址。
			yield scrapy.Request(url, callback=self.parse)

	def parse(self, response):
		for url in response.css('div.hos-total a').xpath('@href').extract(): #
			yield scrapy.Request(url, callback=self.parse_hosp)

	def parse_hosp(self, response):
		about_url = ''
		item = YaofangItem()
		item['name'],item['address'],item['xuke'] = '','',''

		item['name'] = ''.join([i.strip() for i in response.css('h1 strong').xpath('.//text()').extract()])
		item['address'] = response.css('h1 span::text').extract_first(default='')
		for j in self.lis:
			if j=='about':
				about_url = response.css('div.about a').xpath('@href').extract_first(default='')
			else:
				item[j] = response.css('div.'+j+' span::text').extract_first(default='')
		item['description'] = ''.join([i.strip() for i in response.css('div.more-description-container').xpath('.//text()').extract()])
		if about_url!='':
			yield scrapy.Request(about_url, callback=self.parse_about, meta={'item':item})
		else:
			yield item

		for dept in response.css('section.hospital-dept div.grid-content li.g-clear'):
			department = dept.css('label::text').extract_first(default='')
			for sub in dept.css('span'):
				sub_department = sub.css('a::text').extract_first(default='')

				url = sub.css('a').xpath('@href').extract_first(default='').replace('department/','department/shiftcase/')
				yield scrapy.Request(url, callback=self.parse_dept, meta={'hosp_name':item['name'],'dept':department,'subdept':sub_department})

	def parse_about(self, response):
		item = response.meta['item']
		item['about'] = ''.join([i.strip() for i in response.css('div.introduction-content').xpath('.//text()').extract()])
		yield item

	def parse_dept(self, response):
		for i in response.css('div.doc-box a.name').xpath('@href').extract():
			yield scrapy.Request(i, callback=self.parse_doc,meta=response.meta)

	def parse_doc(self, response):
		item = HospDoctorItem()
		item['hosp_name'],item['department'],item['sub_department'],item['name'],item['profession'],item['fields'],item['specialty'],item['about'],item['schedule'],\
		item['pro_schedule'],item['picture'],item['mobile'],item['video'],item['group'],item['register']='','','','','','','','','','','','','','',''
		item['hosp_name'] = response.meta['hosp_name']
		item['department'] = response.meta['dept']
		item['sub_department'] = response.meta['subdept']
		item['name'] = response.css('div.detail h1 strong::text').extract_first(default='')
		item['profession'] = ''.join([i.strip() for i in response.css('div.detail h1 span::text').extract()])
		item['fields'] = ''.join([i.strip() for i in response.css('div.keys').xpath('.//text()').extract()])
		item['specialty'] = ','.join([i.strip() for i in response.css('div.goodat').xpath('.//text()').extract()])
		item['about'] = ''.join([i.strip() for i in response.css('div.about').xpath('.//text()').extract()])
		item['schedule'] = ''.join([i.strip() for i in response.css('li.schedules-item').xpath('.//text()').extract()])
		item['pro_schedule'] = ''.join([i.strip() for i in response.css('section.expert-add-schedule').xpath('.//text()').extract()])
		# item['register'] = ''.join([i.strip() for i in response.css('div.guahao').xpath('.//text()').extract()])
		item['picture'] = ''.join([i.strip() for i in response.css('div.tuwen').xpath('.//text()').extract()])
		item['mobile'] = ''.join([i.strip() for i in response.css('div.dianhua').xpath('.//text()').extract()])
		item['video'] = ''.join([i.strip() for i in response.css('div.shipin').xpath('.//text()').extract()])
		item['group'] = ''.join([i.strip() for i in response.css('a.expert-group').xpath('.//text()').extract()])
		item['register'] = 'yes' if 'active' in response.css('a.guahao').xpath('@class').extract_first(default='') else 'no'
		# item['picture'] = 'yes' if 'active' in response.css('a.tuwen').xpath('@class').extract_first(default='') else 'no'
		# item['mobile'] = 'yes' if 'active' in response.css('a.dianhua').xpath('@class').extract_first(default='') else 'no'
		# item['video'] = 'yes' if 'active' in response.css('a.shipin').xpath('@class').extract_first(default='') else 'no'

		yield item



