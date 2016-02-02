#! /usr/bin/python
from instagram.client import InstagramAPI
import urllib2
import json
import re
api = InstagramAPI(access_token="2055276013.1677ed0.de948b2188724a9a83d5628293f126ed", client_id='b5a54679833e4dfd8afabd53de5027f8', client_secret='9ef736739aa54261b70f862fea858cdc')
media = api.tag_recent_media(100, 981560249971920139, "eiffel")

r = urllib2.urlopen(media[-1])

pictures_data = json.loads( r.read() ) 

#print pictures_data

while ( pictures_data['pagination']['next_url'].__len__() ):
	print "next_url is " + pictures_data['pagination']['next_url']
	print "data size=%d" % pictures_data['data'].__len__()

	for pic in pictures_data['data']:
		print pic['images']['standard_resolution']
		print pic['tags']
#		print pic
#		print pic['images']['standard_resolution']

	r = urllib2.urlopen( pictures_data['pagination']['next_url'] )
	pictures_data = json.loads( r.read() )



