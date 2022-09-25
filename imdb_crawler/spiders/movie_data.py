import scrapy
import re
from scrapy.loader import ItemLoader
from imdb_crawler.items import TalentItem, GoofItem, ImdbCrawlerItem, QuoteItem


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
        movie.add_value(
            'id', re.findall("tt[\d]+", response.url)[0])
        movie.add_xpath(
            'title', '//h1[@data-testid="hero-title-block__title"]//text()')
        movie.add_xpath(
            'year', '//h1[@data-testid="hero-title-block__title"]/following-sibling::*/ul/li/a[contains(@href, "releaseinfo")]/text()')
        movie.add_xpath(
            'parentalGuide', '//h1[@data-testid="hero-title-block__title"]/following-sibling::*/ul/li/a[contains(@href, "parentalguide")]/text()')
        yield scrapy.Request(response.urljoin('quotes'), callback=self.quotes, meta={'movie': movie.load_item()})

    def quotes(self, response):
        movie = ItemLoader(item=response.meta['movie'], response=response)
        for quote in response.xpath('//div[contains(@class,"soda sodavote")]'):

            quoteLoader = ItemLoader(item=QuoteItem(), selector=quote)

            quoteType = quote.xpath(
                './preceding-sibling::h4[@class="li_group"]/text()').get()
            if quoteType is None:
                quoteType = 'Common'
            else:
                quoteType = quoteType.strip()
            quoteLoader.add_value('type', quoteType)

            quoteLoader.add_xpath('content', './div[@class="sodatext"]')
            quoteLoader.add_xpath(
                'rating', './/a[@class="interesting-count-text"]/text()')

            movie.add_value('quotes', quoteLoader.load_item())

        yield scrapy.Request(response.url.replace('quotes', 'goofs'), callback=self.goofs, meta={'movie': movie.load_item()})

    def goofs(self, response):
        movie = ItemLoader(item=response.meta['movie'], response=response)
        for goof in response.xpath('//div[contains(@class,"soda sodavote")]'):

            goofLoader = ItemLoader(item=GoofItem(), selector=goof)

            goofType = goof.xpath(
                './preceding-sibling::h4[@class="li_group"]/text()').get()
            if goofType is None:
                goofType = 'Unknown'
            else:
                goofType = goofType.strip()
            goofLoader.add_value('type', goofType)

            goofLoader.add_css('content', 'div.sodatext')
            goofLoader.add_css(
                'rating', 'div.did-you-know-actions a.interesting-count-text::text')

            movie.add_value('goofs', goofLoader.load_item())

        yield scrapy.Request(response.url.replace('goofs', 'fullcredits'), callback=self.fullcredits, meta={'movie': movie.load_item()})

    def fullcredits(self, response):
        movie = ItemLoader(item=response.meta['movie'], response=response)

        for director in response.xpath('//h4[@name="director"]/following-sibling::*[position()=1]//td[@class="name"]'):
            directorLoader = ItemLoader(item=TalentItem(), selector=director)
            directorLoader.add_xpath(
                'id', './a[contains(@href, "/name/")]/@href')
            directorLoader.add_xpath(
                'name', './a[contains(@href, "/name/")]/text()')
            movie.add_value('director', directorLoader.load_item())

        for writer in response.xpath('//h4[@name="writer"]/following-sibling::*[position()=1]//td[@class="name"]'):
            writerLoader = ItemLoader(item=TalentItem(), selector=writer)
            writerLoader.add_xpath(
                'id', './a[contains(@href, "/name/")]/@href')
            writerLoader.add_xpath(
                'name', './a[contains(@href, "/name/")]/text()')
            movie.add_value('writer', writerLoader.load_item())

        for actor in response.xpath('//table[@class="cast_list"]//tr'):
            actorLoader = ItemLoader(item=TalentItem(), selector=actor)
            actorLoader.add_xpath(
                'id', './td/a[contains(@href, "/name/")]/@href')
            actorLoader.add_xpath(
                'name', './td/a[contains(@href, "/name/")]/text()')
            movie.add_value('actors', actorLoader.load_item())

        yield movie.load_item()
