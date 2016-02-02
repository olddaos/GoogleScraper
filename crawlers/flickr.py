from celery import Celery
from celery import group
from celery import Task

# APIs
import flickr_api
from flickr_api.api import flickr
import urllib2
import json
import re

# Converts request to Flickr API call, and then -- to the list of URLs ( which is then put to the queur )
class FlickrCrawler(Task):
    def __init__(self ):
        self.queue      = 'flickr_crawler'

    # Actually converts query to Flickr to search request
    # Query is a search query ( keywords or free-form text )

    # TODO: Obtain api_key and api_secret from Flickr!
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

