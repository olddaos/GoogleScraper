#! /usr/bin/python
from celery_tasks import InstagramCrawler
from celery_tasks import FlickrCrawler


class FlickrPaginator:
	def __init__( self, query ):
		self.crawler  = FlickrCrawler()
		self.query    = query
		self.pages    = 0
		self.page     = 0

	def __iter__(self):
		return self

	def next(self):
		print "Next page is activated"
		pagination_struct = self.crawler.delay( self.query, self.page ).get()
		print pagination_struct
		self.pages = pagination_struct['pages']

		self.page  += 1
		if ( self.page < self.pages ):
			return pagination_struct['urls']
		else:
			raise StopIteration()

class InstaPaginator:
	def __init__( self, query ):
		self.crawler  = InstagramCrawler()
		self.query    = query
		self.next_url = None

	def __iter__(self):
		return self

	def next(self):
		print "Next page is activated"
		pagination_struct = self.crawler.delay( self.query, self.next_url ).get()
		print pagination_struct
		self.next_url = pagination_struct['next_url']

		# TODO: think of best way to raise StopIteration!
		return pagination_struct['urls']


pages = FlickrPaginator( 'eiffel' )

for i in xrange(10):
	print pages.next()
