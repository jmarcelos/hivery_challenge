import re
import scrapy

class ColesSpider(scrapy.Spider):
    name = 'myspider'

    def __init__(self, *args, **kwargs):
        super(ColesSpider, self).__init__(*args, **kwargs)
        self.urls = [kwargs.get('url')]

    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.get_homepages_url)
   

    def get_products_url(self, response):
        url_rules = '//div[@class="outer-prod prodtile"]/@data-refresh'
        products = response.xpath(url_rules).extract()
        regex = r'"(.*?)"'
        products_url = []

        for product in products:
            url = re.findall(regex, product)[4]
            products_url.append(url)
        
        return products_url
       
    def get_next_page(self, response):
        pagination_rule = '//ul[@class="navigator"]/li[@class="next"]/a/@href'
        pagination = response.xpath(pagination_rule).extract()
        
        return pagination[0]

    def get_homepages_url(self, response):
        url_rules = '//ul[@id="subnav"]/li/a/@href'
        urls = response.xpath(url_rules).extract()
        return urls 
