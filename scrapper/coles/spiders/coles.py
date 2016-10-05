import sys
import os
import re
import json
import scrapy
from selenium import webdriver
from scrapper.coles.items import Product, Region, PriceRegion
from scrapy.utils.project import get_project_settings

class ColesSpider(scrapy.Spider):
    
    name = 'coles_general_spider'
    SEARCH_TOTAL_VALUES = 20
    regions = []

    def __init__(self, *args, **kwargs):
        super(ColesSpider, self).__init__(*args, **kwargs)
        self.start_urls = [kwargs.get('url')]
        dirty_postcodes = kwargs.get('postcode') or ""
        self.postcodes = dirty_postcodes.split(',')
    
    def start_requests(self):

        for postcode in self.postcodes:
            url = u'https://shop.coles.com.au/online/national/COLAjaxAutoSuggestCmd?searchTerm={0}&expectedType=json-comment-filtered&serviceId=COLAjaxAutoSuggestCmd'.format(postcode)
            yield scrapy.Request(url=url, callback=self.get_region)

        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.yield_get_homepages_url)
 
    def get_product_detail(self, response):
        dirty_name = response.xpath('//div[@id="FBLikeDiv"]/@data-social').extract()[0] 
        regex = r"'(.*?)'"
        name  = re.findall(regex, dirty_name)[2] 
        brand = response.xpath('//div[@class="brand"]/text()').extract()[0]
        product_info = response.xpath('//div[@id="FBLikeDiv"]/@data-social').extract()[0]
        redirect_url = response.xpath('//form [@action="COLLocalisationControllerCmd"]/input[@name="fullURLHttps"]/@value').extract()[0]

        info = response.xpath('//div[@class="plain-box product-detail-left"]/p/text()').extract()
        ingredients = info[0]
        allergen = info[1]
        servings_per_pack = info[2] 
        serving_size = info[3]
        retail_limit = info[4]
        size = info[5]


        description = re.findall(regex, product_info)[3] or "Not Available"
        product_img = re.findall(regex, product_info)[0]
        url_friendly_name_dirty = re.findall(regex, product_info)[1]
        url_friendly_name = url_friendly_name_dirty.split('/')[-1]
        social_data= response.xpath('//div[@id="reviewsCommentsDiv"]/@data-social').extract()[0]
        product_id = re.findall(regex, social_data)[0]

        dirty_data = response.xpath('//div[@class="prodtile"]/form/div/@data-refresh').extract()[0]
        data  = re.sub('\s+', '', dirty_data)
        regex = r'"(.*?)"'
        price_type = re.findall(regex, data)[9]
    
        general_price = response.xpath('//div[@class="purchasing"]/div[@class="price"]/text()').extract()

        product = Product(name=name.rstrip(), brand=brand, description=description, ingredients=ingredients, allergen=allergen, 
                            servings_per_pack=servings_per_pack, size=size, retail_limit=retail_limit, serving_size=serving_size, 
                            url_friendly_name=url_friendly_name, product_img=product_img, id=product_id, general_price=general_price,
                            redirect_url=redirect_url, price_type=price_type, prices_region = [])
    
        for region in self.regions:
            product = self.get_product_price_region(region, product)
        
        return product


    def get_region(self, response):
        dirty_json = re.sub('\s+', '', response.body)        
        regions_string = dirty_json[2:-2]
        regions = json.loads(regions_string)
        suggestions = regions['autoSuggestSearchResults']
        
        #getting only the first store of the region
        suggestion =  suggestions[0]
        region = Region()
        region['state'] = suggestion['state']
        region['score'] = suggestion['score']
        region['collectionpoint'] = suggestion['collectionpoint']
        region['suburb'] = suggestion['suburb']
        region['country'] = suggestion['country']
        region['zone_id'] = suggestion['zoneid']
        region['webstore_id'] = suggestion['webstoreid']
        region['lon'] = suggestion['lon']
        region['id'] = suggestion['id']
        region['postcode'] = suggestion['postcode']
        region['lat'] = suggestion['lat']
        region['service_type'] = suggestion['servicetype']
   
        self.regions.append(region)

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

    def get_product_price_region(self, region, product):
        url=self.get_price_per_region_url(region, product)
        driver = self.get_driver()
        driver.get(url)
        price = driver.find_element_by_xpath('//strong[@class="product-price"]').text
        price_region = PriceRegion(price=price, postcode=region['postcode'])
        product['prices_region'].append(price_region)
        return product 

    def get_price_per_region_url(self, region, product):
        try:
            url = 'https://shop.coles.com.au/online/COLLocalisationControllerCmd'
            params= "redirectUrl={0}&suburbPostCodeId={1}&serviceType={2}&externalffmcId={3}&state={4}&score={5}&collectionpoint={6}&suburb={7}&zoneid={8}&postcode={9}&longitude={10}&latitude={11}&storeId=10601".format(
                  product['redirect_url'],region['id'],
                  region['service_type'],region['webstore_id'],
                  region['state'],region['score'],region['collectionpoint'],
                  region['suburb'],region['zone_id'],region['postcode'],
                  region['lon'],region['lat'])
            final_url = url + '?' + params
            return final_url
        except: 
             print('Not possible to retrieve information from product {0} region {1}'.format(product, region))

    def get_driver(self):
        chromedriver = get_project_settings()['CHROME_DRIVE_LOCATION']
        os.environ["webdriver.chrome.driver"] = chromedriver
        driver = webdriver.Chrome(chromedriver)
        #driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true', '--ssl-protocol=TLSv1'])
        return driver

