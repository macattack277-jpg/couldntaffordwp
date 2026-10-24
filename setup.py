# Modules
from getpass import getpass
from os import environ
from dotenv import load_dotenv
from pathlib import Path
from sys import exit
import bcrypt
import secrets


# The .env path should be here
env = Path('.env')

if env.exists():
	action = input('! You seem to already have a .env file in your working directory. Continuing with the setup will overwrite any existing credentials you have set. Are you sure you want to continue? (y/n) ')
	if action == 'y':
		pass
	else:
		exit()

# Create the .env file for credentials
with open('.env', 'w') as file:
	file.write('# .env')
	file.close()

# Ensure that the custom environment is being used
load_dotenv(dotenv_path='.env', override='True')

print('Welcome to the Couldntaffordwp setup wizard! In the current version, you must change the .env variables directly if you wish to update any of these details.')
environ['PUBLIC_NAME'] = input('Enter your public name (showed on your profile): ')
environ['USERNAME'] = input('Enter your private name (used to log you in): ')
while True:
	password = getpass(prompt='Enter your password: ').encode('utf-8')
	passwordconfirm = getpass(prompt='Enter your password: ').encode('utf-8')
	if password == passwordconfirm:
		break
	else:
		print('Passwords did not match!')
salt = bcrypt.gensalt()
environ['HASH'] = str(bcrypt.hashpw(password, salt))
environ['SECRET_KEY'] = secrets.token_hex(32)
print('Done!')
