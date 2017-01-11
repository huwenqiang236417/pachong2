# -*- coding: utf-8 -*-
import scrapy


class EztSpider(scrapy.Spider):
	name = "ezt"
	allowed_domains = ["www.eztcn.com"]
	start_urls = (
		'http://www.eztcn.com/Home/Find/findHos.html',
	)

	def parse(self, response):
		for url in response.css('div.sh_hospital_name a').xpath('@href').extract():
			yield scrapy.Request(response.urljoin(url),callback=self.parse_page)

	# def parse_page(self, response):
		
		# id	名称	省（直辖市）	市（区）	县（街道）	地址	医生	科室	科室最大特色（例：国内、唯一、领先、重点学科、实验室）	职称	挂号量	挂号日期	是否有号	床位	收费	最高收费	最低收费	主治项目	电话	是否公办	医院级别（三级？）	医院等级（甲等）	医学最大特色	占地面积	工作人员	医疗仪器设备	交通	网址	邮编	医院简介	患者评价	其他

	
