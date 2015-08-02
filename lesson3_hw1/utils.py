import webapp2
import os
from google.appengine.ext import db
import jinja2

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader= jinja2.FileSystemLoader(template_dir),
	autoescape= True)


class Blog(db.Model):
	subject = db.StringProperty(required=True)
	content = db.TextProperty(required=True)
	created = db.DateTimeProperty(auto_now_add=True)
	updated = db.DateTimeProperty(auto_now=True)

	def get_content(self):
		return self.content.replace('\n', '<br>')

class User(db.Model):
	name = db.StringProperty(required=True)
	password = db.StringProperty(required=True)
	email = db.EmailProperty(required=True)


class Handler(webapp2.RequestHandler):
	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.response.write(self.render_str(template, **kw))

	def render_blog(self, blogs=[], logged_in_user=""):
		return self.render('index.html', blogs=blogs, logged_in_user=logged_in_user)