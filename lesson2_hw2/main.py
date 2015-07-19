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

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader= jinja2.FileSystemLoader(template_dir),
	autoescape= True)

USER_RE = re.compile(r'^[a-zA-Z0-9_-]{3,20}$')
PASS_RE = re.compile(r'^.{3,20}$')
EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')

alpha = 'abcdefghijklmnopqrstuvwxyz'
alphaidx = {}
alpharevidx = {}
for i in range(len(alpha)):
	alphaidx[alpha[i]] = i
	alpharevidx[i] = alpha[i]

form = '''
<title>Sign Up</title>
<h1>Signup</h1>
<form method="post" action="/">
<table>
<tbody>
	<tr>
		<td align="right">
		<label>Username</label>
		</td>
		<td align="right">
		<input type="text" name="username" value="%(username)s">
		</td>
		<td align="right">
		<label style="color: red"><b>%(uerror)s</b></label>
		</td>
	</tr>
	<tr>
		<td align="right">
		<label>Password</label>
		</td>
		<td align="right">
		<input type="password" name="password">
		</td>
		<td align="right">
		<label style="color: red"><b>%(perror)s</b></label>
		</td>
	</tr>
	<tr>
		<td align="right">
		<label>Verify Password</label>
		</td>
		<td align="right">
		<input type="password" name="verify">
		</td>
		<td align="right">
		<label style="color: red"><b>%(pverror)s</b></label>
		</td>
	</tr>
	<tr>
		<td align="right">
		<label>Email (optional)</label>
		</td>
		<td align="right">
		<input type="text" name="email" value="%(email)s">
		</td>
		<td align="right">
		<label style="color: red"><b>%(eerror)s</b></label>
		</td>
	</tr>
	<tr>
		<td>
			<input type="submit">
		</td>
	</tr>
</tbody>
</table>
</form>
'''

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

class Handler(webapp2.RequestHandler):
	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.response.write(self.render_str(template, **kw))

class MainHandler(webapp2.RequestHandler):

	def write_form(self, uerror="",
		perror="",
		pverror="",
		eerror="",
		username="",
		email=""):
		self.response.write(form % {'uerror': uerror,
			'perror': perror,
			'pverror': pverror,
			'eerror': eerror,
			'username' : username,
			'email': email})
		return

	def get(self):
		self.write_form()

	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')
		verify = self.request.get('verify')
		email = self.request.get('email')

		s_username = sanitize(username)
		s_email = sanitize(email)

		uerror = ""
		perror = ""
		pverror = ""
		eerror = ""
		error = False

		if not valid_username(username):
			uerror = "That's not a valid username."
			error = True
		if not valid_password(password):
			perror = "That wasn't a valid password."
			error = True
		elif password != verify:
			pverror = "Your passwords didn't match"
			error = True
		if email and not valid_email(email):
			eerror = "That's not a valid email."
			error = True

		if not error:
			self.redirect('/welcome?username=%s'%username)
		else:
			self.write_form(uerror,
				perror,
				pverror,
				eerror,
				s_username,
				s_email)

class WelcomeHandler(webapp2.RequestHandler):
	def get(self):
		username = self.request.get("username")
		self.response.write('''
<title>Sign Up</title>
<h1>Welcome, %s</h1>
'''%username)


app = webapp2.WSGIApplication([
	('/', MainHandler),
	('/welcome', WelcomeHandler),
], debug=True)
