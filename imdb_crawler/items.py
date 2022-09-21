# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from tokenize import String
from itemloaders.processors import TakeFirst, MapCompose
from scrapy.selector import Selector
import scrapy
import re

def lookahead(iterable):
    """Pass through all values from the given iterable, augmented by the
    information if there are more values to come after the current one
    (True), or if it is the last value (False).
    """
    # Get an iterator and pull the first value.
    it = iter(iterable)
    last = next(it)
    # Run the iterator to exhaustion (starting from the second value).
    for val in it:
        # Report the *previous* value (more to come).
        yield last, True
        last = val
    # Report the last value.
    yield last, False
    # https://stackoverflow.com/questions/1630320/what-is-the-pythonic-way-to-detect-the-last-element-in-a-for-loop

def OnlyNumbers(text):
    digits = re.findall(r'\d+', text)
    if len(digits) > 0:
        return digits

def cleanContent(divQuote):
    fullText = ''
    for p, has_more in lookahead(Selector(text=divQuote).xpath('.//text()').getall()):
        fullText = fullText + p.strip().replace('\n', ' ')
    return fullText

def setRating(rating):
    rate = re.findall('[\d,]+', rating)
    if len(rate) == 2:
        return {'positive': int(rate[0].replace(',', '')), 'total': int(rate[1].replace(',', ''))}
    return {'positive': 0, 'total': 0}


class GoofItem(scrapy.Item):
    type = scrapy.Field(output_processor=TakeFirst())
    content = scrapy.Field(input_processor=MapCompose(
        cleanContent), output_processor=TakeFirst())
    rating = scrapy.Field(input_processor=MapCompose(
        setRating), output_processor=TakeFirst())


class QuoteItem(scrapy.Item):
    type = scrapy.Field(output_processor=TakeFirst())
    content = scrapy.Field(input_processor=MapCompose(
        cleanContent), output_processor=TakeFirst())
    rating = scrapy.Field(input_processor=MapCompose(
        setRating), output_processor=TakeFirst())


class ImdbCrawlerItem(scrapy.Item):
    id = scrapy.Field()
    position = scrapy.Field(input_processor=MapCompose(
        OnlyNumbers), output_processor=TakeFirst())
    title = scrapy.Field(output_processor=TakeFirst())
    year = scrapy.Field(output_processor=TakeFirst())
    parentalGuide = scrapy.Field(output_processor=TakeFirst())
    quotes = scrapy.Field()
    goofs = scrapy.Field()
