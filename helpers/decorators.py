
class Decorators():
    def post_exists(self, f):
        def wrap(self, post_id, *args):
            post = self.get_post(post_id)
            if post:
                return f(self, post_id, *args)
            else:
                self.error(404)
        return wrap

    def comment_exists(self, f):
        def wrap(self, post_id, comment_id):
            comment = self.get_comment(post_id, comment_id)
            if comment:
                return f(self, post_id, comment_id)
            else:
                self.redirect('/' + post_id)

        return wrap

    def user_logged_in(self, f):
        def wrap(self, *args, **kwargs):
            user = self.user
            if not user:
                self.redirect('/login')
            else:
                return f(self, *args, **kwargs)
        return wrap

    def user_owns_post(self, f):
        def wrap(self, post_id, *args):
            user = self.user
            post = self.get_post(post_id)
            if user.name == post.owner.name:
                return f(self, post_id, *args)
            else:
                self.redirect('/' + post_id)
        return wrap

    def user_owns_comment(self, f):
        def wrap(self, post_id, comment_id):
            comment = self.get_comment(post_id, comment_id)
            if self.user.name == comment.owner.name:
                return f(self, post_id, comment_id)
            else:
                self.redirect('/' + post_id)
        return wrap