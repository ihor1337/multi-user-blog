from google.appengine.ext import db
from models import User


class Post(db.Model):
    title = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)
    owner = db.ReferenceProperty(User, required=True)
    ratio = db.ListProperty(db.Key, required=True, indexed=True)
