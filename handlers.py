import os
import webapp2
import jinja2
import dbmodels
from google.appengine.ext import db
import login
import cookies

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)


########## BASE HANDLER ##########
class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = cookies.make_secure_value(val)
        self.response.headers.add_header('Set-Cookie', '%s=%s; Path=/'
                                         % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and cookies.check_secure_value(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.delete_cookie('user_id')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        user_id = self.read_secure_cookie('user_id')
        self.user = user_id and dbmodels.User.by_id(int(user_id))


class JsonHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(*a, **kw)

#    def render_str(self, template, **params):
#        t = jinja_env.get_template(template)
#        return t.render(params)

#    def render(self, template, **kw):
#        self.write(self.render_str(template, **kw))



########## MAIN PAGE HANDLER ##########
class MainPageHandler(BlogHandler):
    def render_front(self, posts=""):
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 10")

        self.render("front.html", posts=posts)

    def get(self):
        self.render_front()


########## NEW POST HANDLER ##########
class NewPostHandler(BlogHandler):
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
class PostHandler(BlogHandler):
    def get(self, post_id):
        post_id = long(post_id)
        p = dbmodels.Post.get_by_id(post_id)
        self.render("post.html", post=p)


########## SIGN UP HANDLER ##########
class SignUpHandler(BlogHandler):
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

        if not login.valid_username_form(username):
            params["error_username"] = "Nombre de usuario invalido"
            error_en_form = True
        else:
            u = dbmodels.User.by_name(username)
            if u:
                params["error_username"] = "Usuario ya existe"
                error_en_form = True
                
        if not login.valid_password_form(password):
            params["error_password"] = "Contrasena invalida"
            error_en_form = True
        elif password != verify:
            params["error_verify"] = "Las contrasenas son distintas"
            error_en_form = True

        if not login.valid_email_form(email):
            params["error_email"] = "email invalido"
            error_en_form = True

        if error_en_form:
            self.render_page(**params)
        else:
            user = dbmodels.User.register(username, password, email)
            user.put()

            self.login(user)

            self.redirect("/welcome")


########## WELCOME HANDLER ##########
class WelcomeHandler(BlogHandler):
    def get(self):
        if self.user:
            self.render("welcome.html", username = self.user.name)
        else:
            self.redirect("/signup")


########## LOGIN HANDLER ##########
class LoginHandler(BlogHandler):
    def render_page(self, error = ""):
        self.render("login.html", error_login = error)

    def get(self):
        self.render_page()

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")

        user = dbmodels.User.validate(username, password)
        if user:
            self.login(user)
            self.redirect('/welcome')
        else:
            error = "Invalid user and pass"
            self.render_page(error)



########## LOGOUT HANDLER ##########
class LogoutHandler(BlogHandler):
    def get(self):
        self.response.delete_cookie('user_id')
        self.redirect('/signup')


########## POST JSON HANDLER ##########
class PostJsonHandler(JsonHandler):
    def get(self, post_id):
        json_string = ""
        post_id = long(post_id)
        p = dbmodels.Post.get_by_id(post_id)
        if p:
            json_string = p.toJson()

        self.write(json_string)

########## MAIN PAGE JSON HANDLER ##########
class MainPageJsonHandler(JsonHandler):
    def get(self):
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 10")
        posts = list(posts)

        json_string = "["
        json_string += ",".join(post.toJson() for post in posts)
        json_string += "]"

        self.write(json_string)

