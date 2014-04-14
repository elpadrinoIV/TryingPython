import handlers
import webapp2

application = webapp2.WSGIApplication([
    ('/', handlers.MainPageHandler),
    ('/newpost', handlers.NewPostHandler),
    ('/signup', handlers.SignUpHandler),
    ('/welcome', handlers.WelcomeHandler),
    ('/(\d+)', handlers.PostHandler),
    ], debug = True)
