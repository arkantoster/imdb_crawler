import scrapy
import re
from scrapy.loader import ItemLoader
from imdb_crawler.items import GoofItem, ImdbCrawlerItem, QuoteItem


class MovieDataSpider(scrapy.Spider):
    name = 'movie_data'
    allowed_domains = ['www.imdb.com']
    start_urls = ['http://www.imdb.com/chart/top']

    def parse(self, response):
        for row in response.css('tr'):
            movie = ItemLoader(item=ImdbCrawlerItem(), selector=row)
            movie.add_css(
                'position', 'td[class="titleColumn"]::text')
            link = row.css('td.titleColumn a::attr(href)').get()
            if link is not None:
                link = re.findall("\/title\/[\d\w]+", link)
                if len(link) == 1:
                    yield scrapy.Request(response.urljoin(link[0]), callback=self.main, meta={'movie': movie.load_item()})

    def main(self, response):
        movie = ItemLoader(item=response.meta['movie'], response=response)
        movie.add_xpath(
            'title', '//h1[@data-testid="hero-title-block__title"]//text()')
        movie.add_xpath(
            'year', '//h1[@data-testid="hero-title-block__title"]/following-sibling::*/ul/li/a[contains(@href, "releaseinfo")]/text()')
        movie.add_xpath(
            'parentalGuide', '//h1[@data-testid="hero-title-block__title"]/following-sibling::*/ul/li/a[contains(@href, "parentalguide")]/text()')
        yield scrapy.Request(response.urljoin('quotes'), callback=self.quotes, meta={'movie': movie.load_item()})

    def quotes(self, response):
        movie = ItemLoader(item=response.meta['movie'], response=response)
        for list in response.xpath('//div[@class="list"]'):
            quoteType = list.css('h4.li_group::text').get()
            if quoteType is None:
                quoteType = 'Common'
            else:
                quoteType = quoteType.strip()
            for quoteSelector in list.css('div.quote'):
                quoteLoader = ItemLoader(
                    item=QuoteItem(), selector=quoteSelector)
                quoteLoader.add_value('type', quoteType)
                quoteLoader.add_css('content', 'div.sodatext')
                quoteLoader.add_css(
                    'rating', 'div.did-you-know-actions a.interesting-count-text::text')
                movie.add_value('quotes', quoteLoader.load_item())
        yield scrapy.Request(response.url.replace('quotes', 'goofs'), callback=self.goofs, meta={'movie': movie.load_item()})

    def goofs(self, response):
        movie = ItemLoader(item=response.meta['movie'], response=response)
        for goof in response.xpath('//div[contains(@class,"soda sodavote")]'):
            goofLoader = ItemLoader(item=GoofItem(), selector=goof)
            goofType = goof.xpath('./preceding-sibling::h4[@class="li_group"]/text()').get()
            if goofType is None:
                goofType = 'Unknown'
            else:
                goofType = goofType.strip()
            goofLoader.add_value('type', goofType)
            goofLoader.add_css('content', 'div.sodatext')
            goofLoader.add_css(
                'rating', 'div.did-you-know-actions a.interesting-count-text::text')
            movie.add_value('goofs', goofLoader.load_item())
        yield movie.load_item()

