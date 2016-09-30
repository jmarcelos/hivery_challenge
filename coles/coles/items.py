# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import datetime

class Product(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    brand = scrapy.Field()
    description = scrapy.Field()
    product_img = scrapy.Field()
    purchasing_price = scrapy.Field() 
    last_updated = datetime.datetime.now()  
    #brand = response.xpath('//div[@class="brand"]/text()').extract()

    #name =
    #dirty_name = response.xpath('//div[@id="FBLikeDiv"]/@data-social').extract()
    #regex = r"'(.*?)'"
    #re.findall(regex, dirty_name)[2]

    #description =
    #response.xpath('//div[@id="FBLikeDiv"]/@data-social').extract()
    #regex = r"'(.*?)'"
    #re.findall(regex, dirty_name)[3]


    #produdct_img = re.findall(regex, y)[0]
    #url_friendly_name_dirty = re.findall(regex, y)[1]
    #url_friendly_name = url_friendly_name_dirty.split('/').[-1]

    #purchasing = response.xpath('//div[@class="purchasing"]').extract()
    #purchasing_price = response.xpath('//div[@class="purchasing"]/div[@class="price"]/text()').extract()

