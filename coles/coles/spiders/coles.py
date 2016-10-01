import sys
import os.path
import re
import scrapy
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from items import Product


class ColesSpider(scrapy.Spider):
    name = 'myspider'
    SEARCH_TOTAL_VALUES = 100
    

    def __init__(self, *args, **kwargs):
        super(ColesSpider, self).__init__(*args, **kwargs)
        self.start_urls = [kwargs.get('url')]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.yield_get_homepages_url)
 
    def get_product_detail(self, response):
        dirty_name = response.xpath('//div[@id="FBLikeDiv"]/@data-social').extract()[0] 
        regex = r"'(.*?)'"
        name  = re.findall(regex, dirty_name)[2] 

        brand = response.xpath('//div[@class="brand"]/text()').extract()[0]
        product_info = response.xpath('//div[@id="FBLikeDiv"]/@data-social').extract()[0]
        description = re.findall(regex, product_info)[3] or "Not Available"

        product_img = re.findall(regex, product_info)[0]
        
        url_friendly_name_dirty = re.findall(regex, product_info)[1]
        url_friendly_name = url_friendly_name_dirty.split('/')[-1]
        
        social_data= response.xpath('//div[@id="reviewsCommentsDiv"]/@data-social').extract()[0]
        product_id = re.findall(regex, social_data)[0]

        product = Product(name=name.rstrip(), brand=brand, description=description, url_friendly_name=url_friendly_name, product_img=product_img, id=product_id)
        return product

    def yield_get_search_page(self, response):
        search_url = self.get_search_url(response)
        yield scrapy.Request(url=search_url, callback=self.yield_get_products_url)


    def get_search_url(self, response):
        search_rules = '//div[@id="searchDisplay"]/@data-refresh'
        search_dirty_parameters = response.xpath(search_rules).extract()[0]
        order_by, begin_index, catalogId, categoryId = self.extract_search_parameters(search_dirty_parameters)
        search_url = self.generate_search_url(order_by, begin_index, catalogId, categoryId)
        return search_url 

    def extract_search_parameters(self, search_dirty_parameters):
        regex = r"'(.*?)'"
        order_by = re.findall(regex, search_dirty_parameters)[2] or ""
        begin_index = re.findall(regex, search_dirty_parameters)[3] or ""
        catalogId = re.findall(regex, search_dirty_parameters)[6]  or ""
        categoryId =  re.findall(regex, search_dirty_parameters)[7] or ""

        return order_by, begin_index, catalogId, categoryId


    def generate_search_url(self, order_by, begin_index, catalogId, categoryId):
        search_url = u'https://shop.coles.com.au/online/national/drinks/ColesCategoryView?orderBy={0}&productView=list&beginIndex={1}&pageSize={2}&catalogId={3}&storeId=10601&categoryId={4}&localisationState=2&serviceId=ColesCategoryView&langId=-1'.format(order_by, begin_index, self.SEARCH_TOTAL_VALUES, catalogId, categoryId)
        
        return search_url

    def yield_get_products_url(self, response):
        products_url, search_url = self.get_products_url(response)
        for url in products_url:
            yield scrapy.Request(url=url, callback=self.get_product_detail)
    
        if search_url:
            yield scrapy.Request(url=search_url, callback=self.yield_get_products_url)


    def get_products_url(self, response):
        url_rules = '//div[@class="outer-prod prodtile"]/@data-refresh'
        products = response.xpath(url_rules).extract()
        regex = r'"(.*?)"'
        products_url = []
        for product in products:
            url = re.findall(regex, product)[4]
            products_url.append(url)
       
        search_url = None
        if len(products) == self.SEARCH_TOTAL_VALUES:
            search_rules = '//div[@id="searchDisplay"]/@data-refresh'
            search_dirty_parameters_list = response.xpath(search_rules).extract()
            if len(search_dirty_parameters_list) > 0:
                search_dirty_parameters = search_dirty_parameters_list[0]
                order_by, begin_index, catalogId, categoryId = self.extract_search_parameters(search_dirty_parameters)
                search_url = self.generate_search_url(order_by, int(begin_index) + self.SEARCH_TOTAL_VALUES, catalogId, categoryId)

        return products_url, search_url

    def yield_get_homepages_url(self, response):
        urls = self.get_homepages_url(response)
        
        for url in urls:
            yield scrapy.Request(url=url, callback=self.yield_get_search_page)

    def get_homepages_url(self, response):
        url_rules = '//ul[@id="subnav"]/li/a/@href'
        urls = response.xpath(url_rules).extract()
        return urls 
