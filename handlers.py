import os
import webapp2
import jinja2
import dbmodels
from google.appengine.ext import db
import login

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)


########## BASE HANDLER ##########
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


########## MAIN PAGE HANDLER ##########
class MainPageHandler(Handler):
    def render_front(self, posts=""):
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 10")

        self.render("front.html", posts=posts)

    def get(self):
        self.render_front()


########## NEW POST HANDLER ##########
class NewPostHandler(Handler):
    def render_page(self, subject="", content="", error=""):
        self.render("newpost.html", subject=subject, content=content, error=error)

    def get(self):
        self.render_page()

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            p = dbmodels.Post(subject = subject, content=content)
            p.put()

            url = "/" + str(p.key().id())
            self.redirect(url)
        else:
            error = "Oops, we need both subject and content"
            self.render_page(subject, content, error)


########## POST HANDLER ##########
class PostHandler(Handler):
    def get(self, post_id):
        post_id = long(post_id)
        p = dbmodels.Post.get_by_id(post_id)
        self.render("post.html", post=p)


########## SIGN UP HANDLER ##########
class SignUpHandler(Handler):
    def render_page(self, **params):
        self.render("signup.html", **params)

    def get(self):
        self.render_page()

    def post(self):
        params = {}
        username = self.request.get("username")
        password = self.request.get("password")
        verify = self.request.get("verify")
        email = self.request.get("email")

        params["username"] = username
        params["email"] = email

        error_en_form = False

        if not login.valid_username(username):
            params["error_username"] = "Nombre de usuario invalido"
            error_en_form = True

        if not login.valid_password(password):
            params["error_password"] = "Contrasena invalida"
            error_en_form = True
        elif password != verify:
            params["error_verify"] = "Las contrasenas son distintas"
            error_en_form = True

        if not login.valid_email(email):
            params["error_email"] = "email invalido"
            error_en_form = True

        if error_en_form:
            self.render_page(**params)
        else:
            username = str(username)
            self.response.headers.add_header('Set-Cookie', 'username=%s' % username)
            self.redirect("/welcome")


########## WELCOME HANDLER ##########
class WelcomeHandler(Handler):
    def get(self):
        username = self.request.cookies.get('username', '')
        self.render("welcome.html", username=username)




