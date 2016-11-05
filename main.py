#!/usr/bin/env python

import os

import webapp2
import jinja2
import feedparser
import re
from models import Jobs4


currency = 'PLN'
city = ('Warsaw', 'Warszawa')

rloc = re.compile(r'<b>Location:</b> (\w+)', re.UNICODE)
rsal = re.compile(r'<b>Salary:</b> from (\d+) to (\d+) ({})'.format(currency))

d = feedparser.parse('https://nofluffjobs.com/rss/projectManager')

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class CursorPaginationHandler(webapp2.RequestHandler):
    def get(self):
        prev_cursor = self.request.get('prev_cursor', '')
        next_cursor = self.request.get('next_cursor', '')
        res = Jobs4.cursor_pagination(prev_cursor, next_cursor)
        template = JINJA_ENVIRONMENT.get_template('templates/cursor_pagination.html')
        self.response.write(template.render(res))


class UpdateJobOffers(webapp2.RequestHandler):
    def post(self):
        self.abort(405, headers=[('Allow', 'GET')])

    def get(self):
        if 'X-AppEngine-Cron' not in self.request.headers:
            self.error(403)
        for post in d.entries:
            for c in rloc.findall(post.description):
                if c in city:  # Warsaw or Warszawa
                    for s in rsal.findall(post.description):
                        if s[2] == currency:  # PLN
                            Jobs4.get_or_insert(post.link[-8:],
                                                jobTitle=post.title,
                                                minWage=int(s[0]),
                                                maxWage=int(s[1]))

app = webapp2.WSGIApplication([
    ('/', CursorPaginationHandler),
    ('/update', UpdateJobOffers),
], debug=True)
