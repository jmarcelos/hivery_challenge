import scrapy


class ColesSpider(scrapy.Spider):
    name = 'myspider'

    def __init__(self, url=None, *args, **kwargs):
        super(ColesSpider, self).__init__(*args, **kwargs)
        self.start_urls = [url]

    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.get_homepages_url)
    

    def get_homepages_url(self, response):
        url_rules = '//ul[@id="subnav"]/li/a/@href'
        urls = response.xpath(url_rules).extract()
        
        return urls 
