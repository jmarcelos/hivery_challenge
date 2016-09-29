import unittest
from coles import ColesSpider
from fake_response import coles_response

class TestColesSpider(unittest.TestCase):

    def test_get_drinks_homepages_urls(self):
        coles = ColesSpider('http://shop.coles.com.au/online/national/drinks')
        response = coles_response('drinks.html')
        urls = coles.get_homepages_url(response)
        self.assertEquals(len(urls), 10)
        self.assertEquals(urls[0], u'http://shop.coles.com.au/online/national/drinks/soft-drinks-3314551')
        self.assertEquals(urls[1], u'http://shop.coles.com.au/online/national/drinks/cordials')

    def test_get_products_url(self):
        coles = ColesSpider('http://shop.coles.com.au/online/national/drinks')
        response = coles_response('drinks_list.html')
        products_url = coles.get_products_url(response)
        self.assertEquals(len(products_url), 20)
        self.assertEquals(products_url[0], u'http://shop.coles.com.au/online/national/coca-cola-soft-drink-coke-375ml-cans-7365777p',)
        self.assertEquals(products_url[1], u'http://shop.coles.com.au/online/national/coca-cola-soft-drink-coke-zero-chilled')

    def test_get_products_url_pagination(self):
        coles = ColesSpider('http://shop.coles.com.au/online/national/drinks')
        response = coles_response('drinks_list.html')
        pagination_rule = coles.get_next_page(response)
        self.assertEquals(pagination_rule, u'#pageNumber=2&currentPageSize=20')
        



if __name__ == '__main__':
    unittest.main()




