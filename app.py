import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)


class MainPageHandler(Handler):
    def render_front(self, posts=""):
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 10")

        self.render("front.html", posts=posts)

    def get(self):
        self.render_front()

    
class NewPostHandler(Handler):
    def render_page(self, subject="", content="", error=""):
        #self.render("newpost.html", subject, content, error)
        self.render("newpost.html", subject=subject, content=content, error=error)

    def get(self):
        self.render_page()

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            p = Post(subject = subject, content=content)
            p.put()

            url = "/" + str(p.key().id())
            self.redirect(url)
        else:
            error = "Oops, we need both subject and content"
            self.render_page(subject, content, error)

class PostHandler(Handler):
    def get(self, number):
        p = db.get_by_id(number)
        self.render("post.html", post=p)


application = webapp2.WSGIApplication([
    ('/', MainPageHandler),
    ('/newpost', NewPostHandler),
    ('/(\d+)', PostHandler),
    ], debug = True)
