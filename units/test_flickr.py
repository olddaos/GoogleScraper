#! /usr/bin/python
from flickr_api.api import flickr
import flickr_api
import json
import re
flickr_api.set_keys(api_key = "a1c5cc6b3d6c7bad6ceff207e2d901b2", api_secret = "7ee7e077ffb72800" )
res = flickr.photos.search( text = 'eiffel', per_page=500, page=0, format = 'json', extras="url_m,geo,tags,views,date_taken" )
m  = re.search(r'jsonFlickrApi\((.+)\)', res)
reply = json.loads( m.group(1) )

print reply

for photo in reply['photos']['photo']:
	print photo['url_m']
