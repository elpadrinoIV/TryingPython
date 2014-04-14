import hashlib
import hmac
import random
import re
import string
from google.appengine.ext import db

########## REGEX VALIDATION ##########
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username_form(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password_form(password):
    return password and PASS_RE.match(password)

EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email_form(email):
    return not email or EMAIL_RE.match(email)

########## COOKIES ##########
SECRET_VALUE = "vpqas11.q+"

def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(10))

def hash_string(s):
    return hmac.new(SECRET_VALUE, s, hashlib.sha256).hexdigest()

def make_secure_value(s):
    return "%s|%s" %(s, hash_string(s))


def check_secure_value(v):
    s = v.split('|')[0]
    if v == make_secure_value(s):
        return s

def make_password_hash(name, pw, salt = None):
    if salt is None:
        salt = make_salt()

    hash_value = hashlib.sha256(name + pw + salt).hexdigest()
    return "%s,%s" %(hash_value, salt)

def valid_password(name, pw, h):
    salt = h.split(',')[1]
    return h == make_password_hash(name, pw, salt)

def exists_user(username):
    query = "SELECT * FROM User WHERE name='%s'" % username
    user = db.GqlQuery(query).get()
    if user:
        return True
    else:
        return False

def valid_username_and_password(username, password):
    query = "SELECT * FROM User WHERE name='%s'" % username
    user = db.GqlQuery(query).get()
    if user:
        h = user.password
        if valid_password(username, password, h):
            return user

