import os
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from scrapper.coles.spiders.coles import ColesSpider

def start():

    settings = Settings()
    os.environ['SCRAPY_SETTINGS_MODULE'] = 'scrapper.coles.settings'
    settings_module_path = os.environ['SCRAPY_SETTINGS_MODULE']
    settings.setmodule(settings_module_path, priority='project')
    process = CrawlerProcess(settings)

    process.crawl(ColesSpider(), url='http://shop.coles.com.au/online/national/drinks',
            postcode='3182,6160,2010')
    process.start()

start()
