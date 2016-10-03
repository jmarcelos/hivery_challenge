import os
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from scrapy.utils.project import get_project_settings
from coles.spiders.coles import ColesSpider

settings = Settings()
os.environ['SCRAPY_SETTINGS_MODULE'] = 'scrapper.coles.settings'
settings_module_path = os.environ['SCRAPY_SETTINGS_MODULE']
settings.setmodule(settings_module_path, priority='project')
process = CrawlerProcess(settings)

process.crawl(ColesSpider(),url='http://shop.coles.com.au/online/national/drinks')
process.start()
