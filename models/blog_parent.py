from google.appengine.ext import db


class BlogParent(db.Model):
    hey = db.StringProperty(required=True, default='lol')