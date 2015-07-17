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
import webapp2
import cgi

alpha = 'abcdefghijklmnopqrstuvwxyz'
alphaidx = {}
alpharevidx = {}
for i in range(len(alpha)):
	alphaidx[alpha[i]] = i
	alpharevidx[i] = alpha[i]

form = '''
<title>Unit 2 Rot 13</title>
<h1>Enter some text to ROT13:</h1>
<form method="post">
	<textarea name="text" rows="10" cols="50">%(text)s</textarea>
	<br>
		<input type="submit">
</form>
'''

def escape_html(s):
	return cgi.escape(s, quote=True)

def sanitize(s):
	r = ''
	for c in s:
		r += escape_html(c)
	return r

def rot13_char(c):
	upper = False
	if c.isupper():
		upper = True
	c = c.lower()
	if c in alphaidx:
		idx = alphaidx[c]
		idx = (idx + 13) % 26
		c = alpharevidx[idx]
	if upper:
		c = c.upper()
	return c

def rot13(s):
	r = ''
	for c in s:
		r += rot13_char(c)
	return r

class MainHandler(webapp2.RequestHandler):

	def write_form(self, text=""):
		self.response.write(form % {'text' : text})
		return

	def get(self):
		self.write_form()

	def post(self):
		user_text = self.request.get('text')
		print 'user_text: ', user_text
		rotated_text = rot13(user_text)
		print 'rotated_text: ', rotated_text
		sanitized_text = sanitize(rotated_text)
		print 'sanitized_text: ', sanitized_text

		self.write_form(sanitized_text)

class TestHandler(webapp2.RequestHandler):
	def get(self):
		q = self.request.get("q")
		self.response.out.write("Why do you want to submit '%s'?"%q)
		#self.response.headers['Content-Type'] = 'text/plain'
		#self.response.write(self.request)

	def post(self):
		q = self.request.get("q")
		self.response.out.write("Why do you want to submit '%s'?"%q)
		#self.response.headers['Content-Type'] = 'text/plain'
		#self.response.write(self.request)


app = webapp2.WSGIApplication([
	('/', MainHandler),
], debug=True)
