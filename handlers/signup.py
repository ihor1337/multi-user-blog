from handlers import BlogHandler
from helpers import Helpers


class SignupHandler(BlogHandler):
    def get(self):
        self.render('signup.html')

    def post(self):
        is_error = False
        h = Helpers()
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username=self.username, email=self.email)

        if not h.valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            is_error = True

        if not h.valid_password(self.password):
            params['error_password'] = "That wasn't a valid password."
            is_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            is_error = True

        if not h.valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            is_error = True

        if is_error:
            self.render('signup.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        raise NotImplementedError