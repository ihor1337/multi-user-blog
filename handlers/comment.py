from handlers import BlogHandler
from models import BlogParent
from models import Comment
from helpers import Decorators
from google.appengine.ext import db


class CommentHandler(BlogHandler):
    d = Decorators()

    @d.user_logged_in
    @d.post_exists
    def post(self, post_id):
        comment = self.request.get('comment')
        form_token = self.request.get('token')
        author = self.user.key()
        post = self.get_post(post_id)
        c = Comment.all().filter('post =', post)
        p = BlogParent.get_by_key_name('key')
        likes = db.GqlQuery("SELECT * FROM Votes WHERE ANCESTOR IS :1 AND post = :2 ORDER BY rating DESC", p,
                            post).get()
        if self.validate_csrf_token(self.user, form_token):
            if comment:
                c = Comment(post=post, comment=comment, owner=author, parent=post)
                c.put()
                self.redirect('/' + post_id)
            else:
                comment_error = "Sorry, you can not post an empty comment!"
                token = self.generate_csrf_token(self.user).split('.')[1]
                self.render('permalink.html', post=post, comment=c, likes=likes.rating, token=token,
                            comment_error=comment_error)
        else:
            self.error(403)