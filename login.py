import random
import re
import string

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

