from typing import Any, Iterable
import scrapy
from scrapy.http import Request, Response
from bookscraper.items import BookItem
import random

#Rotate user-agent
user_agent_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_4_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
        'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 Edg/87.0.664.75',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18363',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0'
    ]

class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    # custom_settings = {
    #     'FEEDS' : {'bookscrape2.csv':{'format' : 'csv'}}
    # }
    # Or command line: scrapy crawl bookspider -O bookscrape2.csv

    def start_requests(self) -> Iterable[Request]:
        for url in self.start_urls:
            return Request(url=url, callback=self.parse, headers={'User-Agent': user_agent_list[random.randint(0, len(user_agent_list)-1)]})

    def parse(self, response):
        books = response.css('article.product_pod')
        for book in books:
            relative_url = book.css('h3 a').attrib['href']
            if 'catalogue/' in relative_url:
                book_url = 'https://books.toscrape.com/' + relative_url
            else:
                book_url = 'https://books.toscrape.com/catalogue/' + relative_url
            yield scrapy.Request(book_url, callback=self.parse_each_book)

        next_page = response.css('li.next a ::attr(href)').get()
        if next_page is not None:
            if 'catalogue/' in next_page:
                next_page_url = 'https://books.toscrape.com/' + next_page
            else:
                next_page_url = 'https://books.toscrape.com/catalogue/' + next_page
            yield response.follow(next_page_url, callback=self.parse)

    def parse_each_book(self,response):
        content = response.css('article.product_page')
        item = BookItem()
        item['title'] = content.css('div.row h1::text').get(),
        item['category'] = response.css('ul.breadcrumb li:nth-child(2) a::text').get(),
        item['upc'] = content.css('table tr td::text').get(),
        item['product_type'] = content.css('table tr:nth-child(2) td::text').get(),
        item['price_excl_tax'] = content.css('table tr:nth-child(3) td::text').get(),
        item['price_incl_tax'] = content.css('table tr:nth-child(4) td::text').get(),
        item['tax'] = content.css('table tr:nth-child(5) td::text').get(),
        item['availability'] = content.css('table tr:nth-child(6) td::text').get(),
        item['num_reviews'] = content.css('table tr:nth-child(7) td::text').get(),
        item['description'] = response.css('article.product_page > p::text').get(),
        item['stars'] = content.css('p.star-rating').attrib['class']
        
        yield item


        # def parse(self, response):
        #     books = response.css('article.product_pod')
        #     for book in books:
        #         yield{
        #             'name' : book.css('h3 a::text').get(),
        #             'price' : book.css('div.product_price .price_color::text').get(),
        #             'url' : book.css('h3 a').attrib['href'],
        #         }

        #     next_page = response.css('li.next a ::attr(href)').get()
        #     if next_page is not None:
        #         if 'catalogue/' in next_page:
        #             next_url = self.start_urls[0] + '/' + next_page
        #         else:
        #             next_url = self.start_urls[0] + '/catalogue/' +next_page
        #         yield response.follow(next_url, callback = self.parse)

    #First spider send request to web and downloader download file HTML for spider to extract it.
    #after receiving, spider parse this response to data by parse function
    # Activity in parse
        #extract books by css selector
        #yield each book with (name, price, url)
        #Expand browsing all next pages to extract all books (have link to next page and use response.follow as quy nap)
        #response.follow create a request to next_url and use parse ,...
    

    