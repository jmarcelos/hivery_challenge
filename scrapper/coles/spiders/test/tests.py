# encoding: utf-8
import unittest
from scrapper.coles.spiders.coles import ColesSpider, ColesStoreLocatorSpider, ColesRegionLocator, ColesPriceRegion
from mocked_data import coles_response, get_product_details
import scrapper.coles.items


class TestColesSpider(unittest.TestCase):

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
        product = coles.get_product_detail(response)
        self.assertEquals(product['name'], u'Birell Ultra Light Beer')
        self.assertEquals(product["brand"], u'Birell')


class TestColesPriceRegion(unittest.TestCase):

    def test_get_price_based_on_store(self):
        postcode = '3182'
        url = 'http://shop.coles.com.au/online/national/birell-ultra-light-beer'
        
        coles_price = ColesPriceRegion(url=url, postcode=postcode)
        response = coles_response('fixtures/product-detail-beer-3182.html')
        product = coles_price.get_product_price_info(response)

        self.assertEquals(product['id'], 84624)
        self.assertEquals(product['prices_region'][0]['postcode'], 3182)
        self.assertEquals(product['prices_region'][0]['price'], 100)
        
class TestColesRegionLocator(unittest.TestCase):

    def test_coles_url_starters(self):
        coles_region = ColesRegionLocator(areas= '3182,2010,6160')
        self.assertEquals(len(coles_region.start_urls), 3)
        self.assertEquals(coles_region.start_urls[0], u'https://shop.coles.com.au/online/national/COLAjaxAutoSuggestCmd?searchTerm=3182&expectedType=json-comment-filtered&serviceId=COLAjaxAutoSuggestCmd')


    def test_get_3182_post_code(self):
        coles_region = ColesRegionLocator(areas= '3182')
        response = coles_response('fixtures/store-regions.json')
        regions = coles_region.generate_regions(response)

        self.assertEquals(len(regions), 3)
        self.assertEquals(regions[0]['zoneid'], u'0645HD')
        self.assertEquals(regions[1]['zoneid'], u'0482HD')
        self.assertEquals(regions[2]['zoneid'], u'0482HD')

class TestColesStoreLocator(unittest.TestCase):

    def test_QLD_stores(self):
        coles_stores = ColesStoreLocatorSpider(url='https://www.coles.com.au/storelocator/api/getAllStoreList', state='QLD')
        response = coles_response('fixtures/store-QLD.json')
        stores = coles_stores.get_stores(response)
        stores = stores.next()
        self.assertEquals(len(stores['storesList']), 161)


if __name__ == '__main__':
    unittest.main()




