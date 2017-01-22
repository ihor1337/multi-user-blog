from handlers import BlogHandler
from helpers import Decorators


class EditPost(BlogHandler):
    d = Decorators()

    @d.user_logged_in
    @d.post_exists
    @d.user_owns_post
    def get(self, post_id):
        token = self.generate_csrf_token(self.user).split('.')[1]
        post = self.get_post(post_id)
        self.render('newpost.html', token=token, post=post)

    @d.user_logged_in
    @d.post_exists
    @d.user_owns_post
    def post(self, post_id):
        post = self.get_post(post_id)
        new_title = self.request.get('title')
        new_body = self.request.get('content')
        form_token = self.request.get('token')
        if new_title and new_body:
            if self.validate_csrf_token(self.user, form_token):
                post.title = new_title
                post.content = new_body
                post.put()
                self.redirect('/'+post_id)
            else:
                self.render('newpost.html', post=post, error='Please add title and body')
