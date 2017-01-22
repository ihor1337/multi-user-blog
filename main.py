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
import webapp2
from handlers import *

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
    ('/([0-9]+)/delete', DeletePost),
    ('/([0-9]+)/comment/([0-9]+)/delete', DeleteComment),
    ('/([0-9]+)/comment/([0-9]+)/edit', EditComment),
], debug=True)
