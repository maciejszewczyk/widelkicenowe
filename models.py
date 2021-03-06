from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor

ITEMS = 10

categoriesDict = dict(backend=1, fullstack=2, mobile=3, frontend=4, testing=5, devops=6, businessIntelligence=7,
                      projectManager=8, businessAnalyst=9)

class Jobs4(ndb.Model):
    create_date = ndb.DateTimeProperty(auto_now_add=True)   # For the proper sorting
    view_date = ndb.DateProperty(auto_now_add=True)         # For view only
    jobTitle = ndb.StringProperty()
    minWage = ndb.IntegerProperty()
    maxWage = ndb.IntegerProperty()
    category = ndb.IntegerProperty()

    @classmethod
    def cursor_pagination(cls, prev_cursor_str, next_cursor_str, category_str):
        ctg = True if category_str else False
        if ctg:
            cat_search = categoriesDict[category_str]
        if not prev_cursor_str and not next_cursor_str:
            # q.filter('title =', 'Imagine')
            # objects, next_cursor, more = cls.query().filter(cls.category == 1).order(-cls.view_date).fetch_page(ITEMS)
            if ctg:
                objects, next_cursor, more = cls.query().filter(cls.category == cat_search).order(-cls.view_date).fetch_page(ITEMS)
            else:
                objects, next_cursor, more = cls.query().order(-cls.view_date).fetch_page(ITEMS)
            prev_cursor_str = ''
            if next_cursor:
                next_cursor_str = next_cursor.urlsafe()
            else:
                next_cursor_str = ''
            next_ = True if more else False
            prev = False
        elif next_cursor_str:
            cursor = Cursor(urlsafe=next_cursor_str)
            if ctg:
                objects, next_cursor, more = cls.query().filter(cls.category == cat_search).order(-cls.view_date).fetch_page(ITEMS, start_cursor=cursor)
            else:
                objects, next_cursor, more = cls.query().order(-cls.view_date).fetch_page(ITEMS, start_cursor=cursor)
            prev_cursor_str = next_cursor_str
            next_cursor_str = next_cursor.urlsafe()
            prev = True
            next_ = True if more else False
        elif prev_cursor_str:
            cursor = Cursor(urlsafe=prev_cursor_str)
            if ctg:
                objects, next_cursor, more = cls.query().filter(cls.category == cat_search).order(cls.view_date).fetch_page(ITEMS, start_cursor=cursor)
            else:
                objects, next_cursor, more = cls.query().order(cls.view_date).fetch_page(ITEMS, start_cursor=cursor)
            objects.reverse()
            next_cursor_str = prev_cursor_str
            prev_cursor_str = next_cursor.urlsafe()
            prev = True if more else False
            next_ = True

        return {'objects': objects, 'next_cursor': next_cursor_str, 'prev_cursor': prev_cursor_str, 'prev': prev,
                'next': next_, 'category': category_str, 'ctg': ctg}