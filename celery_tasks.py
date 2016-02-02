#! /usr/bin/python

import sys
import time
import numpy as np
from celery import Celery
from celery import group
from celery import Task
from celery import current_app
from celery.contrib.methods import task
from celery.contrib.methods import task_method

# Google deps
from crawlers.google import  GoogleCrawler

# Bing deps
from crawlers.bing import  BingCrawler

# Flickr deps
from crawlers.flickr import  FlickrCrawler

# Instagram
from crawlers.instagram import  InstagramCrawler

# Mongo
from bson import Binary
from pymongo import MongoClient

# APIs
from instagram.client import InstagramAPI
import flickr_api
from flickr_api.api import flickr
import urllib2
import json
import re


# TODO: move out celery configs to the more appropriate place
app = Celery('celery_tasks', backend='redis://54.221.232.248', broker='redis://54.221.232.248') 
app.conf.update(
   CELERY_ROUTES = {
       'BingCrawler': {'queue': 'bing_crawler'},
       'InstagramCrawler': {'queue': 'instagram_crawler'},
       'FlickrCrawler': {'queue': 'flickr_crawler'},
       'GetURL': {'queue': 'urls_queue'},
       'GoogleCrawler': {'queue': 'google_crawler'}
   }
)

# As the name suggests, it only gets URL, stores it at the disk and updates Mongo to fix that fact
class GetURL(Task):
    def __init__( self ):
	self.queue      = 'urls_queue'
	self.client = MongoClient()
	self.db     = self.client.test_crawl

    def run(self,  picture_url, tags = None, taken_time = None, coords = None ):
	print "GetURL received "+ picture_url

	r = urllib2.urlopen( picture_url )
	pic_wrapper = Binary( r.read())

	obj_struct = {
		"bad_categories" : [ ],
		"good_categories" : [ ],
		"loc" : {
		        "type" : "Point",
		        "coordinates" : coords, 
    		},
		"url" : picture_url,
		"image" : pic_wrapper,
		"tags" : tags,
		"taken" : taken_time
	}
	self.db.test_crawl.insert( obj_struct )


# Converts request to Instagram API call, and then -- to the list of URLs ( which is then put to the queur )
class InstagramCrawler(Task):
    def __init__(self):
	self.queue      = 'instagram_crawler'

    # Actually converts query to Instagram media search
    # TODO: use tags search to expand possible variants of query ( "eiffel", "eiffelparis", "eiffelcarzy" etc ) 
    # TODO: do not call this task directly, only from pagination iterator
    # Query is a search query ( keywords or free-form text )
    def run(self, query, next_url = None, token="", cli_id='', cli_secret='', results_amount = 100):
	# 1. Call Instagram and get list of media for this query  
	if ( next_url == None ):
		print "Calling API for a first time..."
		api = InstagramAPI(client_id=cli_id, client_secret=cli_secret, access_token=token )	
		media = api.tag_recent_media(results_amount, 0,  query )

		print media

		# Dirtiest hack ever! Expect this gets broken someday! media[-1] is a hidden internal representation of instagram request, suitable for pagination
		# But how to make this pagination using current stable API is unclear
		r = urllib2.urlopen(media[-1])
	else:
		print "Calling NextURL =" + next_url
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

	print "pagination:"
	print pagination_struct
	return pagination_struct 
		

# Converts request to Flickr API call, and then -- to the list of URLs ( which is then put to the queur )
class FlickrCrawler(Task):
    def __init__(self ):
        self.queue      = 'flickr_crawler'

    # Actually converts query to Flickr to search request
    # Query is a search query ( keywords or free-form text )
    def run(self, query, page_id = 0, urls_per_page = 500, api_key= "", api_secret=""):
	# 1. Call Flickr

	flickr_api.set_keys(api_key = api_key, api_secret = api_secret )
	json_reply = flickr.photos.search( text = query, page = page_id, per_page = urls_per_page, format = 'json', extras="url_m,geo,tags,views,date_taken" )

	m  = re.search(r'jsonFlickrApi\((.+)\)', json_reply )
	reply = json.loads( m.group(1) )

	#print reply
	urls = []
	print "TRC: pages = %d" % reply['photos']['pages']
	for photo in reply['photos']['photo']:
		#print "Submitted " + photo['url_m']
		urls.append( photo['url_m'] )
	       # FIXME deal correctly with date_taken GetURL().delay( photo['url_m'], tags= photo['tags'], taken_time=photo['date_taken'], coords=photo['geo'] )	

	        GetURL().delay( photo['url_m'], tags= photo['tags'].split())

	pagination_struct = { 'urls' : urls, 'pages' : reply['photos']['pages'] }
	return pagination_struct
	# TODO: add pagination once upon a time
