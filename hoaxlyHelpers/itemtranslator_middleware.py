# after adding microdata in the previous middleware run this middleware to create output item
#     Spider middleware for creating storedItem massaging data before save

"""
Spider middleware for creating storedItem massaging data before save
"""
from __future__ import absolute_import
import logging
import scrapy
from scrapy.http import Request
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def is_string_field(fieldtocheck):
    """ check a field to make sure it is a string """
    if not isinstance(fieldtocheck, str):
        return None
    return fieldtocheck


def get_nested(obj, keys):
    """ get a value from a nested object by following a list of keys """
    try:
        for key in keys:
            obj = obj[key]
    except KeyError:
        return None
    return obj


class BuildHoaxlyReviewItem:
    """Takes scraped item and maps it into a new object representing the hxl item."""

    fields = {}

    fields['hoaxly_review_title'] = 'n/a'
    fields['hoaxly_review_rating_alternate'] = 'n/a'
    fields['hoaxly_review_rating_badge'] = 'n/a'
    fields['hoaxly_review_rating_best'] = 'n/a'
    fields['hoaxly_review_rating_worst'] = 'n/a'
    fields['hoaxly_review_publisher_name'] = 'n/a'
    fields['hoaxly_review_publisher_url'] = 'n/a'
    fields['hoaxly_review_publisher_logo'] = 'n/a'
    fields['hoaxly_review_date_published'] = 'n/a'

    fields['hoaxly_claim_reviewed'] = 'n/a'
    fields['hoaxly_claim_date_published'] = 'n/a'
    fields['hoaxly_claim_publisher_name'] = 'n/a'

    def __init__(self, input_item):
        self.input_item = input_item
    def map(self, target, source):
        """ prepare a field for building items"""
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        logging.debug("will try to map to %s", target)
        if not source:
            logging.info("skipping empty mapping to %s", target)
        else:
            try:
                logging.info("will try mapping from %s to %s", source, target)
                valuefromsource = get_nested(self.input_item, source)
                if not valuefromsource:
                    logging.error("sorry, empty value")
                else:
                    self.fields[target] = get_nested(self.input_item, source)
                    logging.info("ok, mapping from %s to %s", source, target)
            except KeyError:
                logging.error("sorry, cant map this")
                self.fields[target] = None

    def output_item(self):
        """this methid creates the final review item for output"""
        logging.debug(self.fields.keys())

        title = self.fields['hoaxly_review_title']
        reviewed_url = self.fields['hoaxly_review_url']
        review_date_published = self.fields['hoaxly_review_date_published']
        reviewed_claim = self.fields['hoaxly_claim_reviewed']
        reviewed_claim_date_published = self.fields['hoaxly_claim_date_published']
        reviewed_claim_publisher_name = self.fields['hoaxly_claim_publisher_name']

        ratings = {
            'badge': self.fields['hoaxly_review_rating_badge'],
            'originalAlternateName': self.fields['hoaxly_review_rating_alternate'],
            'bestRating': self.fields['hoaxly_review_rating_best'],
            'worstRating': self.fields['hoaxly_review_rating_worst'],
            'originalRatingValue': self.fields['hoaxly_review_rating_value']
        }
        publisher = {
            'name':  self.fields['hoaxly_review_publisher_name'],
            'logo':  self.fields['hoaxly_review_publisher_logo'],
            'url':  self.fields['hoaxly_review_publisher_url']
        }

        outputted_item = HoaxlyReviewItem()
        outputted_item['hoaxly_review_title'] = title
        outputted_item['hoaxly_review_date_published'] = review_date_published
        outputted_item['hoaxly_review_url'] = reviewed_url
        outputted_item['hoaxly_review_rating'] = ratings
        outputted_item['hoaxly_review_publisher'] = publisher
        outputted_item['hoaxly_claim_reviewed'] = reviewed_claim
        outputted_item['hoaxly_claim_date_published'] = reviewed_claim_date_published
        outputted_item['hoaxly_claim_publisher_name'] = reviewed_claim_publisher_name

        return outputted_item


class HoaxlyReviewItem(scrapy.Item):
    """a rewritten item to be saved to db enriched with extracted microdata."""

    url = scrapy.Field()
    spider = scrapy.Field()
    timestamp = scrapy.Field()
    hoaxly_review_title = scrapy.Field()
    hoaxly_review_url = scrapy.Field()
    hoaxly_review_date_published = scrapy.Field(serializer=str)
    hoaxly_review_authors = scrapy.Field()
    hoaxly_review_rating = scrapy.Field()
    hoaxly_review_publisher = scrapy.Field()
    hoaxly_claim_reviewed = scrapy.Field()
    hoaxly_claim_date_published = scrapy.Field()
    hoaxly_claim_publisher_name = scrapy.Field()

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def print_review_item(self):
        """ a way to look at the current object """
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

                logging.debug(scraped_item)
                enriched_item = BuildHoaxlyReviewItem(scraped_item)

                prefered_title_source = spider.settings['MICROMAP_TITLE_SOURCE']
                prefered_review_url_source = spider.settings['MICROMAP_REVIEWED_URL_SOURCE']
                prefered_review_date_published = spider.settings['MICROMAP_REVIEW_DATE_PUBLISHED']
                prefered_reviewed_claim = spider.settings['MICROMAP_CLAIM_REVIEWED']

                prefered_rating_best = spider.settings['MICROMAP_RATING_BEST']
                prefered_rating_worst = spider.settings['MICROMAP_RATING_WORST']
                prefered_rating_alternate = spider.settings['MICROMAP_RATING_ALTERNATE']
                prefered_rating_value = spider.settings['MICROMAP_RATING_VALUE']
                prefered_rating_badge = spider.settings['MICROMAP_RATING_BADGE']

                prefered_publisher_name = spider.settings['MICROMAP_PUBLISHER_NAME']
                prefered_publisher_url = spider.settings['MICROMAP_PUBLISHER_URL']
                prefered_publisher_logo = spider.settings['MICROMAP_PUBLISHER_LOGO']

                prefered_claim_date_published = spider.settings['MICROMAP_CLAIM_DATE_PUBLISHED']
                prefered_claim_publisher_name = spider.settings['MICROMAP_CLAIM_PUBLISHER_NAME']

                enriched_item.map(
                    "hoaxly_review_title", prefered_title_source)
                enriched_item.map(
                    "hoaxly_review_url", prefered_review_url_source)
                enriched_item.map(
                    "hoaxly_review_date_published", prefered_review_date_published)

                enriched_item.map(
                    "hoaxly_review_rating_best", prefered_rating_best)
                enriched_item.map(
                    "hoaxly_review_rating_worst", prefered_rating_worst)
                enriched_item.map(
                    "hoaxly_review_rating_alternate", prefered_rating_alternate)
                enriched_item.map(
                    "hoaxly_review_rating_value", prefered_rating_value)
                enriched_item.map(
                    "hoaxly_review_rating_badge", prefered_rating_badge)

                enriched_item.map(
                    "hoaxly_review_publisher_name", prefered_publisher_name)
                enriched_item.map(
                    "hoaxly_review_publisher_url", prefered_publisher_url)
                enriched_item.map(
                    "hoaxly_review_publisher_logo", prefered_publisher_logo)

                enriched_item.map(
                    "hoaxly_claim_reviewed", prefered_reviewed_claim)
                enriched_item.map(
                    "hoaxly_claim_date_published", prefered_claim_date_published)
                enriched_item.map(
                    "hoaxly_claim_publisher_name", prefered_claim_publisher_name)

                review_item = enriched_item.output_item()
                review_item['url'] = scraped_item['url']
                review_item['spider'] = scraped_item['spider']
                review_item['timestamp'] = scraped_item['timestamp']
                logging.debug(review_item.print_review_item())

                yield review_item
