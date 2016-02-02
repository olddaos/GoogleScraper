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

# WARNING!!! This crawler is illegal! It's just a screenscraping hack!
# Expect this gets broken some day ( when Google will change it's HTML markup )
#
class GoogleCrawler(Task):
        def __init__(self):
                self.queue  = 'google_crawler'

        def run( self, query ):
                try:
                        driver = webdriver.Firefox()
                        driver.get("http://images.google.com")
                        search_bar = driver.find_element_by_id("lst-ib")

                        # this emulates sending request
                        search_bar.send_keys( query ) #cat.decode('utf-8'))
                        driver.find_element_by_name("btnG").click()

                        # wait for a page to load completely
                        # TODO: add multiple scrolls to paginate
                        time.sleep(3)
                        driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")

                        # wait till the scrolled page will arrive
                        time.sleep(3)

                        image_links = driver.find_elements_by_xpath("//div[@id='rg_s']/div[@class='rg_di rg_el']/a[@class='rg_l']")
                        for image_link in image_links:
                                m = re.search(r'mgres\?imgurl=(.+?)\&imgrefurl=', image_link.get_attribute('href'))
                                print "Got a pic from Google: " + m.group( 1 ) #image_link.get_attribute('href')
                                # save URLs from href anchors
                                GetURL().delay( m.group( 1 ), tags=query )

                except StaleElementReferenceException as e:
                        print "Err: stale element reference exception: " + e.message

