from handlers import BlogHandler
from helpers import Decorators


class DeleteComment(BlogHandler):
    d = Decorators()

    @d.post_exists
    def get(self, post_id):
        self.redirect('/'+post_id)

    @d.user_logged_in
    @d.comment_exists
    @d.user_owns_comment
    def post(self, post_id, comment_id):
        if self.validate_csrf_token(self.user, form_token=self.request.get('token')):
            comment = self.get_comment(post_id, comment_id)
            comment.delete()
            self.redirect('/'+post_id)