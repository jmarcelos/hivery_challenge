import os
import re
import json
import logging
import scrapy
from selenium import webdriver
from scrapper.coles.items import Product, Region, PriceRegion
from scrapy.utils.project import get_project_settings

class ColesSpider(scrapy.Spider):

    name = 'coles_general_spider'
    _search_total_values = 20
    regions = []
    _regex_double_quote = r'"(.*?)"'
    _regex_sigle_quote = r"'(.*?)'"
    _url_region = u'https://shop.coles.com.au/online/national/COLAjaxAutoSuggestCmd?searchTerm={0}&expectedType=json-comment-filtered&serviceId=COLAjaxAutoSuggestCmd'
    _search_url = u'https://shop.coles.com.au/online/national/drinks/ColesCategoryView?orderBy={0}&productView=list&beginIndex={1}&pageSize={2}&catalogId={3}&storeId=10601&categoryId={4}&localisationState=2&serviceId=ColesCategoryView&langId=-1'
    _url_price_region = u'https://shop.coles.com.au/online/COLLocalisationControllerCmd'
    _params_price_region = u"redirectUrl={0}&suburbPostCodeId={1}&serviceType={2}&externalffmcId={3}&state={4}&score={5}&collectionpoint={6}&suburb={7}&zoneid={8}&postcode={9}&longitude={10}&latitude={11}&storeId=10601"


    def __init__(self, *args, **kwargs):
        super(ColesSpider, self).__init__(*args, **kwargs)
        
        self.start_urls = [kwargs.get('url')]
        dirty_postcodes = kwargs.get('postcode') or ""
        self.postcodes = dirty_postcodes.split(',')
        
        if self.start_urls is None or self.start_urls is "":
            raise ValueError("start url was not defined")

    def start_requests(self):

        for postcode in self.postcodes:
            url = self._url_region.format(postcode)
            yield scrapy.Request(url=url, callback=self._get_region)

        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.yield_get_homepages_url)



    def yield_get_search_page(self, response):
        search_url = self._get_search_url(response)
        
        yield scrapy.Request(url=search_url, callback=self.yield_get_products_url)

    def yield_get_products_url(self, response):
        products_url, search_url = self.get_products_url(response)
        for url in products_url:
            yield scrapy.Request(url=url, callback=self._get_product_detail)
    
        if search_url:
            yield scrapy.Request(url=search_url, callback=self.yield_get_products_url)

    def yield_get_homepages_url(self, response):
        urls = self._get_homepages_url(response)
        
        for url in urls:
            yield scrapy.Request(url=url, callback=self.yield_get_search_page)

    def _get_product_detail(self, response):
        try:
            dirty_name = response.xpath('//div[@id="FBLikeDiv"]/@data-social').extract()[0] 
            regex = r"'(.*?)'"
            name = re.findall(regex, dirty_name)[2] 
            brand = response.xpath('//div[@class="brand"]/text()').extract()[0]
            product_info = response.xpath('//div[@id="FBLikeDiv"]/@data-social').extract()[0]
            redirect_url = response.xpath('//form [@action="COLLocalisationControllerCmd"]/input[@name="fullURLHttps"]/@value').extract()[0]

            info_answer = response.xpath('//div[@class="plain-box product-detail-left"]/p/text()').extract()
            info_question = response.xpath('//div[@class="plain-box product-detail-left"]/h2/text()').extract()
            info = dict(zip(info_question, info_answer))

            description = re.findall(regex, product_info)[3] or "Not Available"
            product_img = re.findall(regex, product_info)[0]
            url_friendly_name_dirty = re.findall(regex, product_info)[1]
            url_friendly_name = url_friendly_name_dirty.split('/')[-1]
            social_data = response.xpath('//div[@id="reviewsCommentsDiv"]/@data-social').extract()[0]
            product_id = re.findall(regex, social_data)[0]

            dirty_data = response.xpath('//div[@class="prodtile"]/form/div/@data-refresh').extract()[0]
            data = re.sub('\s+', '', dirty_data)
            regex = r'"(.*?)"'
            price_type = re.findall(regex, data)[9]

            general_price = response.xpath('//div[@class="purchasing"]/div[@class="price"]/text()').extract()[0]

            product = Product(name=name.rstrip(), brand=brand, description=description, info=info,
                    url_friendly_name=url_friendly_name, product_img=product_img, 
                    id=product_id, general_price=general_price,redirect_url=redirect_url,
                    price_type=price_type, prices_region=[], has_price_difference=False)

            for region in self.regions:
                product = self._get_product_price_region(region, product)
            
            return product
        
        except:
            logging.debug("Not possible to crawl product under url {}".format(response.url))

    def _extract_search_parameters(self, search_dirty_parameters):
        order_by = re.findall(self._regex_sigle_quote, search_dirty_parameters)[2] or ""
        begin_index = re.findall(self._regex_sigle_quote, search_dirty_parameters)[3] or ""
        catalog_id = re.findall(self._regex_sigle_quote, search_dirty_parameters)[6]  or ""
        category_id = re.findall(self._regex_sigle_quote, search_dirty_parameters)[7] or ""

        return order_by, begin_index, catalog_id, category_id

    def _get_region(self, response):
        dirty_json = re.sub('\s+', '', response.body)        
        regions_string = dirty_json[2:-2]
        regions = json.loads(regions_string)
        suggestions = regions['autoSuggestSearchResults']
        
        #getting only the first store of the region
        suggestion = suggestions[0]
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

    def get_products_url(self, response):
        url_rules = '//div[@class="outer-prod prodtile"]/@data-refresh'
        products = response.xpath(url_rules).extract()
        
        products_url = []
        for product in products:
            url = re.findall(self._regex_double_quote, product)[4]
            products_url.append(url)
       
        search_url = None
        next_rules = '//li[@class="next"]'
        
        if len(response.xpath(next_rules).extract()):
           search_url = self._get_search_url(response)
        return products_url, search_url

    def _get_search_url(self, response):
        search_url = ''
        search_rules = '//div[@id="searchDisplay"]/@data-refresh'
        search_dirty_parameters_list = response.xpath(search_rules)
        if len(search_dirty_parameters_list) > 0:
            search_dirty_parameters = search_dirty_parameters_list.extract()[0]
            order_by, begin_index, catalog_id, category_id = self._extract_search_parameters(search_dirty_parameters)
            search_url = self._search_url.format(order_by, begin_index, self._search_total_values, catalog_id, category_id)
    
        return search_url 
    

    def _get_homepages_url(self, response):
        url_rules = '//ul[@id="subnav"]/li/a/@href'
        urls = response.xpath(url_rules).extract()
        return urls

    def _get_price_region(self, url):
        driver = self._get_driver()
        driver.get(url)
        price = driver.find_element_by_xpath('//strong[@class="product-price"]').text
        
        return price

    def _get_product_price_region(self, region, product):
        url = self._get_price_per_region_url(region, product)
        price = self._get_price_region(url)
        
        #just update flag if there is no price difference
        if  not product['has_price_difference']:
            product['has_price_difference'] = product['general_price'] == price
        
        price_region = PriceRegion(price=price, postcode=region['postcode'])
        product['prices_region'].append(price_region)
        return product 

    def _get_price_per_region_url(self, region, product):
        try:
            params = self._params_price_region.format(product['redirect_url'], region['id'],
                    region['service_type'], region['webstore_id'], region['state'], region['score'], region['collectionpoint'],
                    region['suburb'], region['zone_id'], region['postcode'], region['lon'], region['lat'])
           
            final_url = self._url_price_region + '?' + params
            
            return final_url
        
        except: 
             print 'Not possible to retrieve information from product {0} region {1}'.format(product, region)

    def _get_driver(self):
        chromedriver = get_project_settings()['CHROME_DRIVE_LOCATION']
        os.environ["webdriver.chrome.driver"] = chromedriver
        driver = webdriver.Chrome(chromedriver)
        #driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true', '--ssl-protocol=TLSv1'])
        
        return driver
