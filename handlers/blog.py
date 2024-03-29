# -*- coding: utf-8 -*-

import datetime
import config
import PyRSS2Gen
import re

import webapp2

from google.appengine.api import memcache

import blogview as view
import logging
import errors

from classes import *
from lib.myhandler import MyHandler
from lib.mycachehandler import MyCacheHandler

def slugify(value):
    """
    Adapted from Django's django.template.defaultfilters.slugify.
    """
    import unicodedata
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return re.sub('[-\s]+', '-', value)

class IndexHandler(MyHandler):

    def head(self):
        self.response.set_status(200)
        return

    def get(self):
        try:
            query = Post.all()
            query.order('-pub_date')

            template_values = {'page_title': 'Home'}
            page = view.Page()
            page.render_paginated_query(self, query, 'posts', 'templates/blog/index.html', template_values)
        except:
            return errors.overquota(self)

class PostHandler(MyHandler):
    
    pattern = re.compile("<!--STARTCUTTINGPART-->(.*)<!--ENDCUTTINGPART-->", re.S)

    def head(self, year, month, day, slug):
        self.response.set_status(200)
        return

    def get(self, year, month, day, slug):
	
        memcache_label = "post:"+year+month+day+slug
        archive = memcache.get(memcache_label)
        if archive is not None:
             logging.info("Blog post haz memcache! Using it")
             self.response.out.write(archive)
             return
  
        year = int(year)
        month = int(month)
        day = int(day)
 

        # Build the time span to check for the given slug
        start_date = datetime.datetime(year, month, day)
        time_delta = datetime.timedelta(days=1)
        end_date = start_date + time_delta

        # Create a query to check for slug uniqueness in the specified time span
        query = Post.all()
        query.filter('pub_date >= ', start_date)
        query.filter('pub_date < ', end_date)
        query.filter('slug = ', slug)

        post = query.get()

        if post == None:
            page = view.Page()
            page.render_error(self, 404)
        else:
            template_values = {
                'post': post,
                }

            page = view.Page()
            html = page.rendertostring(self, 'templates/blog/post.html', template_values)
            # antigamente, tinha: 
            #page.render(self, 'templates/blog/post.html', template_values)
            logging.info("Blog post inserted into memcache.")
            memcache.set(memcache_label, html,time=86400)
            self.response.out.write(html)
            	
class TagHandler(MyHandler):

    def head(self, tag):
        self.response.set_status(200)
        return

    def get(self, tag):
        query = Post.all()
        query.filter('tags = ', tag)
        query.order('-pub_date')

        template_values = {'page_title': 'Posts tagged "%s"' % (tag),
                           'page_description': 'Posts tagged "%s"' % (tag),
                          }

        page = view.Page()
        page.render_paginated_query(self, query, 'posts', 'templates/blog/index.html', template_values)

class YearHandler(MyHandler):

    def head(self, year):
        self.response.set_status(200)
        return

    def get(self, year):
        year = int(year)

        # Build the time span to check for posts
        start_date = datetime.datetime(year, 1, 1)
        end_date = datetime.datetime(year + 1, 1, 1)

        # Create a query to find posts in the given time span
        query = Post.all()
        query.filter('pub_date >= ', start_date)
        query.filter('pub_date < ', end_date)
        query.order('-pub_date')

        template_values = {'page_title': 'Yearly Post Archive: %d' % (year),
                           'page_description': 'Yearly Post Archive: %d' % (year),
                          }

        page = view.Page()
        page.render_paginated_query(self, query, 'posts', 'templates/blog/index.html', template_values)

class MonthHandler(MyHandler):

    def head(self, year, month):
        self.response.set_status(200)
        return

    def get(self, year, month):
        year = int(year)
        month = int(month)

        # Build the time span to check for posts
        start_date = datetime.datetime(year, month, 1)
        end_year = year if month < 12 else year + 1
        end_month = month + 1 if month < 12 else 1
        end_date = datetime.datetime(end_year, end_month, 1)

        # Create a query to find posts in the given time span
        query = Post.all()
        query.filter('pub_date >= ', start_date)
        query.filter('pub_date < ', end_date)
        query.order('-pub_date')

        month_text = start_date.strftime('%B %Y')
        template_values = {'page_title': 'Monthly Post Archive: %s' % (month_text),
                           'page_description': 'Monthly Post Archive: %s' % (month_text),
                          }

        page = view.Page()
        page.render_paginated_query(self, query, 'posts', 'templates/blog/index.html', template_values)

class DayHandler(MyHandler):

    def head(self, year, month, day):
        self.response.set_status(200)
        return

    def get(self, year, month, day):
        year = int(year)
        month = int(month)
        day = int(day)

        # Build the time span to check for posts
        start_date = datetime.datetime(year, month, day)
        time_delta = datetime.timedelta(days=1)
        end_date = start_date + time_delta

        # Create a query to find posts in the given time span
        query = Post.all()
        query.filter('pub_date >= ', start_date)
        query.filter('pub_date < ', end_date)
        query.order('-pub_date')

        day_text = start_date.strftime('%x')
        template_values = {'page_title': 'Daily Post Archive: %s' % (day_text),
                           'page_description': 'Daily Post Archive: %s' % (day_text),
                          }

        page = view.Page()
        page.render_paginated_query(self, query, 'posts', 'templates/blog/index.html', template_values)

class RSS2Handler(MyCacheHandler): 

	cache_namespace = "rss"
	cache_url = "/rss"

        def head(self, tag):
            self.response.set_status(200)
            return

	def get(self):
		self.checkCacheFreshen()
		self.requestHandler()
		return 
	
	def checkCacheFreshen(self):
		data_cache = None # data do HTML gerado em cache
		
		self.softcache_content_html =  memcache.get(self.cache_url, namespace=self.cache_namespace)
		if self.softcache_content_html:
			data_cache = self.softcache_content_html['date']
		else:
			hardcache_content_html = CacheHTML.all().filter("cch_url = ",self.cache_url).get()
			if hardcache_content_html:
				data_cache = hardcache_content_html.cch_date
		
		# não é mto eficiente
		blog_date = Post.all().order('-pub_date').get().pub_date

		if data_cache and blog_date > data_cache:
			self.refreshen_cache = True

	def renderDados(self):
        
		query = Post.all().order('-pub_date')
		posts = query.fetch(10)

		rss_items = []
		for post in posts:
			item = PyRSS2Gen.RSSItem(
				title=post.title,
				link="%s%s" % (config.SETTINGS['url'], post.get_absolute_url()),
				#description=post.excerpt_html or post.body_html,
				description=post.body_html,  
				guid=PyRSS2Gen.Guid("%s%s" % (config.SETTINGS['url'], post.get_absolute_url())),
				pubDate=post.pub_date
				)
			rss_items.append(item)

		rss = PyRSS2Gen.RSS2(
			title=config.SETTINGS['title'],
			link=config.SETTINGS['url'],
			description=config.SETTINGS['description'],
			lastBuildDate=datetime.datetime.now(),
			items=rss_items
			)
		return rss

	def renderHTML(self):
		return self.dados.to_xml()

	def renderTitle(self):
		return config.SETTINGS["maintitle"]
	
