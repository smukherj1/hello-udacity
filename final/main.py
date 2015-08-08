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
import time
import logging
from utils import *


class LoginHandler(Handler):
	def render_login(self,
		username="",
		uerror="",
		perror=""):
		return self.render('login.html',
			username=username,
			uerror=uerror,
			perror=perror)

	def get(self):
		return self.render_login()

	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')
		s_username = sanitize(username)

		uerror = ""
		perror = ""
		error = False
		if not valid_username(username):
			uerror = "That's not a valid username."
			error = True
		if not valid_password(password):
			perror = "That wasn't a valid password."
			error = True

		user = None
		if not uerror:
			user = get_user(s_username)
			if not user:
				uerror = "That user doesn't exist!"
				error = True
			elif not check_user_info(s_username, password, user.password):
				perror = "Invalid login"
				error = True
		if error:
			return self.render_login(username=s_username,
				uerror=uerror,
				perror=perror)
		set_user_cookie(self.response, user)
		return self.redirect('/')

class LogoutHandler(Handler):
	def get(self):
		unset_user_cookie(self.response)
		return self.redirect('/')




class SignupHandler(Handler):
	def render_signup(self,
		username="",
		email="",
		uerror="",
		perror="",
		pverror="",
		eerror=""):
		return self.render('signup.html',
			username="",
			email="",
			uerror=uerror,
			perror=perror,
			pverror=pverror,
			eerror=eerror)

	def get(self):
		return self.render_signup()

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
		if error:
			return self.render_signup(uerror=uerror,
				perror=perror,
				pverror=pverror,
				eerror=eerror,
				username=s_username,
				email=s_email)

		user = get_user(s_username)
		if not user:
			if not email:
				s_email = None
			user = User(name=s_username, 
				password=hash_user_info(s_username, password),
				email=s_email)
			user.put()
		else:
			return self.render_signup(uerror="User already exists!",
				username=s_username)
		set_user_cookie(self.response, user)

		return self.redirect('/')


class MainHandler(Handler):

	def get(self, title="front"):
		logging.info("Wiki Title request " + title + ", user: " + str(self.logged_in_user))
		wiki = Wiki.getEntryByTitle(title)
		if wiki:
			return self.render('index.html', 
				logged_in_user=self.logged_in_user,
				edit_link="/_edit/" + title,
				content=wiki.content)
		elif self.logged_in_user:
			return self.redirect('/_edit/' + title)
		return self.redirect('/login')


class EditHandler(Handler):

	def get(self, title):
		if not self.logged_in_user:
			return self.redirect('/login')
		logging.info("Wiki Title edit request " + title)
		wiki = Wiki.getEntryByTitle(title)
		content=""
		if wiki:
			content = wiki.content
		return self.render('new.html', 
			logged_in_user=self.logged_in_user,
			content=content)

	def post(self, title):
		if not self.logged_in_user:
			self.redirect('/login')
		content = self.request.get('content')
		wiki = Wiki(title=title, content=content)
		wiki.put()

		if title == 'front':
			title = ""

		return self.redirect('/' + title)



app = webapp2.WSGIApplication([
	('/', MainHandler),
	('/signup/?', SignupHandler),
	('/login/?', LoginHandler),
	('/logout/?', LogoutHandler),
	('/_edit/' + PAGE_RE_STR, EditHandler),
	('/' + PAGE_RE_STR, MainHandler),
], debug=True)
