from handlers import BlogHandler
from helpers import Decorators
from models import Post
from models import BlogParent
from models import Votes


class NewPost(BlogHandler):
    d = Decorators()

    @d.user_logged_in
    def get(self):
        token = self.generate_csrf_token(self.user).split('.')[1]
        self.render('newpost.html', token=token)

    @d.user_logged_in
    def post(self):
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