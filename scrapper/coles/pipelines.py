# -*- coding: utf-8 -*-
from pymongo import MongoClient
from scrapy.utils.project import get_project_settings

class MongoDBPipeline(object):

    def __init__(self):
        settings = get_project_settings()
        self.connection = MongoClient(settings['MONGODB_SERVER'], settings['MONGODB_PORT'])
        db = self.connection[settings['MONGODB_SERVER']]
        self.collection = db[settings['MONGODB_COLLECTION']]

    def close_spider(self, spider):
        self.connection.close()

    def process_item(self, item, spider):
        self.collection.insert(dict(item))
        return item
