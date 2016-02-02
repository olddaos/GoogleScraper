from celery import Celery
from celery import Task

# Mongo
from bson import Binary
from pymongo import MongoClient

import urllib2


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

