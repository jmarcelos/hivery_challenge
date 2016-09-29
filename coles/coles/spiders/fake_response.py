import os

from scrapy.http import  Request
from scrapy.http.response.text import TextResponse

def coles_response(file_name, url=None):
    if not url:
        url = 'http://www.example.com'

    request = Request(url=url)
    
    if not file_name[0] == '/':
        responses_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(responses_dir, file_name)
    else:
        file_path = file_name
        
    file_content = open(file_path, 'r').read()
    response = TextResponse(url=url, request=request, body=file_content)

    return response
