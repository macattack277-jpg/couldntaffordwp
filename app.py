# Flask modules
from flask import Flask, request, flash, session, render_template, redirect

# Other modules
from markupsafe import escape
import datetime
from pathlib import Path, rename
import re
import secrets
from datetime import datetime

# Initialize
app = Flask(__name__)
app.secret_key = b'000'

# If a get request is sent, show the login form
@app.get("/prod")
def init():
	return render_template('prod')

# If a post request is sent (with the necessary parameters), create a new post
@app.post('/prod')
def post():

	directory = escape(request.form['title'])
	# check for skids thinking they're Mr Robot bluds
	if any(c in directory for c in '/.'):
    		print('True')
    		flash('Invalid title')
    		return render_template('prod')

	if g.editing:
		
	directory = (f'posts/{directory}')
	newdirectory = Path(directory)
	newdirectory.mkdir(parents=True, exist_ok=True)
	with open(f'{directory}/content', 'w') as content:
		content.write(request.form['content'])
	return('Your post has been posted! You can view it <a href="../">Here</a>')

# This is where the user's blog posts will appear
@app.route('/')
def view_posts():

	data = '<h1>Your posts:</h1><a href="./prod">Create a new post!</a>'
	path = Path('posts')
	posts = [post for post in path.iterdir()]
	posts.sort(key=lambda f: f.stat().st_ctime)
	posts.reverse()
	for post in posts:
		with open(f'{post}/content', 'r') as file:
			data += f'<br><br><h2>{str(post).replace("posts/", "")}</h2><a>Created: {datetime.fromtimestamp(post.stat().st_ctime).replace(microsecond=0)}</a><br>{file.read()}<br><br><a href="edit/{post}">Edit</a>'

	return data

@app.route('/edit/posts/<post>')
def edit(post):
	g.editing = True
	g.postbeingedited = post
	return redirect(url_for('prod'))


@app.errorhandler(404)
def not_found(error):
	return('404. Aint nothing here mate <br> <a href="/"> Click here to go to the home page</a>')

