import handlers
import webapp2

application = webapp2.WSGIApplication([
    ('/', handlers.MainPageHandler),
    ('/login', handlers.LoginHandler),
    ('/logout', handlers.LogoutHandler),
    ('/newpost', handlers.NewPostHandler),
    ('/signup', handlers.SignUpHandler),
    ('/welcome', handlers.WelcomeHandler),
    ('/(\d+)', handlers.PostHandler),
    ], debug = True)
