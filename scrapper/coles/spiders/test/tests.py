# encoding: utf-8
import unittest
import os
from scrapper.coles.spiders.coles import ColesSpider
from scrapy.settings import Settings
from mocked_data import coles_response, get_product_details
from scrapper.coles.items import Product, Region

class TestColesSpider(unittest.TestCase):

    def setUp(self):
        settings = Settings()
        os.environ['SCRAPY_SETTINGS_MODULE'] = 'scrapper.coles.settings'
        settings_module_path = os.environ['SCRAPY_SETTINGS_MODULE']
        settings.setmodule(settings_module_path, priority='project')
    
    def test_get_drinks_homepages_urls(self):
        coles = ColesSpider(url='http://shop.coles.com.au/online/national/drinks')
        response = coles_response('fixtures/drinks.html')
        urls = coles.get_homepages_url(response)
        self.assertEquals(len(urls), 10)
        self.assertEquals(urls[0], u'http://shop.coles.com.au/online/national/drinks/soft-drinks-3314551')
        self.assertEquals(urls[1], u'http://shop.coles.com.au/online/national/drinks/cordials')

    def test_get_product_url_list(self):
        coles = ColesSpider(url='http://shop.coles.com.au/online/national/drinks')
        response = coles_response('fixtures/drinks_list.html')
        products_url, search_url = coles.get_products_url(response)
        self.assertEquals(len(products_url), 20)
        self.assertEquals(products_url[0], u'http://shop.coles.com.au/online/national/coca-cola-soft-drink-coke-375ml-cans-7365777p',)
        self.assertEquals(products_url[1], u'http://shop.coles.com.au/online/national/coca-cola-soft-drink-coke-zero-chilled')

    def test_get_search_url(self):
        coles = ColesSpider(url='http://shop.coles.com.au')
        search_url = coles.generate_search_url(1,2,3,4)
        response = coles_response('fixtures/drinks_list.html')
        url = coles.get_search_url(response)
        expected_url = "https://shop.coles.com.au/online/national/drinks/ColesCategoryView?orderBy=10601_6&productView=list&beginIndex=0&pageSize=20&catalogId=10576&storeId=10601&categoryId=3314551&localisationState=2&serviceId=ColesCategoryView&langId=-1"
        self.assertEquals(url, expected_url)    

    def test_generate_search_url(self):
        coles = ColesSpider(url='http://shop.coles.com.au')
        search_url = coles.generate_search_url(1,2,3,4)
        expected_url = u'https://shop.coles.com.au/online/national/drinks/ColesCategoryView?orderBy=1&productView=list&beginIndex=2&pageSize=20&catalogId=3&storeId=10601&categoryId=4&localisationState=2&serviceId=ColesCategoryView&langId=-1'
        self.assertEquals(search_url, expected_url)

    def test_extract_search_parameters(self):
        coles = ColesSpider(url='http://shop.coles.com.au')
        search_dirty_parameters = u"{refreshId:'searchView', productView:'list', orderBy:'10601_6', beginIndex:'0', pageSize:'20', storeId:'10601', catalogId:'10576', categoryId:'3314551',topcategoryId:'',browseView:'true'}"
        
        order_by, begin_index, catalogId, categoryId = coles.extract_search_parameters(search_dirty_parameters)

        self.assertEquals(order_by, '10601_6')
        self.assertEquals(begin_index, '0')
        self.assertEquals(catalogId, '10576')
        self.assertEquals(categoryId, '3314551')

    def test_get_products_and_next_page(self):
        coles = ColesSpider(url='http://shop.coles.com.au/online/national/drinks')
        response = coles_response('fixtures/page-with-next.html')
        products_url, search_url = coles.get_products_url(response)

        self.assertEquals(len(products_url), 20)
        self.assertEquals(products_url[0], u'http://shop.coles.com.au/online/national/coca-cola-coke-zero-soft-drink-bottle')
        self.assertEquals(products_url[1], u'http://shop.coles.com.au/online/national/coca-cola-diet-coke')
        self.assertTrue("beginIndex=220" in search_url)


    def test_get_products_without_next_page(self):
        coles = ColesSpider(url='http://shop.coles.com.au/online/national/drinks')
        response = coles_response('fixtures/page-without-next.html')
        products_url, search_url = coles.get_products_url(response)

        self.assertEquals(len(products_url), 0)
        self.assertEquals(search_url, None)

    def test_get_product_detail(self):
        coles = ColesSpider(url='http://shop.coles.com.au/online/national/drinks')
        response = coles_response('fixtures/product-detail-beer.html')
        region = Region(state='VIC', score='8.029414', collectionpoint='',
                suburb='ST KILDA SOUTH', country='AU', zone_id= '0645HD',
                lon='144.98116', lat='-37.872868', service_type='HD', 
                postcode='3182', webstore_id='0645', id='14854')
        coles.regions = [] 
        product = coles.get_product_detail(response)
        expected_info = {u'Contains Barley': u'Allergen:', u'Malted barley, hops, yeast and water.': u'Ingredients:', u'20': u'Size:', u'375ml': u'Serving Size:', u'1.0': u'Servings Per Pack:', u'* Percentage Daily Intake per serving. Percentage Daily Intakes are based on an average adult diet of 8700 kJ. Your daily intakes may be higher or lower depending on your energy needs.': u'Retail Limit:'}

        self.assertEquals(product['name'], u'Birell Ultra Light Beer')
        self.assertEquals(product["brand"], u'Birell')
        self.assertEquals(product["general_price"], u'8.25')
        self.assertEquals(product["brand"], u'Birell')
        self.assertEquals(product['info'], expected_info)
        self.assertEquals(product['redirect_url'], u'https://shop.coles.com.au/webapp/wcs/stores/servlet/national/birell-ultra-light-beer')

    def test_get_product_price_per_region_same_price(self):
        coles = ColesSpider(url='http://shop.coles.com.au/online/national/drinks')
        product = Product(id=84624, general_price=u'10.00', has_price_difference=False, redirect_url = 'http://shop.coles.com.au/webapp/wcs/stores/servlet/national/pepsi-max-soft-drink-cola-375ml-cans-7366022p', prices_region= [])
        region = Region(state='VIC', score='8.029414', collectionpoint='',
                suburb='ST KILDA SOUTH', country='AU', zone_id= '0645HD',
                lon='144.98116', lat='-37.872868', service_type='HD', 
                postcode='3182', webstore_id='0645', id='14854')
        product = coles.get_product_price_region(region, product)
        product = coles.get_product_price_region(region, product)
        
        self.assertEquals(product['id'], 84624)
        self.assertFalse(product['has_price_difference'])
        self.assertEquals(product['prices_region'][0]['postcode'], '3182')
        self.assertEquals(product['prices_region'][0]['postcode'], '3182')
        self.assertEquals(product['prices_region'][1]['price'], '$14.00')
        self.assertEquals(product['prices_region'][1]['price'], '$14.00')
    
    def test_get_product_price_per_region(self):
        coles = ColesSpider(url='http://shop.coles.com.au/online/national/drinks')
        product = Product(id=84624, general_price=u'10.00', has_price_difference=False, redirect_url = 'http://shop.coles.com.au/webapp/wcs/stores/servlet/national/pepsi-max-soft-drink-cola-375ml-cans-7366022p', prices_region= [])
        region = Region(state='VIC', score='8.029414', collectionpoint='',
                suburb='ST KILDA SOUTH', country='AU', zone_id= '0645HD',
                lon='144.98116', lat='-37.872868', service_type='HD', 
                postcode='3182', webstore_id='0645', id='14854')
        product = coles.get_product_price_region(region, product)
        product = coles.get_product_price_region(region, product)
        
        self.assertEquals(product['id'], 84624)
        self.assertEquals(product['prices_region'][0]['postcode'], '3182')
        self.assertEquals(product['prices_region'][0]['postcode'], '3182')
        self.assertEquals(product['prices_region'][1]['price'], '$14.00')
        self.assertEquals(product['prices_region'][1]['price'], '$14.00')

    def test_generate_price_region_url(self):
        coles = ColesSpider(url='http://shop.coles.com.au/online/national/drinks')
        product = Product(redirect_url=u'http://shop.coles.com.au/webapp/wcs/stores/servlet/national/pepsi-max-soft-drink-cola-375ml-cans-7366022p')
        region = Region(state='VIC', score='8.029414', collectionpoint='',
                suburb='ST KILDA SOUTH', country='AU', zone_id= '0645HD',
                lon='144.98116', lat='-37.872868', service_type='HD', 
                postcode='3182', webstore_id='0645', id='14854')
        price_region_url = coles.get_price_per_region_url(region, product)
        expected_url = u'https://shop.coles.com.au/online/COLLocalisationControllerCmd?redirectUrl=http://shop.coles.com.au/webapp/wcs/stores/servlet/national/pepsi-max-soft-drink-cola-375ml-cans-7366022p&suburbPostCodeId=14854&serviceType=HD&externalffmcId=0645&state=VIC&score=8.029414&collectionpoint=&suburb=ST KILDA SOUTH&zoneid=0645HD&postcode=3182&longitude=144.98116&latitude=-37.872868&storeId=10601'
        
        self.assertEquals(price_region_url, expected_url)

    def test_get_region(self):
        coles_region = ColesSpider(postcodes= '3182')
        response = coles_response('fixtures/store-regions.json')
        coles_region.get_region(response)

        self.assertEquals(coles_region.regions[0]['zone_id'], u'0645HD')
        self.assertEquals(coles_region.regions[0]['postcode'], u'3182')
        self.assertEquals(coles_region.regions[0]['webstore_id'], u'0645')


if __name__ == '__main__':
    unittest.main()




