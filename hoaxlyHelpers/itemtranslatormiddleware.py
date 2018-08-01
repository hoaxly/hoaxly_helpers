"""
Spider middleware for creating storedItem massaging data before save
"""
from __future__ import absolute_import
import logging
import scrapy
from scrapy.http import Request


def is_string_field(fieldtocheck):

    if not isinstance(fieldtocheck, str):
        return
    else:
        return fieldtocheck


def get_nested(obj, keys):
    try:
        for key in keys:
            obj = obj[key]
    except KeyError:
        return None
    return obj


class BuildHoaxlyReviewItem:
    """Takes all the different microdata found for one item and merges the info into a new object representing the hxl item."""
    fields = {}
    def __init__(self, input_item):
        self.input_item = input_item


    def map(self, target, source):

        try:
            self.fields[target] = get_nested(self.input_item, source)

        except KeyError:
            self.fields[target] = None

    def output_item(self):
        logging.debug(self.fields.keys())

        title = self.fields['hoaxly_review_title']
        reviewed_url = self.fields['hoaxly_review_url']
        ratings = {
            'badge': self.fields['hoaxly_review_rating_badge'],
            'originalAlternateName': self.fields['hoaxly_review_rating_alternate'],
            'bestRating': self.fields['hoaxly_review_rating_best'],
            'worstRating': self.fields['hoaxly_review_rating_worst'],
            'originalRatingValue': self.fields['hoaxly_review_rating_value']
        }
        outputted_item = HoaxlyReviewItem()
        outputted_item['hoaxly_review_title'] = title
        outputted_item['hoaxly_review_url'] = reviewed_url
        outputted_item['hoaxly_review_rating'] = ratings
        return outputted_item


class HoaxlyReviewItem(scrapy.Item):
    """a rewritten item to be saved to db enriched with extracted microdata."""

    url = scrapy.Field()
    hoaxly_review_title = scrapy.Field()
    hoaxly_review_url = scrapy.Field()
    hoaxly_review_datePublished = scrapy.Field(serializer=str)
    hoaxly_review_authors = scrapy.Field()
    hoaxly_review_rating = scrapy.Field()

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)


    def printReviewItem(self):
        return self


class ItemTransformer(object):
    """This class transforms items (run after microdata extraction)."""


    def process_spider_output(self, response, result, spider):
        """get all metadata and add them as fields to item"""
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        for scraped_item in result:
            if isinstance(scraped_item, Request):
                # yield the request without making changes
                yield scraped_item
            else:
                enriched_item = BuildHoaxlyReviewItem(scraped_item)

                prefered_title_source = spider.settings['MICROMAP_TITLE_SOURCE']
                prefered_review_url_source = spider.settings['MICROMAP_REVIEWED_URL_SOURCE']
                prefered_rating_best = spider.settings['MICROMAP_RATING_BEST']
                prefered_rating_alternate = spider.settings['MICROMAP_RATING_ALTERNATE']
                prefered_rating_value = spider.settings['MICROMAP_RATING_VALUE']



                enriched_item.map("hoaxly_review_title", prefered_title_source)
                enriched_item.map("hoaxly_review_url", prefered_review_url_source)
                enriched_item.map("hoaxly_rating_best", prefered_rating_best)
                enriched_item.map("hoaxly_rating_alternate", prefered_rating_alternate)
                enriched_item.map("hoaxly_rating_value", prefered_rating_value)

                review_item = enriched_item.output_item()
                review_item['url'] = scraped_item['url']
                review_item['source'] = scraped_item['spider']
                logging.debug(review_item.printReviewItem())

                yield review_item
