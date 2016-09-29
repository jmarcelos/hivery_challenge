import scrapy


class ColesSpider(scrapy.Spider):
    name = 'myspider'

    def __init__(self, *args, **kwargs):
        super(ColesSpider, self).__init__(*args, **kwargs)
        self.urls = [kwargs.get('url')]

    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.get_homepages_url)
   

    def get_products_url(self, urls):
        return [u'http://shop.coles.com.au/online/national/coca-cola-soft-drink-coke-375ml-cans-7365777p', u'http://shop.coles.com.au/online/national/coca-cola-soft-drink-coke-zero-chilled']


    def get_homepages_url(self, response):
        url_rules = '//ul[@id="subnav"]/li/a/@href'
        urls = response.xpath(url_rules).extract()
        return urls 
