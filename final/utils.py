import webapp2
import os
import cgi
from google.appengine.ext import db
import jinja2
import hashlib
import hmac
import string
import random
import datetime
import re
import time
import logging

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader= jinja2.FileSystemLoader(template_dir),
	autoescape= True)
random.seed()

USER_RE = re.compile(r'^[a-zA-Z0-9_-]{3,20}$')
PASS_RE = re.compile(r'^.{3,20}$')
EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
PAGE_RE_STR = r'([_0-9a-zA-Z]+)'

SECRET = 'NA3kjq8K5R'
SALT_CHARS = string.ascii_letters + string.digits + '@#$%!&*'

def make_salt(slen=5):
	salt = ''
	for i in xrange(slen):
		salt += random.choice(SALT_CHARS)
	return salt

def hash_user_info(username, password, salt=None):
	if not salt:
		salt = make_salt()
	h = hashlib.sha256(username + password + salt).hexdigest()
	#h = hmac.new(SECRET, password + salt, hashlib.sha256).hexdigest()
	h += '|' + salt
	return h

def check_user_info(username, password, h):
	salt = None
	try:
		salt = h.split('|')[1]
	except IndexError:
		return False
	if h == hash_user_info(username, password, salt):
		return True
	return False


def valid_username(username):
	return USER_RE.match(username)

def valid_password(password):
	return PASS_RE.match(password)

def valid_email(email):
	return EMAIL_RE.match(email)

def escape_html(s):
	return cgi.escape(s, quote=True)

def sanitize(s):
	r = ''
	for c in s:
		r += escape_html(c)
	return r

def get_user(username):
	q = db.GqlQuery("SELECT * from User WHERE name=:1", username)
	return q.get()

def hash_username_for_cookie(username):
	h = hmac.new(SECRET, username, hashlib.sha256)
	return h.hexdigest()

def verify_user_cookie(user_cookie):
	split_cookie = user_cookie.split('|')
	if len(split_cookie) != 2:
		print split_cookie
		return False
	username = None
	hashed_username = None
	try:
		username = split_cookie[0]
		hashed_username = split_cookie[1]
	except IndexError:
		return False
	if hashed_username == hash_username_for_cookie(username):
		return username
	return


def set_user_cookie(response, user):
	response.set_cookie('user', 
		value=user.name + '|' + hash_username_for_cookie(user.name), 
		path='/', 
		#domain='www.suvanjanmukherjee.me',
		expires=datetime.datetime.now() + datetime.timedelta(days=1))
	#username = str(user.name)
	#cookie_value = username + '|' + hash_username_for_cookie(username)
	#response.headers.add_header('Set-Cookie', 'user=%s; Path=/'%cookie_value)
	return

def unset_user_cookie(response):
	response.delete_cookie('user')
	return

class Wiki(db.Model):
	title = db.StringProperty(required=True)
	content = db.TextProperty(required=True)
	created = db.DateTimeProperty(auto_now_add=True)
	updated = db.DateTimeProperty(auto_now=True)

	@staticmethod
	def getEntryByTitle(title):
		wiki = Wiki.all().filter('title =', title).order('-created').get()
		return wiki

	@staticmethod
	def getEntryById(wiki_id):
		wiki = Wiki.get_by_id(wiki_id)
		return wiki

	@staticmethod
	def getAllEntries(title):
		wikis = list(Wiki.all().filter('title =', title).order('-created'))
		return wikis

	def view_link(self):
		return '/' + self.title + '?id=' + str(self.key().id())

	def edit_link(self):
		return '/_edit/' + self.title + '?id=' + str(self.key().id())

	def edit_link_no_id(self):
		return '/_edit/' + self.title

class User(db.Model):
	name = db.StringProperty(required=True)
	password = db.StringProperty(required=True)
	email = db.EmailProperty(required=False)
	created = db.DateTimeProperty(auto_now_add=True)
	updated = db.DateTimeProperty(auto_now=True)


class Handler(webapp2.RequestHandler):
	def dispatch(self):
		user_cookie = self.request.cookies.get('user', '')
		username = verify_user_cookie(user_cookie)
		if username:
			self.logged_in_user = username
		else:
			self.logged_in_user = None
		super(Handler, self).dispatch()

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.response.write(self.render_str(template, **kw))




