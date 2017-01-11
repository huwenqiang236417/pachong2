# -*- coding: utf-8 -*-
import scrapy
from elder.items import HospItem
# from elder.items import HospDepartmentItem
from elder.items import HospDoctorItem
from scrapy.conf import settings
from datetime import datetime
import MySQLdb as mdb


class GuahaoSpider(scrapy.Spider):
	name = "guahao"
	allowed_domains = ["guahao.com","wu.gov.cn"]
	start_urls = (
		'http://www.guahao.com/search/hospital',
	)
	custom_settings = {
		'ITEM_PIPELINES' : {
			'elder.pipelines.HospPipeline':100,	
			},
	}

	def __init__(self):
		now = datetime.now()
		today = str(now.year) + str(now.month).zfill(2) + str(now.day).zfill(2)
		con = mdb.connect(host=settings['MYSQL_HOST'], user=settings['MYSQL_USER'], passwd=settings['MYSQL_PASS'], db=settings['MYSQL_DB'],charset='utf8');
		cur = con.cursor()
		cur.execute("""DROP TABLE IF EXISTS `hosp_%s`;""" % today)
		cur.execute("""
			CREATE TABLE `hosp_%s` (
			  `id` int(11) NOT NULL AUTO_INCREMENT,
			  `名称` varchar(1000) DEFAULT NULL,
			  `地址` varchar(1000) DEFAULT NULL,
			  `电话` varchar(100) DEFAULT NULL,
			  `简介` varchar(5000) DEFAULT NULL,
			  `描述` varchar(5000) DEFAULT NULL,
			  `网站` varchar(100) DEFAULT NULL,
			  `等级` varchar(100) DEFAULT NULL,
			  `省` varchar(255) DEFAULT NULL,
			  `市` varchar(255) DEFAULT NULL,
			  `区` varchar(255) DEFAULT NULL,
			  PRIMARY KEY (`id`)
			) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
			""" % today)

		# cur.execute("""DROP TABLE IF EXISTS `hospdept_%s`;""" % today)
		# cur.execute("""
		# 	CREATE TABLE `hospdept_%s` (
		# 	  `id` int(11) NOT NULL AUTO_INCREMENT,
		# 	  `医院名` varchar(1000) DEFAULT NULL,
		# 	  `主科` varchar(100) DEFAULT NULL,
		# 	  `子科` varchar(100) DEFAULT NULL,
		# 	  `人员` varchar(100) DEFAULT NULL,
		# 	  PRIMARY KEY (`id`)
		# 	) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
		# 	""" % today)

		cur.execute("""DROP TABLE IF EXISTS `hospdoc_%s`;""" % today)
		cur.execute("""
			CREATE TABLE `hospdoc_%s` (
			  `id` int(11) NOT NULL AUTO_INCREMENT,
			  `医院名` varchar(1000) DEFAULT NULL,
			  `主科` varchar(100) DEFAULT NULL,
			  `子科` varchar(100) DEFAULT NULL,
			  `姓名` varchar(100) DEFAULT NULL,
			  `职称` varchar(500) DEFAULT NULL,
			  `主治项目` varchar(1000) DEFAULT NULL,
			  `擅长` varchar(1000) DEFAULT NULL,
			  `简介` varchar(5000) DEFAULT NULL,
			  `专家团队` varchar(100) DEFAULT NULL,
			  `预约挂号` varchar(3000) DEFAULT NULL,
			  `专业挂号` varchar(1000) DEFAULT NULL,
			  `挂号功能` varchar(10) DEFAULT NULL,
			  `图文功能` varchar(10) DEFAULT NULL,
			  `电话功能` varchar(10) DEFAULT NULL,
			  `视频功能` varchar(10) DEFAULT NULL,
			  PRIMARY KEY (`id`)
			) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
			""" % today)
		con.close()

		self.lis = ['address','tel','website','about'] #定义两个表，用来存入待爬取数据；
		# self.hosp = 'hosp_%s' % today
		# self.hospdept = 'hospdept_%s' % today
		# self.hospdoc = 'hospdoc_%s' % today
		# self.con = con
		# self.cur = cur

	def start_requests(self):
		for i in range(1,44):
			url = 'http://www.guahao.com/search/hospital?pageNo=%s' % i  #循环请求按页码区分的地址。
			yield scrapy.Request(url, callback=self.parse)

	def parse(self, response):
		for url in response.css('div.hos-total a').xpath('@href').extract(): #
			yield scrapy.Request(url, callback=self.parse_hosp)

	def parse_hosp(self, response):
		about_url = ''
		item = HospItem()
		item['name'],item['address'],item['tel'],item['about'],item['description'],item['website'],item['province'],item['city'],item['district'] = '','','','','','','','',''

		item['name'] = ''.join([i.strip() for i in response.css('h1 strong').xpath('.//text()').extract()])
		item['degree'] = response.css('h1 span::text').extract_first(default='')
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
