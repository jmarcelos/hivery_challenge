import sys
import os
import os.path
import re
import json
import scrapy
from selenium import webdriver
from scrapper.coles.items import Product, Region, PriceRegion

import scrapper.coles.settings

class ColesSpider(scrapy.Spider):
    
    name = 'coles_general_spider'
    SEARCH_TOTAL_VALUES = 20
    

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
        next_rules = '//li[@class="next"]'
        has_next = len(response.xpath(next_rules).extract()) > 0 or False
        if has_next:
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


class ColesPriceRegion(scrapy.Spider):

    name = 'coles_price_region'
   
    
    def __init__(self, *args, **kwargs):
        super(ColesPriceRegion, self).__init__(*args, **kwargs)
        urls = kwargs.get('url')
        self.start_urls = urls.split(',')
        postcode = kwargs.get('postcode')
        self.driver = self.get_driver_conf() 
        
        #self.start_urls = [self.url.format(area) for area in search_areas]

    def get_driver_conf(self):
        #chromedriver = 'CHROME_DRIVE_LOCATION'
        #os.environ["webdriver.chrome.driver"] = chromedriver
        #driver = webdriver.Chrome(chromedriver)
        driver = None
        return driver

    def start_requests(self):
        pass

    def get_product_price_info(self, response):
        price_region = PriceRegion(price=100, postcode=3182)
        prices = [price_region]
        product = Product(id = 84624, prices_region = prices)
        return product

class ColesRegionLocator(scrapy.Spider):
    
    name = "coles_region"
    url = u'https://shop.coles.com.au/online/national/COLAjaxAutoSuggestCmd?searchTerm={}&expectedType=json-comment-filtered&serviceId=COLAjaxAutoSuggestCmd'


    def __init__(self, *args, **kwargs):
        super(ColesRegionLocator, self).__init__(*args, **kwargs)
        areas = kwargs.get('areas')
        search_areas = areas.split(',')
        self.start_urls = [self.url.format(area) for area in search_areas]

    def start_requests(self):
        for url in self.start_urls:
            print('scrapeando url {}'.format(url))
            yield scrapy.Request(url=url, callback=self.generate_regions)

    def generate_regions(self, response):
        dirty_json = re.sub('\s+', '', response.body)        
        regions_string = dirty_json[2:-2]
        regions = json.loads(regions_string)
        
        suggestions = regions['autoSuggestSearchResults']
        new_regions = []
        
        for suggestion in suggestions:
            region = Region()
            region['state'] = suggestion['state']
            region['score'] = suggestion['score']
            region['collectionpoint'] = suggestion['collectionpoint']
            region['suburb'] = suggestion['suburb']
            region['country'] = suggestion['country']
            region['zoneid'] = suggestion['zoneid']
            region['webstoreid'] = suggestion['webstoreid']
            region['lon'] = suggestion['lon']
            region['id'] = suggestion['id']
            region['postcode'] = suggestion['postcode']
            region['lat'] = suggestion['lat']
            region['servicetype'] = suggestion['servicetype']
            new_regions.append(region)

        return new_regions


class ColesStoreLocatorSpider(scrapy.Spider):
    name = "coles_stores"

    def __init__(self, *args, **kwargs):
        super(ColesStoreLocatorSpider, self).__init__(*args, **kwargs)
        parameters = ''
        if kwargs.get('state') is None or kwargs.get('state') is "":
            parameters = u'?statename={0}'.format(kwargs.get('state'))
        
        self.start_urls = [kwargs.get('url') + parameters]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.yield_get_homepages_url)


    def get_stores(self, response):
        yield json.loads(response.body[1:-1])

