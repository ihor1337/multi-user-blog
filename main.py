#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import jinja2
import re
import hashlib
import random
import hmac
import webapp2
from string import letters
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")


def valid_username(username):
    return username and USER_RE.match(username)


PASS_RE = re.compile(r"^.{3,20}$")


def valid_password(password):
    return password and PASS_RE.match(password)


EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')


def valid_email(email):
    return not email or EMAIL_RE.match(email)


secret = "Iamsooooosecret!"
csrf_sercret = "I_am_a_very_secret_CSRF_key_to_generate_a_secure_token"


def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())


def csrf_secret_hash(user):
    return hmac.new(user, csrf_sercret).hexdigest()


def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val


class BlogHandler(webapp2.RequestHandler):
    def write(self, *args, **kwargs):
        self.response.out.write(*args, **kwargs)

    def render_str(self, template, **params):
        params['user'] = self.user
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header('Set-Cookie', '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.generate_csrf_token(user)
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def generate_csrf_token(self, user):
        csrf_h = csrf_secret_hash(str(user.key().id()))
        token = make_hash(str(user.key().id()), csrf_h)
        self.response.headers.add_header('Set-Cookie', 'token=%s; Path=/' % token)
        return token

    def validate_csrf_token(self, user, form_token):
        csrf_h = csrf_secret_hash(str(user.key().id()))
        cookie_token = self.request.cookies.get('token').split('.')[1]
        cookie_salt = self.request.cookies.get('token').split('.')[0]
        if cookie_token == form_token:
            cookie_val = cookie_salt + '.' + cookie_token
            form_val = cookie_salt + '.' + form_token
            return valid_hash(str(user.key().id()),
                              csrf_h, cookie_val) and valid_hash(str(user.key().id()),
                                                                 csrf_h, form_val)

    def get_post(self, post_id):
        p = BlogParent.get_by_key_name('key')
        key = db.Key.from_path('Post', int(post_id), parent=p.key())
        post = db.get(key)
        return post

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

def make_salt(length=5):
    return ''.join(random.choice(letters) for x in xrange(length))


def make_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s.%s' % (salt, h)


def valid_hash(name, password, h):
    salt = h.split('.')[0]
    return h == make_hash(name, password, salt)


def users_key(group='default'):
    return db.Key.from_path('users', group)


class User(db.Model):
    name = db.StringProperty(required=True)
    pw_hash = db.StringProperty(required=True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid)

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email=None):
        pw_hash = make_hash(name, pw)
        return User(name=name, pw_hash=pw_hash, email=email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_hash(name, pw, u.pw_hash):
            return u


class SignupHandler(BlogHandler):
    def get(self):
        self.render('signup.html')

    def post(self):
        is_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username=self.username, email=self.email)

        if not valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            is_error = True

        if not valid_password(self.password):
            params['error_password'] = "That wasn't a valid password."
            is_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            is_error = True

        if not valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            is_error = True

        if is_error:
            self.render('signup.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        raise NotImplementedError


class Register(SignupHandler):
    def done(self):
        u = User.by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('signup.html', error_username=msg)
        else:
            u = User.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.redirect('/')


class Login(BlogHandler):
    def get(self):
        self.render('login.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect('/')
        else:
            msg = 'Invalid login'
            self.render('login.html', error=msg)


class Logout(BlogHandler):
    def get(self):
        self.logout()
        self.redirect('/')


class BlogParent(db.Model):
    hey = db.StringProperty(required=True, default='lol')


class Post(db.Model):
    title = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)
    owner = db.ReferenceProperty(User, required=True)
    ratio = db.ListProperty(db.Key, required=True, indexed=True)

    def render(self, token):
        self.render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p=self, token=token)


class Votes(db.Model):
    rating = db.IntegerProperty(default=0)
    post = db.ReferenceProperty(Post, required=True)
    voted_by = db.ReferenceProperty(User, required=True)


class Comment(db.Model):
    post = db.ReferenceProperty(Post, required=True)
    owner = db.ReferenceProperty(User, required=True)
    comment = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)


class CommentHandler(BlogHandler):
    def post(self, post_id):
        comment = self.request.get('comment')
        author = self.user.key()
        post = self.get_post(post_id)
        c = Comment(post=post, comment=comment, owner=author, parent=post)
        c.put()
        self.redirect('/'+post_id)

class FrontPage(BlogHandler):
    def get(self):
        posts = Post.all().order('-created')
        c = Comment
        self.render('front.html', posts=posts, c=c)


class PostPage(BlogHandler):
    def get(self, post_id):
        post = self.get_post(post_id)
        comment = Comment.all().filter('post =', post)
        p = BlogParent.get_by_key_name('key')
        print p.key()
        likes = db.GqlQuery("SELECT * FROM Votes WHERE ANCESTOR IS :1 ORDER BY rating DESC", p).get()
        print likes
        #print likes
        if not post:
            self.error(404)
            return
        token = self.generate_csrf_token(self.user).split('.')[1]
        self.render('permalink.html', post=post, comment=comment, likes=likes.rating, token=token)


class NewPost(BlogHandler):
    def get(self):
        token = self.generate_csrf_token(self.user).split('.')[1]
        self.render('newpost.html', token=token)

    def post(self):
        if not self.user:
            self.redirect('/login')
        else:
            title = self.request.get('title')
            body = self.request.get('content')
            form_token = self.request.get('token')
            user = self.user.key()
            if self.validate_csrf_token(self.user, form_token):
                if title and body:
                    parent = BlogParent.get_or_insert('key', hey='lol')
                    p = Post(title=title, content=body, owner=user, parent=parent)
                    p.put()
                    l = Votes(post=p.key(), voted_by=user, rating=0, parent=p.key())
                    l.put()
                    self.redirect('/%s' % str(p.key().id()))
                else:
                    error = "Please specify both title and body of the post!"
                    self.render('newpost.html', title=title, body=body, error=error)
            else:
                self.error(403)


class Rating(BlogHandler):
    def get(self, post_id):
        self.redirect('/' + post_id)

    def post(self, post_id):
        post = self.get_post(post_id)
        post_author_id = post.owner.key().id()
        current_user_id = self.user.key().id()
        like = db.GqlQuery("SELECT * FROM Votes WHERE ANCESTOR IS :1 ORDER BY rating DESC", users_key()).get()
        form_token = self.request.get('token')
        if int(post_author_id) == int(current_user_id):
            error = "Sorry, you can't like your own post!"
            self.render('permalink.html', post=post, error=error, likes=like.rating)
        elif like.voted_by.key().id() == current_user_id:
            error = "You can not like post more than once!"
            self.render('permalink.html', post=post, error=error, likes=like.rating)
        else:
            if self.validate_csrf_token(self.user, form_token):
                rating = int(like.rating) + 1
                new_ratio = Votes(post=post, rating=rating, voted_by=self.user.key(), parent=post)
                new_ratio.put()
                self.redirect('/' + post_id)
            else:
                self.error(403)


class EditPost(BlogHandler):
    def get(self, post_id):
        token = self.generate_csrf_token(self.user).split('.')[1]
        post = self.get_post(post_id)
        post_author_id = post.owner.key().id()
        current_user_id = self.user.key().id()
        if int(post_author_id) != int(current_user_id):
            self.redirect('/'+post_id)
        self.render('newpost.html', token=token, post=post)

    def post(self, post_id):
        post = self.get_post(post_id)
        post_author_id = post.owner.key().id()
        current_user_id = self.user.key().id()
        if int(post_author_id) == int(current_user_id):
            new_title = self.request.get('title')
            new_body = self.request.get('content')
            form_token = self.request.get('token')
            if self.validate_csrf_token(self.user, form_token):
                post.title = new_title
                post.content = new_body
                post.put()
                self.redirect('/'+post_id)


class DeletePost(BlogHandler):
    def get(self, post_id):
        self.redirect('/'+post_id)

    def post(self, post_id):
        post = self.get_post(post_id)
        print post
        print self.user.key().id()
        print self.user.name
        if self.user.key().id() == post.owner.key().id():
            if self.validate_csrf_token(self.user, form_token=self.request.get('token')):
                post.delete()
                self.redirect('/')

app = webapp2.WSGIApplication([
    ('/', FrontPage),
    ('/signup', Register),
    ('/login', Login),
    ('/logout', Logout),
    ('/([0-9]+)', PostPage),
    ('/([0-9]+)/comment', CommentHandler),
    ('/newpost', NewPost),
    ('/([0-9]+)/rate', Rating),
    ('/([0-9]+)/edit', EditPost),
    ('/([0-9]+)/delete', DeletePost)
], debug=True)
