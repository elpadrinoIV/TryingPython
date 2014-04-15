import hashlib
import hmac
import random
import string
from google.appengine.ext import db

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

