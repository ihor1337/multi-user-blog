from google.appengine.ext import db
from models import User
from models import Post


class Comment(db.Model):
    post = db.ReferenceProperty(Post, required=True)
    owner = db.ReferenceProperty(User, required=True)
    comment = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)