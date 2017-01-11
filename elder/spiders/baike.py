# -*- coding: utf-8 -*-
import scrapy
import MySQLdb as mdb 										# Mysql数据库模块
from elder.items import BaikeItem							# scrapy的items函数（BaikeItem）


class BaikeSpider(scrapy.Spider):
	name = "baike"											# 爬虫名
	allowed_domains = ["baike.baidu.com"]					# 可访问域名，定义域名后爬虫只访问该域名下的网址
	start_urls = (
		'http://www.baike.baidu.com/',						# 初始化URL
	)
	custom_settings = {
		'ITEM_PIPELINES' : {
			'elder.pipelines.CrawlerStorePipeline':100,		# 开通CrawlerStorePipeline
			},
	}

	def __init__(self):
		# ==========初始化函数
		self.con = mdb.connect(host=settings['MYSQL_HOST'], user=settings['MYSQL_USER'], passwd=settings['MYSQL_PASS'], db=settings['MYSQL_DB'],charset='utf8');
		self.cur = self.con.cursor()						# 创建数据库连接，定义连接指针
		self.dict = {
			'中文名称':'chinese',
			'外文名称':'english',
			'行政区类别':'category',
			'所属地区':'belong_to',
			'下辖地区':'administer_area',
			'政府驻地':'government_resident',
			'电话区号':'phone',
			'邮政区码':'post',
			'地理位置':'geography',
			'面    积':'area',
			'人    口':'population',
			'方    言':'language',
			'气候条件':'weather',
			'著名景点':'famous_place',
			'机    场':'airport',
			'火车站':'train_station',
			'功能划分':'functional_divition',
			'收    入':'income',
		}

	def start_requests(self):
		# ==========生成初始请求函数
		self.cur.execute("SELECT * FROM 省市县;") 		# 从`省市县`表里获取全部省市县信息
		datas = self.cur.fetchall()						# 将获取的信息赋给datas序列
		for d in datas:			
			# ==========d[0]:id, d[1]:省, d[2]:市, d[3]:县或区域, d[4]:人口数量	
			url = 'http://baike.baidu.com/search/none?word=%s&pn=0&rn=10&enc=utf8' % '%20'.join(set(d[1:-2]))# 替换百度百科搜索链接里的搜索字段，如：北京市 朝阳区
			yield scrapy.Request(url, callback=self.parse, meta={'id':int(d[0])})					# 生成新请求，并且将县或区域在`省市县`表里的id传给parse函数

	def parse(self, response):
		url = response.css('dl.search-list dd a.result-title').xpath('@href').extract_first(default='')	# 从结果页面获取第一个链接
		yield scrapy.Request(url, callback=self.parse_page, meta={'id':int(d[0])})					# 生成新请求，并且将县或区域在`省市县`表里的id传给parse函数

	def parse_page(self, response):
		item = BaikeItem()		# 定义item
		item['chinese'],item['english'],item['category'],item['belong_to'],item['administer_area'],item['government_resident'],item['phone'],item['post'],\
			item['geography'],item['area'],item['population'],item['language'],item['weather'],item['famous_place'],item['airport'],item['train_station'],\
			item['functional_divition'],item['main_id'],item['income'] = '','','','','','','','','','','','','','','','','','','' # 给全部item赋空值，避免以后出错
		
		dts = response.css('div.basic-info dt')																# 从基本信息表里获取全部行
		for dt in dts:
			key = dt.xpath('text()').extract_first(default='').encode('utf-8')								# 获取栏名
			try:
				item[self.dict[key]] = dt.xpath('following-sibling::dd/text()').extract_first(default='')	# 根据栏名，给对应item赋值
			except Exception, e:
				pass

		item['main_id'] = response.meta['id']				# 给item['main_id']赋`省市县`表里对应的id号，以便以后查找
		contents = response.xpath('//text()').extract()		# 由于基本信息表里没有“人均可支配收入”信息，所以把页面上全部含“人均可支配收入”的字段存到item[income]里
		for c in contents:
			if '人均可支配收入'.decode('utf-8') in c or '':
				item['income'] += c
		
		yield item