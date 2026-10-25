from getpass import getpass
from os import environ
from dotenv import load_dotenv, set_key
from pathlib import Path
from sys import exit
import bcrypt
import secrets

# This was made partly with AI because I originally wrote it trying to use a different method for setting the .env variables but it didn't work so I couldn't be bothered changing that part by hand

env_path = Path('.env')

if env_path.exists():
    action = input('! You seem to already have a .env file in your working directory. Continuing with the setup will overwrite any existing credentials you have set. Are you sure you want to continue? (y/n) ')
    if action.lower() != 'y':
        exit()

# Create / clear the .env file
env_path.write_text('# .env\n')

# Optional: load it (not really needed here since the file is empty)
load_dotenv(dotenv_path=env_path, override=True)

print('Welcome to the Couldntaffordwp setup wizard! In the current version, you must change the .env variables directly if you wish to update any of these details.')

public_name = input('Enter your public name (showed on your profile): ')
username = input('Enter your private name (used to log you in): ')

while True:
    password = getpass(prompt='Enter your password: ').encode('utf-8')
    passwordconfirm = getpass(prompt='Enter your password: ').encode('utf-8')
    if password == passwordconfirm:
        break
    print('Passwords did not match!')

salt = bcrypt.gensalt()
password_hash = str(bcrypt.hashpw(password, salt))
secret_key = secrets.token_hex(32)

# Actually write the values into the .env file
set_key(env_path, 'PUBLIC_NAME', public_name)
set_key(env_path, 'USERNAME', username)
set_key(env_path, 'HASH', password_hash)
set_key(env_path, 'SECRET_KEY', secret_key)

print('Done! Credentials written to .env')
