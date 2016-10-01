# -*- coding: utf-8 -*-

import datetime
from scrapy.item import Item, Field


class Product(Item):


    name = Field()
    brand = Field()
    description = Field()
    product_img = Field()
    purchasing_price = Field() 
    last_updated = datetime.datetime.now()  
    id = Field()
    url_friendly_name = Field()
    #purchasing = response.xpath('//div[@class="purchasing"]').extract()
    #purchasing_price = response.xpath('//div[@class="purchasing"]/div[@class="price"]/text()').extract()

