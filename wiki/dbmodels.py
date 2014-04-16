from google.appengine.ext import db

class WikiPage(db.Model):
    name = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)


class User(db.Model):
    name = db.StringProperty(required = True)
    password_hash = db.StringProperty(required = True)
    email = db.EmailProperty()
    created = db.DateTimeProperty(auto_now_add = True)

    @classmethod
    def by_id(cls, user_id):
        return cls.get_by_id(user_id)

    @classmethod
    def by_name(cls, name):
        u = cls.all().filter('name =', name).get()
        return u

"""
    @classmethod
    def register(cls, name, password, email = None):
        pw_hash = cookies.make_password_hash(name, password)
        u = cls(name = name, password_hash = pw_hash)
        if email:
            u.email = email
        return u

    @classmethod
    def validate(cls, name, password):
        u = cls.by_name(name)
        if u and cookies.valid_password(name, password, u.password_hash):
            return u

"""
