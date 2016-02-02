#  Search systems scrapers ( Google, Bing ) 

A bunch of Celery-based crawlers and scrapers, written solely for research purposes
Included are Google, Bing, Flickr and Instagram

Features:
* Depending on a number of nodes up to 128 pics/sec downloading speed is achievable ( just getting static pics )
* Effortless scalability thanks to Celery ( just increase concurrency parameter in Celery and you added more nodes )
* Adding or removing new crawlers, as well as updating code without stopping crawling
* Crawling farm could be easily geographically distributed thanks to Celery federation mechanism
* All obtained pictures could be saved to MongoDB as a blobs ( or you can mount GridFS and enjoy distributed image filesystem )

Also in nearest plans:
* Support Flash-based sites crawling ( cracking, actually :-) using xdotool, OpenCV and all this stuff  
* User behavior emulation to fool antiscraping protection of most good sites

Disclaimer: this stuff was written just as a capstone project in computer security and have no intention to really distribute warez or things like that. Use it at your own risk!

Usage
-----

*FIRST obtain your own access tokens in Instagram and Flickr crawlers ( see source to know where to put them)!*

Actually, we have two sorts of Celery tasks:
1. URL discoverer
2. URL fetcher

And both are independent: you can launch 100 URL fetchers and 10 URL discoverers, for example.
URL discoverer takes as input a request to search engine ( or Flickr ) such as 'eiffel tower' and at the output it produces a list of URLs from engine.
It then queues these URLs for actual downloading by sending message with URL to Celery GetURL tasks.

**Example Usage**
    First start Celery: ``./launch_happiness.sh``
    Then write code like that ( or use shipped code in test_celery.py ):
    ```python
	class InstaPaginator:
		def __init__( self, query ):
			self.crawler  = InstagramCrawler()
			self.query    = query
			self.next_url = None

		def __iter__(self):
			return self

		def next(self):
			pagination_struct = self.crawler.delay( self.query, self.next_url ).get()
			self.next_url = pagination_struct['next_url']

			return pagination_struct['urls']

        # Here we instantiate the paginator, which will discover URLs for us 
	pages = FlickrPaginator( 'eiffel' )

	# Here we iterate over returned pages and send picture URLs to GetURL task 
	for i in xrange(10):
		print pages.next()

    ```

Requirements
------------
* Celery
* python instagram API
* Selenium WebDriver
* Xvfb ( UNIX headless X )
* MongoDB

(may have to be independently installed)


Installation
------------
#. git clone GoogleScraper 

