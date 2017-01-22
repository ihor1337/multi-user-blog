from handlers import BlogHandler
from helpers import Decorators
from models import Comment
from google.appengine.ext import db


class EditComment(BlogHandler):
    d = Decorators()

    @d.post_exists
    def get(self, post_id):
        self.redirect('/' + post_id)

    @d.user_logged_in
    @d.comment_exists
    @d.user_owns_comment
    def post(self, post_id, comment_id):
        post = self.get_post(post_id)
        new_comment = self.request.get('comment')
        c = Comment.all().filter('post =', post)
        likes = db.GqlQuery("SELECT * FROM Votes WHERE ANCESTOR IS :1 ORDER BY rating DESC", post).get()
        if self.validate_csrf_token(self.user, form_token=self.request.get('token')):
            if new_comment:
                c = self.get_comment(post_id, comment_id)
                c.comment = new_comment
                c.put()
                self.redirect('/' + post_id)
            else:
                comment_error = "Sorry, you can not post an empty comment!"
                token = self.generate_csrf_token(self.user).split('.')[1]
                self.render('permalink.html', post=post, comment=c, likes=likes.rating, token=token,
                            comment_error=comment_error)
        else:
            self.error(403)