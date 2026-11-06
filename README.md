## Couldn't Afford Wordpress

This is a blogposting application built with Flask, deployable on servers. It also supports remote logins.

# Installation

- First, create the folder for your application:

`mkdir mysite
cd mysite`

- Then, clone the repository:

`git clone https://github.com/macattack277-jpg/couldntaffordwp`

- Make a venv (recommended) and install the requirements:

`python3 -m venv .venv`

`source ./.venv/bin/activate`

`pip install -r requirements.txt`

# Setup

CAWP comes with a setup script that enters your details (including hashed/salted passwords) into a .env file to be used.

<img width="1351" height="173" alt="Screenshot_2026-10-25_12-03-13" src="https://github.com/user-attachments/assets/804989a7-7732-46e8-99e5-50a29094cd93" />

Note that if you use this script with a .env file already present it will overwrite any existing data. Upon using the script, you will also be given a custom session key to be used when you log in.

# Starting the server

Couldntaffordwp now comes with WSGI deployability. This can then be used with a reverse proxy server such as Nginx safely in production. To start the application with gunicorn:

`gunicorn --workers 3 --bind 127.0.0.1:8000 app:app`

# Example: Reverse proxy with Nginx

Read <a href='https://flask.palletsprojects.com/en/stable/deploying/nginx/'>this</a> to learn how to use Nginx as a reverse proxy server. I'll also add that in your 'sites-enabled' folder for Nginx you should create a symlink to the file for your blog in the 'sites-available' folder, and make sure there aren't any clashes with any other sites you might have enabled.

# Logging into the application remotely

CAWP comes with a login page, /login. Once you have started the Flask server, Enter the private username/password combination on that screen to start a session. You will be able to create and edit posts.

# More information

- Flask documentation: https://flask.palletsprojects.com/en/stable/
