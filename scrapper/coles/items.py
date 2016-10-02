# -*- coding: utf-8 -*-

import datetime
from scrapy.item import Item, Field

class PriceRegion(Item):


    price = Field()
    postcode = Field()



class Region(Item):

    
    state = Field()
    score = Field()
    collectionpoint = Field()
    suburb = Field()
    country = Field()
    zoneid = Field()
    webstoreid = Field()
    lon = Field()
    id = Field()
    postcode = Field()
    lat = Field()
    servicetype = Field()



class Product(Item):


    name = Field()
    brand = Field()
    description = Field()
    product_img = Field()
    purchasing_price = Field() 
    last_updated = datetime.datetime.now()  
    id = Field()
    url_friendly_name = Field()
    prices_region = Field()
    #purchasing = response.xpath('//div[@class="purchasing"]').extract()
    #purchasing_price = response.xpath('//div[@class="purchasing"]/div[@class="price"]/text()').extract()

