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
from utils import *



class MainHandler(Handler):

	def get(self):
		q = get_blog_list_for_front_page()
		return self.render_blog(q)

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
		return self.redirect('/welcome')

class LogoutHandler(Handler):
	def get(self):
		unset_user_cookie(self.response)
		return self.redirect('/signup')




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

		return self.redirect('/welcome')

class WelcomeHandler(Handler):
	def get(self):
		user_cookie = self.request.cookies.get('user', '')
		username = verify_user_cookie(user_cookie)

		if username:
			self.render('welcome.html', logged_in_user=username)
		else:
			self.redirect('/')


class NewPostHandler(Handler):

	def render_new_blog(self, error_str="", content="", subject="", logged_in_user=""):
		return self.render('new.html', error_str = error_str,
			subject = subject,
			content = content,
			logged_in_user = logged_in_user)

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

		time.sleep(0.5)
		get_blog_list_for_front_page(True)
		return self.redirect('/' + str(b.key().id()))

class BlogEntryHandler(Handler):
	def get(self, blog_id):
		blog_id = int(blog_id)
		blogs = get_permalink(blog_id)
		if not blogs:
			self.error(404)
			return self.response.write('<h1>404 Not Found</h1><br>' + \
				'Oops! Could not find that blog')
		return self.render_blog(blogs)

class BlogCacheFlushHandler(Handler):
	def get(self):
		flush_cache()
		return self.redirect('/')

app = webapp2.WSGIApplication([
	('/', MainHandler),
	('/newpost/?', NewPostHandler),
	('/signup/?', SignupHandler),
	('/login/?', LoginHandler),
	('/logout/?', LogoutHandler),
	('/welcome/?', WelcomeHandler),
	('/flush/?', BlogCacheFlushHandler),
	('/(\d+)', BlogEntryHandler),
], debug=True)
