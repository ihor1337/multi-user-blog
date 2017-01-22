from handlers import BlogHandler
from helpers import Decorators
from models import Comment
from models import BlogParent
from google.appengine.ext import db


class PostPage(BlogHandler):
    d = Decorators()

    @d.post_exists
    def get(self, post_id):
        post = self.get_post(post_id)
        c = Comment.all().filter('post =', post)
        p = BlogParent.get_by_key_name('key')
        likes = db.GqlQuery("SELECT * FROM Votes WHERE ANCESTOR IS :1 AND post = :2 ORDER BY rating DESC",
                            p, post).get()
        if not post:
            self.error(404)
            return
        if self.get_user():
            token = self.generate_csrf_token(self.user).split('.')[1]
            self.render('permalink.html', post=post, comment=c, likes=likes.rating, token=token)
        else:
            self.render('permalink.html', post=post, comment=c, likes=likes.rating)