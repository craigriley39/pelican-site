#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals
import os
LOG_FILTER = [('logging.debug')]
AUTHOR = u'Craig Riley'
SITENAME = u'Blog About Nothin.'
SITEURL = 'http://justlearningdjango.com'

#########
# PATHS #
#########
BASEDIR = '/home/criley/pelican'
PATH = 'content'
DEFAULT_DATE_FORMAT = '%a %d %B %Y'
DEFAULT_DATE = 'fs'
PAGE_PATHS = ['pages']

### Time and Language ###
TIMEZONE = 'America/Denver'
DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (('Pelican', 'http://getpelican.com/'),
         ('Python.org', 'http://python.org/'),
         ('Jinja2', 'http://jinja.pocoo.org/'),
)

# Social widget
SOCIAL = (('Github', 'https://github.com/craigriley39'),
          )

DEFAULT_PAGINATION = 20

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

THEME = 'pelican-blueidea'
SUMMARY_MAX_LENGTH = 50

STATIC_PATHS = ['images']

PLUGIN_PATH = 'plugins/'
PLUGINS = ['tipue_search',]

#MENUITEMS = ( ('Archive','/archives.html'), ('Search', '/search.html') ,)
TEMPLATE_PAGES = {'extras/search.html' : 'search.html' }
DISPLAY_SEARCH_FORM = True
INDEX_SAVE_AS = 'blog_index.html'
