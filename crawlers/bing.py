from celery import Celery
from celery import group
from celery import Task
from celery import current_app
from celery.contrib.methods import task
from celery.contrib.methods import task_method

# Bing deps
from lxml import html
import urlparse
import collections
import requests
import logging

# Converts request to Instagram API call, and then -- to the list of URLs ( which is then put to the queur )
class BingCrawler(Task):
    def __init__(self):
        self.queue      = 'bing_crawler'
        self.response_timeout = 5

    # Actually converts query to Instagram media search
    # TODO: use tags search to expand possible variants of query ( "eiffel", "eiffelparis", "eiffelcarzy" etc )
    # TODO: do not call this task directly, only from pagination iterator
    # Query is a search query ( keywords or free-form text )
    def run(self, query, page_id = 0):
        url_request = 'http://www.bing.com/images/search?q=' + query.replace(" ", "+") + '&first=' + str(page_id)
        try:
                response = requests.get(url_request, timeout = self.response_timeout)
        except Exception:
                print "Err: request %s failed!" % url_request
                return { 'urls' : None, 'next_page' : page_id }

        parsed_body = html.fromstring(response.text)
        href_list = parsed_body.xpath('//a/@m')
        if not href_list:
                print "Wrn: unable to parse Bing output!"
                return { 'urls' : None, 'next_page' : page_id }

        # Initialize list of URLs to download
        imgurls = list()
        for href in href_list:
                parts = href.split(",")
                for part in parts:
                    if "imgurl" in part:
                        imgurl = part[7:]
                        imgurl = imgurl.replace('"', '')
                        imgurls.append(imgurl)

        # Call actual crawling task
        for url in imgurls:
                page_id   += 1
                GetURL().delay( url, tags=query )

        # Output to paginator
        pagination_struct = { 'urls' : imgurls, 'next_page' : page_id }

        print "Bing pagination:"
        print pagination_struct
        return pagination_struct


