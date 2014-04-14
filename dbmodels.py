from google.appengine.ext import db

class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class User(db.Model):
    name = db.StringProperty(required = True)
    password = db.StringProperty(required = True)
    salt = db.StringProperty(required = True)
    email = db.EmailProperty(required = False)
    created = db.DateTimeProperty(auto_now_add = True)

