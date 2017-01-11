# -*- coding: utf-8 -*-
import scrapy
from elder.items import YanglaoItem						# scrapy的items函数（YanglaoItem）
from elder.data_process import DataProcess 				# 数据格式化函数（自定义）
from scrapy.conf import settings 						# scrapy的设置函数
from datetime import datetime							# 日期模块
import MySQLdb as mdb 									# Mysql数据库模块


class YanglaoSpider(scrapy.Spider):
	name = "yanglao"									# 爬虫名
	allowed_domains = ["yanglao.com.cn"]				# 可访问域名，定义域名后爬虫只访问该域名下的网址
	start_urls = (
		'http://www.yanglao.com.cn/resthome',			# 初始化URL
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
		cur.execute("""DROP TABLE IF EXISTS `yl_%s`;""" % today)	# 如果yl_datetime（yl_20160101）表存在，即删除该表
		cur.execute("""
			CREATE TABLE `yl_%s` (
			  `id` int(11) NOT NULL AUTO_INCREMENT,
			  `名称` varchar(1000) DEFAULT NULL,
			  `地址` varchar(1000) DEFAULT NULL,
			  `使用时间` varchar(100) DEFAULT NULL,
			  `床位` varchar(100) DEFAULT NULL,
			  `max收费` varchar(100) DEFAULT NULL,
			  `min收费` varchar(100) DEFAULT NULL,
			  `机构性质` varchar(100) DEFAULT NULL,
			  `占地面积` varchar(100) DEFAULT NULL,
			  `收住对象` varchar(500) DEFAULT NULL,
			  `设施` varchar(3000) DEFAULT NULL,
			  `交通` varchar(1000) DEFAULT NULL,
			  `机构类型` varchar(100) DEFAULT NULL,
			  `服务内容` varchar(5000) DEFAULT NULL,
			  `入住要求` varchar(2000) DEFAULT NULL,
			  `网址` varchar(255) DEFAULT NULL,
			  `邮编` varchar(100) DEFAULT NULL,
			  `简介` varchar(6000) DEFAULT NULL,
			  `省` varchar(255) DEFAULT NULL,
			  `市` varchar(255) DEFAULT NULL,
			  `区` varchar(255) DEFAULT NULL,
			  PRIMARY KEY (`id`)
			) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
			""" % today)											# 新建yl_datetime（yl_20160101）表
		con.close()

	def parse(self, response):
		# ==========从访问的页面上页获取全部养老院链接，并生成Request请求，把response发给parse_page函数
		for url in response.css('div.list-view h4 a').xpath('@href').extract():
			yield scrapy.Request(response.urljoin(url), callback=self.parse_page)
			# break

		# ==========从页底获取下一页的链接，生成Request请求，把response发给原来的parse函数做循环
		next_url = response.css('ul.pages li a').xpath('@href').extract()
		next_url = next_url[-2] if len(next_url)>1 else next_url[0]		# 下一页链接是所获取链接的倒数第二个，所以要取[-2]
		yield scrapy.Request(response.urljoin(next_url), callback=self.parse)

	def parse_page(self, response):
		item = YanglaoItem()	# 定义item
		item['name'],item['address'],item['since'],item['bed'],item['max_charge'],item['min_charge'],item['organization'],item['area'],item['target'],\
			item['facility'],item['transport'],item['category'],item['service'],item['notice'],item['website'],item['post'],item['intro'],item['province'],\
			item['city'],item['district'] = '','','','','','','','','','','','','','','','','','','',''		# 给全部item赋空值，避免以后出错

		# ==========从页面上获取的字段字典
		dic = {
			'地     址：':'address',
			'床     位：':'bed',
			'收     费：':'charge',
			'机构类型：':'category',
			'机构性质：':'organization',
			'占地面积：':'area',
			'收住对象：':'target',
			'成立时间：':'since',
			'邮        编：':'post',
			'网        址：':'website',
			'交        通：':'transport',
			'所在地区：':'address_info',
			# '电     话：':'phone',
			# '特色服务：':'special',
			}
		# ==========xpath和item替换字典
		dic2 = {
			'intro':'div.inst-intro',
			'facility':'div.facilities',
			'service':'div.service-content',
			'notice':'div.inst-notes',
		}

		item['name'] = ''.join([i.strip() for i in response.css('div.inst-summary h1::text').extract()])	# 养老院名称
		for i in response.css('div.main li'):												# 从基本信息栏获里取信息，做for循环
			text = ''.join([j.strip() for j in i.css('::text').extract()]).split(u'\uff1a')	# 得到li里边的全部文字，并在“：”符号处分词
			text = text[1] if len(text)==2 else ''.join(text)								# 如果分词后有2个字段，即赋第二个值，如：“名称：养老院” = “养老院”
			text = text.encode('utf-8')  
			try:
				key = dic[i.css('em::text').extract_first(default='').encode('utf-8')]		# 获取栏名，并找出对应的item字段，如：'地     址：'对应'address'
				if key == 'charge':															# 当key=charge时，将charge的max和min值分开，赋给max_charge和min_charge
					item['max_charge'] = text.split('-')[1]									
					item['min_charge'] = text.split('-')[0]
				elif key=='address_info':													# 当key=address_info时，获取省市县信息，并赋给对应item
					detail = text.split('-')
					item['province'] = detail[0].strip() if len(detail)>0 else ''
					item['city'] = detail[1].strip() if len(detail)>1 else ''
					item['district'] = detail[2].strip() if len(detail)>2 else ''
				elif key=='transport':														# 当key=transport时，获取从下一个li里的全部文字，赋给对应item
					item['transport'] = ''.join([i.strip() for i in i.xpath('following-sibling::li//text()').extract()]).encode('utf-8')
				else:
					item[key] = text
				
			except Exception, e:
				pass

		for key,value in dic2.items():						# 用dic2里的key和value做for循环，获取信息后赋给对应item
			item[key] = ''.join([i.strip() for i in response.css(value).xpath('.//text()').extract()]).encode('utf-8') 

		yield DataProcess().YanglaoProcess(item)			# 用DataProcess模块做数据处理，并生成item

