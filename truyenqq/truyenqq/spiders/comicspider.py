import scrapy
from truyenqq.items import TruyenqqItem
import re
from urllib.parse import urlencode
API_KEY = 'b3a00a28-c975-4755-9033-84e0215590d1'

def get_proxy_url(url):
    payload = {'api_key':API_KEY, 'url':url}
    proxy_url  = 'https://proxy.scrapeops.io/v1/' + urlencode(payload)
    return proxy_url

class ComicspiderSpider(scrapy.Spider):
    name = "comicspider"
    #allowed_domains = ["truyenqqvn.com"]
    start_urls = ["https://truyenqqvn.com/truyen-moi-cap-nhat/trang-1.html"]

    def parse(self, response):
        stories = response.css('div.list_grid_out ul li')
        for story in stories:
            truyen = TruyenqqItem()
            truyen['name'] = story.css('h3 a::text').get(),
            truyen['url'] = story.css('h3 a::attr(href)').get(),
            truyen['description'] = story.css('div.excerpt::text').get(),
            truyen['newest_chapter']= story.css('div.last_chapter a::text').get()
            yield truyen
        
        next_page = response.xpath('//div[@class="page_redirect"]/a[@href="javascript:void(0)"]/following-sibling::*[1]').get()
        pattern = r'<a\s+(?:[^>]*?\s+)?href="([^"]*)"'
        link_next_page = re.findall(pattern, str(next_page))
        
        #yield response.follow(link_next_page[0], callback = self.parse)
        yield scrapy.Request(get_proxy_url(link_next_page), callback=self.parse)