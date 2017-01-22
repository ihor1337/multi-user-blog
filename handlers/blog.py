import os
import jinja2
import webapp2
from helpers import Helpers
from models import BlogParent
from models import User
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), '../templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


class BlogHandler(webapp2.RequestHandler):
    def write(self, *args, **kwargs):
        self.response.out.write(*args, **kwargs)

    def render_str(self, template, **params):
        params['user'] = self.user
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        h = Helpers()
        cookie_val = h.make_secure_val(val)
        self.response.headers.add_header('Set-Cookie', '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        h = Helpers()
        cookie_val = self.request.cookies.get(name)
        return cookie_val and h.check_secure_val(cookie_val)

    def login(self, user):
        self.generate_csrf_token(user)
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

# functions to generate and validate csrf tokens to prevent cross site request forgery
    def generate_csrf_token(self, user):
        h = Helpers()
        csrf_h = h.csrf_secret_hash(str(user.key().id()))
        token = h.make_hash(str(user.key().id()), csrf_h)
        self.response.headers.add_header('Set-Cookie', 'token=%s; Path=/' % token)
        return token

    def validate_csrf_token(self, user, form_token):
        h = Helpers()
        csrf_h = h.csrf_secret_hash(str(user.key().id()))
        cookie_token = self.request.cookies.get('token').split('.')[1]
        cookie_salt = self.request.cookies.get('token').split('.')[0]
        if cookie_token == form_token:
            cookie_val = cookie_salt + '.' + cookie_token
            form_val = cookie_salt + '.' + form_token
            return h.valid_hash(str(user.key().id()),
                              csrf_h, cookie_val) and h.valid_hash(str(user.key().id()),
                                                                 csrf_h, form_val)

    def get_post(self, post_id):
        p = BlogParent.get_by_key_name('key')
        key = db.Key.from_path('Post', int(post_id), parent=p.key())
        post = db.get(key)
        if post:
            return post
        else:
            return False

    def get_comment(self, post_id, comment_id):
        post = self.get_post(post_id)
        key = db.Key.from_path('Comment', int(comment_id), parent=post.key())
        comment = db.get(key)
        if post and comment:
            return comment
        else:
            return False

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))
        if self.user:
            print self.user.name
        else:
            print "No user logged in"

    def get_user(self):
        return self.user