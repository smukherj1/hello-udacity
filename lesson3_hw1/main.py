#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2
import cgi
import re
import time
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader= jinja2.FileSystemLoader(template_dir),
	autoescape= True)

class Blog(db.Model):
	subject = db.StringProperty()
	content = db.TextProperty()
	created = db.DateTimeProperty(auto_now_add=True)

	def get_content(self):
		return self.content.replace('\n', '<br>')

class Handler(webapp2.RequestHandler):
	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.response.write(self.render_str(template, **kw))

	def render_blog(self, blogs=[]):
		return self.render('index.html', blogs=blogs)

class MainHandler(Handler):

	def get(self):
		q = db.GqlQuery("SELECT * from Blog ORDER BY created DESC")
		return self.render_blog(q)

class NewPostHandler(Handler):

	def render_new_blog(self, error_str="", content="", subject=""):
		self.render('new.html', error_str = error_str,
			subject = subject,
			content = content)
		return

	def get(self):
		return self.render('new.html')

	def post(self):
		subject = self.request.get("subject")
		content = self.request.get("content")

		if not subject and not content:
			return self.render_new_blog("Y U NO provide subject and content?")
		elif not subject:
			return self.render_new_blog("Y U NO provide subject?", content = content)
		elif not content:
			return self.render_new_blog("Y U NO provide content?", subject = subject)

		b = Blog(subject=subject, content=content)
		b.put()

		time.sleep(2)
		return self.redirect('/' + str(b.key().id()))

class BlogEntryHandler(Handler):
	def get(self, blog_id):
		blog_id = int(blog_id)
		q = db.GqlQuery("SELECT * from Blog WHERE __key__ = KEY('Blog', :1)", 
			blog_id)
		blogs = q.fetch(1)
		if not blogs:
			self.error(404)
			return self.response.write('<h1>404 Not Found</h1><br>' + \
				'Oops! Could not find that blog')
		return self.render_blog(blogs)

app = webapp2.WSGIApplication([
	('/', MainHandler),
	('/newpost', NewPostHandler),
	('/(\d+)', BlogEntryHandler),
], debug=True)
