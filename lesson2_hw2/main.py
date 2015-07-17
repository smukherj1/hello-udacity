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
		<input type="text" name="user">
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
		<input type="text" name="password">
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
		<input type="text" name="verify">
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
		<input type="text" name="email">
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

def escape_html(s):
	return cgi.escape(s, quote=True)

def sanitize(s):
	r = ''
	for c in s:
		r += escape_html(c)
	return r

class MainHandler(webapp2.RequestHandler):

	def write_form(self, uerror="",
		perror="",
		pverror="",
		eerror=""):
		self.response.write(form % {'uerror': uerror,
			'perror': perror,
			'pverror': pverror,
			'eerror': eerror})
		return

	def get(self):
		self.write_form()

	def post(self):
		self.response.write('Under Construction')

class WelcomeHandler(webapp2.RequestHandler):
	def get(self):
		q = self.request.get("username")
		self.response.write('''
<title>Sign Up</title>
<h1>Welcome, %s</h1>
'''%q)


app = webapp2.WSGIApplication([
	('/', MainHandler),
	('/welcome', WelcomeHandler),
], debug=True)
