from handlers import BlogHandler
from helpers import Decorators
from models import Comment
from models import Votes
from google.appengine.ext import db


class Rating(BlogHandler):
    d = Decorators()

    @d.post_exists
    def get(self, post_id):
        self.redirect('/' + post_id)

    @d.user_logged_in
    @d.post_exists
    def post(self, post_id):
        post = self.get_post(post_id)
        post_author_id = post.owner.key().id()
        current_user_id = self.user.key().id()
        c = Comment.all().filter('post =', post)
        like = db.GqlQuery("SELECT * FROM Votes WHERE ANCESTOR IS :1 ORDER BY rating DESC", post).get()
        form_token = self.request.get('token')
        if int(post_author_id) == int(current_user_id):
            error = "Sorry, you can't like your own post!"
            self.render('permalink.html', post=post, error=error, likes=like.rating, comment=c)
        elif like.voted_by.key().id() == current_user_id:
            error = "You can not like post more than once!"
            self.render('permalink.html', post=post, error=error, likes=like.rating, comment=c)
        else:
            if self.validate_csrf_token(self.user, form_token):
                rating = int(like.rating) + 1
                new_ratio = Votes(post=post, rating=rating, voted_by=self.user.key(), parent=post)
                new_ratio.put()
                self.redirect('/' + post_id)
            else:
                self.error(403)