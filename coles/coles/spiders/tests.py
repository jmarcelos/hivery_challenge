# encoding: utf-8
import unittest
from coles import ColesSpider, ColesStoreLocatorSpider, ColesRegionLocator
from mocked_data import coles_response, get_product_details
import items


class TestColesSpider(unittest.TestCase):

    def test_get_drinks_homepages_urls(self):
        coles = ColesSpider(url='http://shop.coles.com.au/online/national/drinks')
        response = coles_response('drinks.html')
        urls = coles.get_homepages_url(response)
        self.assertEquals(len(urls), 10)
        self.assertEquals(urls[0], u'http://shop.coles.com.au/online/national/drinks/soft-drinks-3314551')
        self.assertEquals(urls[1], u'http://shop.coles.com.au/online/national/drinks/cordials')

    def test_get_product_url_list(self):
        coles = ColesSpider(url='http://shop.coles.com.au/online/national/drinks')
        response = coles_response('drinks_list.html')
        products_url, search_url = coles.get_products_url(response)
        self.assertEquals(len(products_url), 20)
        self.assertEquals(products_url[0], u'http://shop.coles.com.au/online/national/coca-cola-soft-drink-coke-375ml-cans-7365777p',)
        self.assertEquals(products_url[1], u'http://shop.coles.com.au/online/national/coca-cola-soft-drink-coke-zero-chilled')

    def test_get_search_url(self):
        coles = ColesSpider(url='http://shop.coles.com.au')
        search_url = coles.generate_search_url(1,2,3,4)
        response = coles_response('drinks_list.html')
        url = coles.get_search_url(response)
        expected_url = "https://shop.coles.com.au/online/national/drinks/ColesCategoryView?orderBy=10601_6&productView=list&beginIndex=0&pageSize=100&catalogId=10576&storeId=10601&categoryId=3314551&localisationState=2&serviceId=ColesCategoryView&langId=-1"
        self.assertEquals(url, expected_url)    
   
    def test_searh_url_none_end_of_page(self):
        pass

    def test_generate_search_url(self):
        coles = ColesSpider(url='http://shop.coles.com.au')
        search_url = coles.generate_search_url(1,2,3,4)
        expected_url = u'https://shop.coles.com.au/online/national/drinks/ColesCategoryView?orderBy=1&productView=list&beginIndex=2&pageSize=100&catalogId=3&storeId=10601&categoryId=4&localisationState=2&serviceId=ColesCategoryView&langId=-1'
        self.assertEquals(search_url, expected_url)

    def test_extract_search_parameters(self):
        coles = ColesSpider(url='http://shop.coles.com.au')
        search_dirty_parameters = u"{refreshId:'searchView', productView:'list', orderBy:'10601_6', beginIndex:'0', pageSize:'20', storeId:'10601', catalogId:'10576', categoryId:'3314551',topcategoryId:'',browseView:'true'}"
        
        order_by, begin_index, catalogId, categoryId = coles.extract_search_parameters(search_dirty_parameters)

        self.assertEquals(order_by, '10601_6')
        self.assertEquals(begin_index, '0')
        self.assertEquals(catalogId, '10576')
        self.assertEquals(categoryId, '3314551')


    #def test_get_products_url_with_new_page(self):
    #    coles = ColesSpider(url='http://shop.coles.com.au/online/national/drinks')
    #    response = coles_response('drinks_list.html')
    #    products_url, new_page = coles.get_products_url(response)
    #    self.assertEquals(len(products_url), 20)
    #    self.assertEquals(products_url[0], u'http://shop.coles.com.au/online/national/coca-cola-soft-drink-coke-375ml-cans-7365777p',)
    #    self.assertEquals(products_url[1], u'http://shop.coles.com.au/online/national/coca-cola-soft-drink-coke-zero-chilled')
    #    self.assertTrue(u'#pageNumber=2&currentPageSize=20' in new_page)


    #def test_get_products_url_pagination(self):
    #    coles = ColesSpider(url='http://shop.coles.com.au/online/national/drinks')
    #    response = coles_response('drinks_list.html')
    #    pagination_rule = coles.get_next_page(response)
    #    self.assertEquals(pagination_rule, u'#pageNumber=2&currentPageSize=20')

    def test_get_product_detail(self):
        coles = ColesSpider(url='http://shop.coles.com.au/online/national/drinks')
        response = coles_response('product-detail-beer.html')
        product = coles.get_product_detail(response)
        self.assertEquals(product['name'], u'Birell Ultra Light Beer')
        self.assertEquals(product["brand"], u'Birell')


class TestColesRegionLocator(unittest.TestCase):

    def test_coles_url_starters(self):
        coles_region = ColesRegionLocator(areas= [3182, 2010, 6160])
        self.assertEquals(len(coles_region.start_urls), 3)
    
    def test_get_31_post_code(self):
        coles_region = ColesRegionLocator(areas= [3182])
        response = coles_response('store-regions.json')
        regions = coles_region.generate_regions(response)
        regions = regions.next()
        self.assertEquals(len(regions['autoSuggestSearchResults']), 3)

class TestColesStoreLocator(unittest.TestCase):

    def test_QLD_stores(self):
        coles_stores = ColesStoreLocatorSpider(url='https://www.coles.com.au/storelocator/api/getAllStoreList', state='QLD')
        response = coles_response('store-QLD.json')
        stores = coles_stores.get_stores(response)
        stores = stores.next()
        self.assertEquals(len(stores['storesList']), 161)


if __name__ == '__main__':
    unittest.main()




