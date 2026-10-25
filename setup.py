from getpass import getpass
from os import environ
from dotenv import load_dotenv, set_key
from pathlib import Path
from sys import exit
import bcrypt
import secrets

# Made this partly with AI because I had to fix a bunch of stuff and cbf rewriting by hand

env_path = Path('.env')

if env_path.exists():
    action = input('! You seem to already have a .env file in your working directory. Continuing with the setup will overwrite any existing credentials you have set. Are you sure you want to continue? (y/n) ')
    if action.lower() != 'y':
        exit()

# Create a fresh .env file
env_path.write_text('# .env\n')

load_dotenv(dotenv_path=env_path, override=True)

print('Welcome to the Couldntaffordwp setup wizard!')
print('In the current version, you must change the .env variables directly if you wish to update any of these details.\n')

public_name = input('Enter your public name (showed on your profile): ')
username = input('Enter your private name (used to log you in): ')

while True:
    password = getpass(prompt='Enter your password: ').encode('utf-8')
    password_confirm = getpass(prompt='Confirm your password: ').encode('utf-8')
    
    if password == password_confirm:
        break
    print('Passwords did not match! Try again.\n')

# Generate salt + hash
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(password, salt)

# Important: decode the bytes so we store a clean string like $2b$12$...
hashed_str = hashed.decode('utf-8')

secret_key = secrets.token_hex(32)

# Write everything cleanly into the .env file
set_key(env_path, 'PUBLIC_NAME', public_name)
set_key(env_path, 'USERNAME', username)
set_key(env_path, 'HASH', hashed_str)
set_key(env_path, 'SECRET_KEY', secret_key)

print('\nDone! Credentials have been written to .env')
