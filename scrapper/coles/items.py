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
    zone_id = Field()
    webstore_id = Field()
    lon = Field()
    id = Field()
    postcode = Field()
    lat = Field()
    service_type = Field()


class Product(Item):


    name = Field()
    ingredients = Field()
    allergen = Field()
    servings_per_pack = Field()
    serving_size = Field()
    retail_limit = Field()
    ticket_type = Field()
    brand = Field()
    description = Field()
    product_img = Field()
    purchasing_price = Field() 
    last_updated = datetime.datetime.now()  
    id = Field()
    url_friendly_name = Field()
    prices_region = Field()
    redirect_url = Field()
    price_type = Field()
    general_price = Field()
    size = Field()
