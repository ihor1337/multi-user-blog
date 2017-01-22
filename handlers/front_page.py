from handlers import BlogHandler
from models import Post
from models import BlogParent
from models import Comment
from google.appengine.ext import db


class FrontPage(BlogHandler):
    def get(self):
        p = db.Query(Post)
        a = BlogParent.get_or_insert('key', hey='lol')
        p.ancestor(a.key())
        p.order('-created')
        c = Comment
        self.render('front.html', posts=p, c=c)