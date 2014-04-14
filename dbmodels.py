from google.appengine.ext import db

class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class User(db.Model):
    name = db.StringProperty(required = True)
    password = db.StringProperty(required = True)
    email = db.EmailProperty()
    created = db.DateTimeProperty(auto_now_add = True)

def exists_user(username):
    query = "SELECT * FROM User WHERE name='%s'" % username
    user = db.GqlQuery(query).get()
    if user:
        return True
    else:
        return False

