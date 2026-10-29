# Flask modules
from flask import Flask, request, flash, session, render_template, redirect, g, abort, get_flashed_messages
from flask_limiter.util import get_remote_address
from flask_limiter import Limiter
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman

# Other modules
from markupsafe import escape
import datetime
from pathlib import Path
import secrets
from datetime import datetime
from os import getenv
from dotenv import load_dotenv, set_key
import bcrypt
from shutil import rmtree

# Initialize
load_dotenv(dotenv_path='.env', override='True')
app = Flask(__name__)
limiter = Limiter(
	get_remote_address,
	app=app,
	storage_uri='memory://',
)
csp = {'default-src': '\'self\'',
	'script-src': '\'self\'',
	'style-src': '\'self\'',
	'form-action': '\'self\''}

talisman = Talisman(app, content_security_policy=csp, force_https = False, frame_options='SAMEORIGIN')


app.secret_key = getenv('SECRET_KEY')
csrf = CSRFProtect(app)
POSTS_DIR = Path('posts').resolve()

def check_session():
	if 'username' in session:
		if session['username'] != getenv('USERNAME'):
			abort(404)
	else:
		abort(404)


# Login
@app.get('/login')
def getlogin():
	return render_template('login')

# Processor for the login
@app.post('/login')
@limiter.limit('100/day;10/hour;5/minute')
def postlogin():
	password = escape(request.form['password'])
	name = escape(request.form['username'])
	if name == getenv('USERNAME'):
		if bcrypt.checkpw(password.encode('utf-8'), getenv('HASH').encode('utf-8')):
			session['username'] = name
			flash('You have logged in successfully!')
			return redirect('/')
		else:
			flash('Incorrect credentials!')
			return render_template('login')
	else:
		flash('Incorrect credentials!')
		return render_template('login')


# If a get request is sent, show the login form
@app.get("/prod")
def init():
	check_session()
	return render_template('prod')






# If a post request is sent (with the necessary parameters), create a new post
@app.post('/prod')
def post():
	check_session()

	dir = request.form['title']
	# check for skids thinking they're Mr Robot bluds


	directory = (f'posts/{dir}')
	post_path = Path(directory).resolve()
	if not post_path.is_relative_to(POSTS_DIR) or any(char in dir for char in ('.', '/')):
		abort(400)


	newdirectory = Path(directory)
	newdirectory.mkdir(parents=True, exist_ok=True)
	with open(f'{directory}/content', 'w') as content:
		content.write(escape(request.form['content']))
	with open(f'{directory}/created', 'w') as time:
		time.write(f'{datetime.now().replace(microsecond=0)}')
	return('Your post has been posted! You can view it <a href="../">Here</a>')

# This is where the user's blog posts will appear
@app.route('/')
def view_posts():
	g.public_name = getenv('PUBLIC_NAME')
	if 'username' in session and session['username'] == getenv('USERNAME'):
		g.loggedin = True
	else:
		g.loggedin = False
	path = Path('posts')
	posts = [post for post in path.iterdir()]
	posts.sort(key=lambda f: f.stat().st_ctime)
	posts.reverse()
	g.postdict = {}
	for post in posts:
		with open(f'{post}/created', 'r') as file:
			created = file.read()
		try:
			with open(f'{post}/edited', 'r') as file:
				edited = '<br>Last edited: ' + file.read()
		except FileNotFoundError:
			edited = ''
		with open(f'{post}/content', 'r') as file:
			file = file.read()
		g.postdict[str(post).replace('posts/', '')] = [file, created, edited]
	return render_template('index')



@app.get('/edit/<path:post>')
def initedit(post):
	check_session()
	post_path = Path(post).resolve()

	# Credit to u/Diapolo10 for the arbitrary write patch
	if not post_path.is_relative_to(POSTS_DIR):
        	abort(400)
	g.title = post.replace('posts/', '')
	session['title'] = post.replace('posts/', '')
	try:
		with open(f'{post}/content', 'r') as file:
			g.content = file.read()
		return render_template('edit')
	except FileNotFoundError:
		abort(400)

# When something is edited
@app.post('/edit/<path:post>')
def postedit(post):
	check_session()
	content = request.form
	directory = request.form['title']
	post_path = Path(post).resolve()
	if not post_path.is_relative_to(POSTS_DIR) or any(char in directory for char in ('.', '/')):
		abort(400)
	old_directory = Path(f'posts/{session["title"]}')
	del session['title']
	with open(f'{old_directory}/content', 'w') as file:
		file.write(request.form['content'])
	old_directory.rename(f'posts/{directory}')
	with open(f'posts/{directory}/edited', 'w') as file:
		file.write(f'{datetime.now().replace(microsecond=0)}')
	return('Your changes have been saved. <br> <a href="/">Return to homepage</a>')

# If a resource doesn't exist
@app.errorhandler(404)
def not_found(error):
	return('404. Aint nothing here mate <br> <a href="/"> Click here to go to the home page</a>')

# If the user sends a shitty request
@app.errorhandler(400)
def bad_request(error):
	return('400. You probably tried doing something you weren\'t supposed to.<br> <a href="/"> Click here to go to the home page</a>')

# If the user deletes one of their posts
@app.get('/delete/<path:post>')
def delete(post):
	check_session()
	post_path = Path(post).resolve()
	if not post_path.is_relative_to(POSTS_DIR):
        	abort(400)
	rmtree(f'posts/{session["title"]}')
	del session['title']
	return('Your post has been deleted. <br> <a href="/">Return to homepage</a>')

@app.get('/logout')
def logout():
	check_session()
	del session['username']
	flash('Successfully logged out!')
	return redirect('/')


@app.errorhandler(429)
def ratelimit(error):
	abort(400)

@app.get('/admin')
def initaccount():
	check_session()
	g.public_name = getenv('PUBLIC_NAME')
	g.private_name = getenv('USERNAME')
	return render_template('admin')

@app.post('/admin')
def update_public_name():
	check_session()
	set_key('.env', 'PUBLIC_NAME', request.form['publicnameupdate'])
	load_dotenv('.env', override=True)
	flash('Changes saved!')
	return redirect('/admin')

@app.get('/updatecredentials')
def update_creds():
	check_session()
	g.login_name = getenv('USERNAME')
	return render_template('updatecredscreen')

@app.get('/updatecredentials/name')
def get_update_name():
	check_session()
	g.updating = 'username'
	return render_template('updatecreds')

@app.get('/updatecredentials/password')
def get_update_password():
        check_session()
        g.updating = 'password'
        return render_template('updatecreds')

# I should probably make these two functions a singular function later to make the code more simple
@limiter.limit('100/day;10/hour;5/minute')
@app.post('/updatecredentials/name')
def update_name():
	check_session()
	if bcrypt.checkpw(request.form['passwordverify'].encode('utf-8'), getenv('HASH').encode('utf-8')):
		set_key('.env', 'USERNAME', request.form['name'])
		load_dotenv('.env', override=True)
		flash('Your name was updated!')
		return redirect('/updatecredentials/name')
	else:
		flash('Your password was incorrect!')
		return redirect('/updatecredentials/name')


@limiter.limit('100/day;10/hour;5/minute')
@app.post('/updatecredentials/password')
def update_password():
	check_session()
	print(request.form['passwordverify'])
	if request.form['newpassword'] != request.form['newpasswordconfirm']:
		flash('Passwords did not match!')
		return redirect('/updatecredentials/password')

	if bcrypt.checkpw(request.form['passwordverify'].encode('utf-8'), getenv('HASH').encode('utf-8')):
		set_key('.env', 'HASH', str(bcrypt.hashpw(request.form['newpassword'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')))
		load_dotenv('.env', override=True)
		flash('Your password has been successfully updated!')
		return redirect('/updatecredentials/password')
	else:
		flash('Your password was incorrect!')
		return redirect('/updatecredentials/password')
