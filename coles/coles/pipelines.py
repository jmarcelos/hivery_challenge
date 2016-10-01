# -*- coding: utf-8 -*-
from pymongo import MongoClient
from scrapy.conf import settings
from scrapy.exceptions import DropItem
from scrapy import log

class MongoDBPipeline(object):

    def __init__(self):
        self.connection = MongoClient(settings['MONGODB_SERVER'], settings['MONGODB_PORT'])
        db = self.connection[settings['MONGODB_SERVER']]
        self.collection = db[settings['MONGODB_COLLECTION']] 

    def close_spider(self, spider):
        self.connection.close()

    def process_item(self, item, spider):
        self.collection.insert(dict(item))
        log.msg('Saving item {} in MongoDB'.format(dict(item)))
        return item
