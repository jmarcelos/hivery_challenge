# encoding: utf-8
import os
import json

from scrapy.http import  Request
from scrapy.http.response.text import TextResponse

def coles_response(filename, url=None):
    if not url:
        url = 'http://www.example.com'

    request = Request(url=url)

    if not filename[0] == '/fixtures':
        responses_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(responses_dir, filename)
    else:
        file_path = filename

    file_content = open(file_path, 'r').read()
    response = TextResponse(url=url, request=request, body=file_content)

    return response

def get_product_details():
    filename = 'product_details.json'
    if not filename[0] == '/':
        responses_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(responses_dir, filename)
    else:
        file_path = filename

    products_detail = json.loads(open(file_path, 'rt').read())

    return products_detail

def get_products_urls():
    pass
