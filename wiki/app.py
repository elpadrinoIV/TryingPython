import handlers
import webapp2
import re

PAGE_RE = r'(/(?:[a-zA-Z0-9_-]+/?)*)'

application = webapp2.WSGIApplication([
    ('/login', handlers.LoginHandler),
    ('/logout', handlers.LogoutHandler),
    ('/signup', handlers.SignUpHandler),
    ('/_edit' + PAGE_RE, handlers.EditPageHandler),
    (PAGE_RE, handlers.WikiPageHandler),
    ],
    debug = True)
