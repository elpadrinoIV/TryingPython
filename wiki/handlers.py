import os
import webapp2
import jinja2
import dbmodels
from google.appengine.ext import db
import logging
#import login
#import cookies

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)


def get_page(page_name, created = None):
    query = "SELECT * FROM WikiPage WHERE name='%s' ORDER BY created DESC LIMIT 10" % page_name
    logging.error("QUERY: %s" % query)
    page = db.GqlQuery(query).get()
    logging.error("RESULTADO QUERY: %s" % repr(page))
    return page

def save_page(page_name, content):
    wiki_page = dbmodels.WikiPage(name = page_name, content = content)
    wiki_page.put()


########## BASE HANDLER ##########
class Handler(webapp2.RequestHandler):
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


########## WIKI HANDLER ##########
class WikiPageHandler(Handler):
    def get(self, page_name):
        logging.error("PAGE_NAME: %s" % page_name)
        page = get_page(page_name)
        if page:
            # la muestro
            self.render("page.html", content = page.content)
            pass
        else:
            # editar
            self.redirect('/_edit%s' % page_name)
            


########## EDIT PAGE HANDLER ##########
class EditPageHandler(Handler):
    def get(self, page_name):
        page = get_page(page_name)
        content = ""
        if page:
            content = page.content

        self.render("edit_page.html", content = content)

    def post(self, page_name):
        logging.error("PAGE_NAME: %s", page_name)
        content = self.request.get("content")
        save_page(page_name, content)
        self.redirect(page_name)


########## SIGN UP HANDLER ##########
class SignUpHandler(Handler):
    # def render_page(self, **params):
    #     self.render("signup.html", **params)
    
    def get(self):
        pass
        # self.render_page()

    def post(self):
        pass
    """
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
"""


########## LOGIN HANDLER ##########
class LoginHandler(Handler):
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
class LogoutHandler(Handler):
    def get(self):
        self.response.delete_cookie('user_id')
        self.redirect('/signup')


