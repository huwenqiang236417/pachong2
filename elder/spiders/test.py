# -*- coding: utf-8 -*-
import scrapy
from elder.items import TestItem

class TestSpider(scrapy.Spider):
	name = "test"
	allowed_domains = ["baidu.com"]
	start_urls = (
		'http://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=0&rsv_idx=1&tn=baidu&wd=%E5%85%BB%E8%80%81%E9%99%A2&rsv_pq=9cc8be10000227bb&rsv_t=1989QLWBs0fcbwnGXRiDrHGtps0pUTwmDHkdPgwxZz7bPUn4%2BwfFyZjqtAY&rsv_enter=1&rsv_sug3=10&rsv_sug1=1&rsv_sug7=100',
	)
	custom_settings = {
		'ITEM_PIPELINES' : {
			'elder.pipelines.MySQLStorePipeline':100,
			},
	}

	def parse(self, response):
		# for u in  response.css('div#content_left h3 a').xpath('@href').extract():
		# with open('url.txt', 'wb') as f:
		for u in response.css('div#content_left h3 a'):
			item = TestItem()
			item['url'] = u.xpath('@href').extract_first(default='')
			item['text'] = ''.join(u.xpath('.//text()').extract())
			yield item

			# print ''.join(u.xpath('.//text()').extract())
			# f.write(''.join(u.xpath('.//text()').extract())+'\n\n'.encode('utf-8'))
		# f.close()