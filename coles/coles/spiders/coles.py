import sys
import os.path
import re
import scrapy
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from items import Product


class ColesSpider(scrapy.Spider):
    name = 'myspider'

    def __init__(self, *args, **kwargs):
        super(ColesSpider, self).__init__(*args, **kwargs)
        self.urls = [kwargs.get('url')]

    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.get_homepages_url)
 
    def get_product_detail(self, response):
        dirty_name = response.xpath('//div[@id="FBLikeDiv"]/@data-social').extract()[0] 
        regex = r"'(.*?)'"
        name  = re.findall(regex, dirty_name)[2]
        brand = response.xpath('//div[@class="brand"]/text()').extract()[0]
        product = Product(name=name.rstrip(), brand=brand)
        
        return product

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
    
    
    def get_products_details(self, urls):
        return json.loads("""[
          {
                   "name": "Cocobella Coconut Water & Mango",
                            "brand": "xxxx",
                                     "url_friendly_name": "cocobella-coconut-water-mango",
                                              "rich_description": "coconut water is a water from young green coconuts and is naturally rich in 5 key electrolytes making it a great source of natural hydration."
                                                },
                                                  {
                                                           "name": "Cocobella Coconut Water & Mango",
                                                                    "brand": "xxxx",
                                                                             "url_friendly_name": "cocobella-coconut-water-mango",
                                                                                      "rich_description": "coconut water is a water from young green coconuts and is naturally rich in 5 key electrolytes making it a great source of natural hydration."
                                                                                        },
                                                                                          {
                                                                                                   "name": "Cocobella Coconut Water & Mango",
                                                                                                            "brand": "xxxx",
                                                                                                                     "url_friendly_name": "cocobella-coconut-water-mango",
                                                                                                                              "rich_description": "coconut water is a water from young green coconuts and is naturally rich in 5 key electrolytes making it a great source of natural hydration."
                                                                                                                                }
                                                                                                                                ]""")
