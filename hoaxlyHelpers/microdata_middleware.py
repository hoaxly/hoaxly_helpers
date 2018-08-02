"""
Spider middleware for enriching item with scraped metadata
"""
from __future__ import absolute_import
import logging
import scrapy
from scrapy.http import Request
import extruct


def is_string_field(fieldtocheck):

    if not isinstance(fieldtocheck, str):
        return
    else:
        return fieldtocheck


class MicrodataExtruction(object):
    """This class extracts microdata."""

    def process_spider_output(self, response, result, spider):
        """get all metadata and add them as fields to item"""
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        for scraped_item in result:
            if isinstance(scraped_item, Request):
                # yield the request without making changes
                
                yield scraped_item
            else:
                # if this is an item inspect for microdata
                data = extruct.extract(
                    response.body,
                    response.url,
                    syntaxes=['microdata', 'opengraph', 'rdfa', 'json-ld'],
                    uniform=True
                )

                logging.debug(response.url)
                scraped_item['url'] = response.url
                # scraped_item['source_spider'] = spider.name

                if not data:
                    # if no microdata was found set flag and yield the item
                    logging.debug('this item has no microdata')
                    scraped_item['hasMetaData'] = False
                else:
                    scraped_item['hasMetaData'] = True
                    scraped_item['microdatas'] = data
                yield scraped_item
