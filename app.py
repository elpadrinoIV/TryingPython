import handlers
import webapp2

application = webapp2.WSGIApplication([
    ('/', handlers.MainPageHandler),
    ('/newpost', handlers.NewPostHandler),
    ('/(\d+)', handlers.PostHandler),
    ], debug = True)
