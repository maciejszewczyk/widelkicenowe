from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor

ITEMS = 10


class Jobs4(ndb.Model):
    create_date = ndb.DateTimeProperty(auto_now_add=True)   # For the proper sorting
    view_date = ndb.DateProperty(auto_now_add=True)         # For view only
    jobTitle = ndb.StringProperty()
    minWage = ndb.IntegerProperty()
    maxWage = ndb.IntegerProperty()

    @classmethod
    def cursor_pagination(cls, prev_cursor_str, next_cursor_str):
        if not prev_cursor_str and not next_cursor_str:
            objects, next_cursor, more = cls.query().order(cls.create_date).fetch_page(ITEMS)
            prev_cursor_str = ''
            if next_cursor:
                next_cursor_str = next_cursor.urlsafe()
            else:
                next_cursor_str = ''
            next_ = True if more else False
            prev = False
        elif next_cursor_str:
            cursor = Cursor(urlsafe=next_cursor_str)
            objects, next_cursor, more = cls.query().order(cls.create_date).fetch_page(ITEMS, start_cursor=cursor)
            prev_cursor_str = next_cursor_str
            next_cursor_str = next_cursor.urlsafe()
            prev = True
            next_ = True if more else False
        elif prev_cursor_str:
            cursor = Cursor(urlsafe=prev_cursor_str)
            objects, next_cursor, more = cls.query().order(-cls.create_date).fetch_page(ITEMS, start_cursor=cursor)
            objects.reverse()
            next_cursor_str = prev_cursor_str
            prev_cursor_str = next_cursor.urlsafe()
            prev = True if more else False
            next_ = True

        return {'objects': objects, 'next_cursor': next_cursor_str, 'prev_cursor': prev_cursor_str, 'prev': prev,
                'next': next_}