# -*- coding: utf-8 -*-
import scrapy


class A91160Spider(scrapy.Spider):
    name = "91160"
    allowed_domains = ["91160.com"]
    start_urls = (
        'http://www.91160.com/',
    )

    def parse(self, response):
        pass
