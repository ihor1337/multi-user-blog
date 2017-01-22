from google.appengine.ext import db
from models import User
from models import Post


class Votes(db.Model):
    rating = db.IntegerProperty(default=0)
    post = db.ReferenceProperty(Post, required=True)
    voted_by = db.ReferenceProperty(User, required=True)