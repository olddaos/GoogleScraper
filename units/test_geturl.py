#! /usr/bin/python

import urllib2
from bson import Binary
from pymongo import MongoClient

client = MongoClient()
picture_url = "http://farm4.staticflickr.com/3407/3450596863_1fea93d388_m.jpg"
r = urllib2.urlopen( picture_url )

pic_wrapper = Binary( r.read())

obj_struct = {
    "bad_categories" : [ "sangiorgiomaggiore"],
    "good_categories" : [ ],
    "loc" : {
        "type" : "Point",
        "coordinates" : [
            45.428937,
            12.340822
        ]
    },
    "views" : "368",
    "url" : picture_url,
    "image" : pic_wrapper,
    "tags" : [
        "venice",
        "venedig",
        "2009",
        "hdr",
        "sangiorgiomaggiore"
    ],
    "taken" : "2009-02-16 14:29:23"
}

db  = client.test_crawl
db.test_crawl.insert( obj_struct )
found_obj = db.test_crawl.find_one({ 'url' : "http://farm4.staticflickr.com/3407/3450596863_1fea93d388_m.jpg"})

print found_obj
