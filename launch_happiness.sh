#! /bin/bash

FETCH_CONCURRENCY=10
CRAWLERS_CONCURRENCY=2

# Virtual screen number ( used by Google crawler )
export DISPLAY=:10

# Start virtual screen without authorization
sudo Xvfb :10 -ac &

celery worker -D -c $FETCH_CONCURRENCY -Q urls_queue --broker=redis://54.221.232.248:6379 -A celery_tasks --loglevel=info --pidfile=fetcher.pid

celery worker -D -c $CRAWLERS_CONCURRENCY -Q bing_crawler --broker=redis://54.221.232.248:6379 -A celery_tasks --loglevel=info --pidfile=bing_crawler.pid
celery worker -D -c $CRAWLERS_CONCURRENCY -Q flickr_crawler --broker=redis://54.221.232.248:6379 -A celery_tasks --loglevel=info --pidfile=flickr_crawler.pid
celery worker -D -c $CRAWLERS_CONCURRENCY -Q instagram_crawler --broker=redis://54.221.232.248:6379 -A celery_tasks --loglevel=info --pidfile=instagram_crawler.pid
celery worker -D -c $CRAWLERS_CONCURRENCY -Q google_crawler --broker=redis://54.221.232.248:6379 -A celery_tasks --loglevel=info --pidfile=instagram_crawler.pid
