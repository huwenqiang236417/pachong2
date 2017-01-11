# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from twisted.enterprise import adbapi
import re, time
import MySQLdb.cursors
from scrapy import log
from scrapy.conf import settings
from datetime import datetime
from hashlib import md5
# from scrapy import log
from scrapy.exceptions import DropItem


class ElderPipeline(object):
	def process_item(self, item, spider):
		return item


class CrawlerStorePipeline(object):
	"""这里不用看得那么详细，只修改底下的MySQL语句就可以"""

	def __init__(self, dbpool):
		# ==========初始化函数
		self.dbpool = dbpool					# 定义多线程池
		now = datetime.now()					# 获取今天的日期
		self.add_date = str(now.year) + str(now.month).zfill(2) + str(now.day).zfill(2)	# 将日期转换为字段形式：20160101

	@classmethod
	def from_settings(cls, settings):
		# ==========从settings.py里获取mysql数据库信息，并定数据编码为utf-8，以免入库时出错
		dbargs = dict(
			host=settings['MYSQL_HOST'],		
			db=settings['MYSQL_DB'],
			user=settings['MYSQL_USER'],
			passwd=settings['MYSQL_PASS'],
			charset='utf8',
			use_unicode=True,
		)

		dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)
		return cls(dbpool)

	def process_item(self, item, spider):
		# ==========处理item
		for key, value in item.items():			# 用for循环去掉item字段里多余的空格。例如：“   养老院    ” = “养老院”
			item[key] = value.strip()

		if item.get('address','') != '':				# 如果item里有“address”字段，即判断为yanglao爬虫的item
			self.query = "insert IGNORE into `yl_"+self.add_date+"` (名称,地址,使用时间,床位,max收费,min收费,机构性质,占地面积,收住对象,设施,交通,机构类型,"\
				"服务内容,入住要求,网址,邮编,简介,省,市,区) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
			self.data = (item['name'],item['address'],item['since'],item['bed'],item['max_charge'],item['min_charge'],item['organization'],item['area'],\
				item['target'],item['facility'],item['transport'],item['category'],item['service'],item['notice'],item['website'],item['post'],item['intro'],\
				item['province'],item['city'],item['district'])
			
		elif item.get('administer_area','') != '':		# 如果item里有“administer_area”字段，即判断为baike爬虫的item
			self.query = "insert IGNORE into baike (中文名称,外文名称,行政区类别,所属地区,下辖地区,政府驻地,电话区号,邮政区码,地理位置,面积,人口,方言,气候条件,"\
				"著名景点,机场,火车站,功能划分,main_id,收入) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
			self.data = (item['chinese'],item['english'],item['category'],item['belong_to'],item['administer_area'],item['government_resident'],item['phone'],\
				item['post'],item['geography'],item['area'],item['population'],item['language'],item['weather'],item['famous_place'],item['airport'],\
				item['train_station'],item['functional_divition'],item['main_id'],item['income'])

		# run db query in the thread pool
		d = self.dbpool.runInteraction(self._do_upsert, item, spider)
		d.addErrback(self._handle_error, item, spider)
		# at the end return the item in case of success or failure
		d.addBoth(lambda _: item)
		# return the deferred instead the item. This makes the engine to
		# process next item (according to CONCURRENT_ITEMS setting) after this
		# operation (deferred) has finished.
		return d
		
	def _do_upsert(self, conn, item, spider):
		"""Perform an insert or update."""
		try:
			conn.execute(self.query,self.data)		# 执行mysql语句
		except Exception, e:
			print 'error========================================', e

	def _handle_error(self, failure, item, spider):
		"""Handle occurred on db interaction."""
		# do nothing, just log
		log.err(failure)

class HospPipeline(object):
	"""这里不用看得那么详细，只修改底下的MySQL语句就可以"""

	def __init__(self, dbpool):
		self.dbpool = dbpool
		now = datetime.now()
		self.add_date = str(now.year) + str(now.month).zfill(2) + str(now.day).zfill(2)

	@classmethod
	def from_settings(cls, settings):
		dbargs = dict(
			host=settings['MYSQL_HOST'],
			db=settings['MYSQL_DB'],
			user=settings['MYSQL_USER'],
			passwd=settings['MYSQL_PASS'],
			charset='utf8',
			use_unicode=True,
		)

		dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)
		return cls(dbpool)

	def process_item(self, item, spider):
		for key, value in item.items():
			item[key] = value.strip()

		if item.get('address','') != '':
			self.query = "insert IGNORE into `hosp_"+self.add_date+"` (名称,地址,电话,简介,描述,网站,等级,省,市,区) " \
				"values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
			self.data = (item['name'],item['address'],item['tel'],item['about'],item['description'],item['website'],\
				item['degree'],item['province'],item['city'],item['district'])
		# elif item.get('hosp_name','') != '':
		# 	self.query = "insert IGNORE into `hospdept_"+self.add_date+"` (医院名,主科,子科,人员) " \
		# 		"values (%s,%s,%s,%s)"
		# 	self.data = (item['hosp_name'],item['department'],item['sub_department'],item['worker'])
		elif item.get('hosp_name','') != '':
			self.query = "insert IGNORE into `hospdoc_"+self.add_date+"` (医院名,主科,子科,姓名,职称,主治项目,擅长,简介,专家团队,预约挂号,专业挂号,挂号功能,图文功能,电话功能,视频功能) " \
				"values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
			self.data = (item['hosp_name'],item['department'],item['sub_department'],item['name'],item['profession'],\
				item['fields'],item['specialty'],item['about'],item['group'],item['schedule'],item['pro_schedule'],item['register'],item['picture'],item['mobile'],item['video'])
		# run db query in the thread pool
		d = self.dbpool.runInteraction(self._do_upsert, item, spider)
		d.addErrback(self._handle_error, item, spider)
		# at the end return the item in case of success or failure
		d.addBoth(lambda _: item)
		# return the deferred instead the item. This makes the engine to
		# process next item (according to CONCURRENT_ITEMS setting) after this
		# operation (deferred) has finished.
		return d

	def _get_guid(self, item):
		"""Generates an unique identifier for a given item."""
		# hash based solely in the url field
		print md5(item['post_url']).hexdigest()
		
	def _do_upsert(self, conn, item, spider):
		"""Perform an insert or update."""
		# guid = self._get_guid(item)
		# conn.execute("""SELECT EXISTS(
		# 	SELECT 1 FROM dell WHERE file_url = %s and model = %s
		# )""", (item['file_urls'][0],item['model']))
		# ret = conn.fetchone()[0]

		# if not ret:
		try:
			conn.execute(self.query,self.data)

		except Exception, e:
			print 'error========================================', e
		# spider.log("Item stored in db: %r" % (item))

	def _handle_error(self, failure, item, spider):
		"""Handle occurred on db interaction."""
		# do nothing, just log
		log.err(failure)
