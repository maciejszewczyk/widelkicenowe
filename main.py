#!/usr/bin/env python

import os

import webapp2
import jinja2
import feedparser
import urllib2
import json
from models import Jobs4
import datetime


categoriesDict = dict(backend=1, fullstack=2, mobile=3, frontend=4, testing=5, devops=6, businessIntelligence=7,
                      projectManager=8, businessAnalyst=9)
baseURL = 'https://nofluffjobs.com/api/postingNew'
userAgent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36'
currency = 'PLN'
duration = 'Month'
employment = 'Permanent'
city = ('Warsaw', 'Warszawa')
now = datetime.datetime.now()
item = int(now.hour) % 9
element = categoriesDict.keys()[item]

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class NewPost(webapp2.RequestHandler):
    def get(self):
        now = datetime.datetime.now()
        item = int(now.hour) % 9
        element = categoriesDict.keys()[item]
        self.response.write('{}{}{}'.format(item, '/', element))


class CursorPaginationHandler(webapp2.RequestHandler):
    def get(self):
        category = self.request.get('category', '')
        prev_cursor = self.request.get('prev_cursor', '')
        next_cursor = self.request.get('next_cursor', '')
        res = Jobs4.cursor_pagination(prev_cursor, next_cursor, category)
        template = JINJA_ENVIRONMENT.get_template('templates/cursor_pagination.html')
        self.response.write(template.render(res))


class UpdateJobOffers(webapp2.RequestHandler):
    def post(self):
        self.abort(405, headers=[('Allow', 'GET')])

    def get(self):
        if 'X-AppEngine-Cron' not in self.request.headers:
            self.error(403)
        ret = feedparser.parse('https://nofluffjobs.com/rss/{}'.format(element))
        for post in ret.entries:
            if post.link[-8:]:
                req = urllib2.Request('{}{}{}'.format(baseURL, '/', post.link[-8:]))
                req.add_header('User-Agent', userAgent)
                result = urllib2.urlopen(req).read()
                jo = json.loads(result)
                essentials = jo['posting']['essentials']
                title = jo['posting']['title']
                company = jo['posting']['company']
                try:
                    salary_duration = essentials['salaryDuration']  # Month
                    salary_currency = essentials['salaryCurrency']  # PLN
                    employment_type = essentials['employmentType']  # Permanent
                    salary_from = essentials['salaryFrom']  # 5000
                    location_city = essentials['locationCity']  # Warsaw
                    salary_to = essentials['salaryTo']  # 10000
                    job_title = title['title']  # JavaScript
                    job_level = title['level']  # Developer
                    job_company = company['name']  # Company
                except KeyError:
                    pass
                else:
                    # Tylko: wynagrodzenie miesieczne, w PLN brutto, umowa o prace, w Warszawie
                    if duration == salary_duration and salary_currency == currency and employment_type == employment and location_city in city:
                        Jobs4.get_or_insert(post.link[-8:],
                                            jobTitle='{} {} @ {}'.format(job_title, job_level, job_company),
                                            minWage=salary_from,
                                            maxWage=salary_to,
                                            category=categoriesDict[element])


app = webapp2.WSGIApplication([
    ('/', CursorPaginationHandler),
    ('/update', UpdateJobOffers),
    ('/new', NewPost),
], debug=True)
