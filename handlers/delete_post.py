from handlers import BlogHandler
from helpers import Decorators


class DeletePost(BlogHandler):
    d = Decorators()

    @d.post_exists
    def get(self, post_id):
        self.redirect('/'+post_id)

    @d.user_logged_in
    @d.post_exists
    @d.user_owns_post
    def post(self, post_id):
        post = self.get_post(post_id)
        if self.validate_csrf_token(self.user, form_token=self.request.get('token')):
            post.delete()
            self.redirect('/')