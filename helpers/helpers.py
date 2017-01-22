import hashlib
import random
from string import letters
import re
import hmac

class Helpers():

    USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
    PASS_RE = re.compile(r"^.{3,20}$")
    EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')

    secret = "Iamsooooosecret!"
    csrf_sercret = "I_am_a_very_secret_CSRF_key_to_generate_a_secure_token"

    def make_salt(self, length=5):
        return ''.join(random.choice(letters) for x in xrange(length))


    def make_hash(self, name, pw, salt=None):
        if not salt:
            salt = self.make_salt()
        h = hashlib.sha256(name + pw + salt).hexdigest()
        return '%s.%s' % (salt, h)


    def valid_hash(self, name, password, h):
        salt = h.split('.')[0]
        return h == self.make_hash(name, password, salt)

    def valid_username(self, username):
        return username and Helpers.USER_RE.match(username)

    def valid_password(self, password):
        return password and Helpers.PASS_RE.match(password)

    def valid_email(self, email):
        return not email or Helpers.EMAIL_RE.match(email)


    def make_secure_val(self, val):
        return '%s|%s' % (val, hmac.new(Helpers.secret, val).hexdigest())

    def csrf_secret_hash(self, user):
        return hmac.new(user, Helpers.csrf_sercret).hexdigest()

    def check_secure_val(self, secure_val):
        val = secure_val.split('|')[0]
        if secure_val == self.make_secure_val(val):
            return val

    # def users_key(group='default'):
    #     return db.Key.from_path('users', group)