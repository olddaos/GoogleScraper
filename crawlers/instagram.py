from celery import Celery
from celery import group
from celery import Task
from celery import current_app
from celery.contrib.methods import task
from celery.contrib.methods import task_method

# Google deps
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
import time
import os
from instagram.client import InstagramAPI
import urllib2
import json
import re

from .geturl import GetURL

# Converts request to Instagram API call, and then -- to the list of URLs ( which is then put to the queur )
class InstagramCrawler(Task):
    def __init__(self):
        self.queue      = 'instagram_crawler'

    # Actually converts query to Instagram media search
    # TODO: use tags search to expand possible variants of query ( "eiffel", "eiffelparis", "eiffelcarzy" etc )
    # TODO: do not call this task directly, only from pagination iterator
    # Query is a search query ( keywords or free-form text )

    # TODO: obtain token and cli_id, cli_secret using appropriate tools
    def run(self, query, next_url = None, token="", cli_id='', cli_secret='', results_amount = 100):
        # 1. Call Instagram and get list of media for this query
        if ( next_url == None ):
                api = InstagramAPI(client_id=cli_id, client_secret=cli_secret, access_token=token )
                media = api.tag_recent_media(results_amount, 0,  query )

                print media

                # Dirtiest hack ever! Expect this gets broken someday! media[-1] is a hidden internal representation of instagram request, suitable for pagination
                # But how to make this pagination using current stable API is unclear
                r = urllib2.urlopen(media[-1])
        else:
                r = urllib2.urlopen( next_url )

        pictures_data = json.loads( r.read() )

        #print "data size=%d" % pictures_data['data'].__len__()

        urls = []
        # TODO: serialize this to Mongo
        for pic in pictures_data['data']:
                urls.append( pic['images']['standard_resolution']['url'] )
                GetURL().delay( pic['images']['standard_resolution']['url'], tags=pic['tags'] )

        # Output to paginator
        pagination_struct = { 'urls' : urls, 'next_url' : pictures_data['pagination']['next_url']}

        return pagination_struct

