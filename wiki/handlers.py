import os
import webapp2
import jinja2
import dbmodels
from google.appengine.ext import db
from google.appengine.api import memcache
import logging
import utils

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

"""
def get_page(page_name, page_id = None, update = False):
    key = page_name
    pages = memcache.get(key)

    if pages is None or update:
        query = "SELECT * FROM WikiPage WHERE name='%s' ORDER BY created DESC" % page_name
        logging.error("QUERY: %s" % query)
        pages = db.GqlQuery(query)
        pages = list(pages)
        memcache.set(key, pages)

    if pages:
        return pages[0]

def get_historia(page_name, update = False):
    key = page_name
    historia = memcache.get(key)

    if page is None or update:
        query = "SELECT * FROM WikiPage WHERE name='%s' ORDER BY created DESC LIMIT 10" % page_name
        logging.error("QUERY: %s" % query)
        page = db.GqlQuery(query).get()
        memcache.set(key, page)

    return page
"""

def save_page(page_name, content):
    wiki_page = dbmodels.WikiPage(name = page_name, content = content)
    wiki_page.put()
    # memcache.set(page_name, wiki_page)

########## BASE HANDLER ##########
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, user = self.user, **kw))

    def not_found(self):
        self.write("Not Found")


    def set_secure_cookie(self, name, val):
        cookie_val = utils.make_secure_value(val)
        self.response.headers.add_header('Set-Cookie', '%s=%s; Path=/'
                                         % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and utils.check_secure_value(cookie_val)

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
        version = self.request.get("v")
        logging.error("PAGE_NAME: %s, ?v=%s" % (page_name, version))

        page = None

        if version:
            version = long(version)
            page = dbmodels.WikiPage.by_id(version, page_name)
            if page is None:
                self.not_found()
                return
        else:
            # page = get_page(page_name)
            page = dbmodels.WikiPage.by_name(page_name).get()

        if page:
            # la muestro
            edit_link = "/_edit%s" % page_name
            if version:
                edit_link += "?v=%s" % version

            history_link = "/_history%s" % page_name

            content = page.content
            content = content.replace("\n", '<br/>')
            self.render("page.html",
                        content = content,
                        edit_link = edit_link,
                        history_link = history_link)
        else:
            # editar
            self.redirect('/_edit%s' % page_name)
            


########## EDIT PAGE HANDLER ##########
class EditPageHandler(Handler):
    def get(self, page_name):
        if self.user:
            version = self.request.get("v")
            page = None
            if version:
                version = long(version)
                page = dbmodels.WikiPage.by_id(version, page_name)
                if page is None:
                    self.not_found()
                    return
            else:
                # page = get_page(page_name)
                page = dbmodels.WikiPage.by_name(page_name).get()

            content = ""
            if page:
                content = page.content

            self.render("edit_page.html", content = content)
        else:
            self.redirect("/signup")

    def post(self, page_name):
        if self.user:
            content = self.request.get("content")
            save_page(page_name, content)
            self.redirect(page_name)
        else:
            self.redirect("/signup")


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

        if not utils.valid_username_form(username):
            params["error_username"] = "Nombre de usuario invalido"
            error_en_form = True
        else:
            u = dbmodels.User.by_name(username)
            if u:
                params["error_username"] = "Usuario ya existe"
                error_en_form = True
                
        if not utils.valid_password_form(password):
            params["error_password"] = "Contrasena invalida"
            error_en_form = True
        elif password != verify:
            params["error_verify"] = "Las contrasenas son distintas"
            error_en_form = True

        if not utils.valid_email_form(email):
            params["error_email"] = "email invalido"
            error_en_form = True

        if error_en_form:
            self.render_page(**params)
        else:
            user = dbmodels.User.register(username, password, email)
            user.put()

            self.login(user)

            self.redirect("/")


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
            self.redirect('/')
        else:
            error = "Invalid user and pass"
            self.render_page(error)



########## LOGOUT HANDLER ##########
class LogoutHandler(Handler):
    def get(self):
        self.response.delete_cookie('user_id')
        self.redirect('/')


########## HISTORY HANDLER ##########
class HistoryHandler(Handler):
    def get(self, page_name):
        historia = dbmodels.WikiPage.by_name(page_name)
        historia = list(historia)

        historia_for_jinja = []

        if historia:
            for edicion in historia:
                fecha = edicion.created
                snip = edicion.content[:100]
                view_link = "%s?v=%s" % (page_name, edicion.key().id())
                edit_link = "/_edit%s?v=%s" % (page_name, edicion.key().id())

                historia_for_jinja.append({'fecha': fecha,
                                           'snip': snip,
                                           'view_link': view_link,
                                           'edit_link': edit_link})
                                       
                                       
            self.render("historia.html", historia = historia_for_jinja)
        else:
            self.redirect('/')

