# Flask modules
from flask import Flask, request, flash, session, render_template, redirect, g, abort, get_flashed_messages


# Other modules
from markupsafe import escape
import datetime
from pathlib import Path
import secrets
from datetime import datetime
from os import getenv
from dotenv import load_dotenv
import bcrypt
from shutil import rmtree

# Initialize
load_dotenv(dotenv_path='.env', override='True')
app = Flask(__name__)
app.secret_key = getenv('SECRET_KEY')
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

	directory = escape(request.form['title'])
	# check for skids thinking they're Mr Robot bluds


	directory = (f'posts/{directory}')
	post_path = Path(directory).resolve()
	if not post_path.is_relative_to(POSTS_DIR):
		abort(400)

	newdirectory = Path(directory)
	newdirectory.mkdir(parents=True, exist_ok=True)
	with open(f'{directory}/content', 'w') as content:
		content.write(escape(request.form['content']))
	with open(f'{directory}/created', 'w') as time:
		time.write(f'{datetime.now().replace(microsecond=0)}')
	return('Your post has been posted! You can view it <a href="../">Here</a>')

# This is where the user's blog posts will appear
# If you're reading this, I understand you probably find the elif statements instead of just using a template ridiculous, I originally implemented it this way
# Then realised later on that templates would've been way better, however I didn't prioritise this over making other features
@app.route('/')
def view_posts():
	if 'username' in session and session['username'] == getenv('USERNAME'):
		extrainfo = '<a href="./logout">Log out</a><br><a href="./prod">Create a new post!</a>'
	else:
		extrainfo = ''
	messages = ''
	if get_flashed_messages():
		for message in get_flashed_messages():
			messages += f'{message}<br>'
	data = f'<h1>{getenv("PUBLIC_NAME")}\'s posts:</h1>{extrainfo}<br>{messages}'
	path = Path('posts')
	posts = [post for post in path.iterdir()]
	posts.sort(key=lambda f: f.stat().st_ctime)
	posts.reverse()
	for post in posts:
		with open(f'{post}/created', 'r') as file:
			created = file.read()
		try:
			with open(f'{post}/edited', 'r') as file:
				edited = '<br>Last edited: ' + file.read()
		except FileNotFoundError:
			edited = ''
		if 'username' in session and session['username'] == getenv('USERNAME'):
			edit = f'<br><a href="edit/{post}">Edit</a>'
		else:
			edit = ''
		with open(f'{post}/content', 'r') as file:
			data += f'<br><br><h2>{str(post).replace("posts/", "")}</h2><a><small>Created: {created}{edited}</small><br></a><p>{file.read()}</p>{edit}<br>'
	return data



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
	content = escape(request.form)
	directory = escape(request.form['title'])
	post_path = Path(post).resolve()
	if not post_path.is_relative_to(POSTS_DIR):
		abort(400)
	old_directory = Path(f'posts/{session["title"]}')
	del session['title']
	with open(f'{old_directory}/content', 'w') as file:
		file.write(escape(request.form['content']))
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
