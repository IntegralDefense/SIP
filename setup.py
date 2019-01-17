#!/usr/bin/env python3

import getpass
import os

this_dir = os.path.dirname(os.path.abspath(__file__))

# Set the PostgreSQL username/password
postgres_user = input('User for PostgreSQL database: ')
postgres_pass = True
postgres_pass2 = False
while postgres_pass != postgres_pass2:
    postgres_pass = getpass.getpass('Password for PostgreSQL user: ')
    postgres_pass2 = getpass.getpass('Confirm password: ')

# Write the services/web/docker.env file
output = """FLASK_ENV=production
APP_SETTINGS=project.config.ProductionConfig
DATABASE_URL=postgres://{user}:{password}@db:5432/intelooper
DATABASE_TEST_URL=postgres://{user}:{password}@db:5432/intelooper_test
""".format(user=postgres_user, password=postgres_pass)

print()

with open('./services/web/docker.env', 'w') as f:
    f.write(output)
    print('Review the environment variables: ./services/web/docker.env')

# Write the services/web/project/db/docker.env file
output = """POSTGRES_USER={user}
POSTGRES_PASSWORD={password}
""".format(user=postgres_user, password=postgres_pass)

with open('./services/web/project/db/docker.env', 'w') as f:
    f.write(output)
    print('Review the environment variables: ./services/web/project/db/docker.env')

print()

# Generate a certificate
cert_path = os.path.join(this_dir, 'services', 'nginx', 'certs', 'cert.pem')
key_path = os.path.join(this_dir, 'services', 'nginx', 'certs', 'key.pem')
generate = input('Generate a self-signed certificate (y/n)? ')
print()
if generate.lower() == 'y':
    os.system('openssl req -x509 -newkey rsa:2048 -nodes -keyout {key} -out {cert} -days 1095'.format(key=key_path, cert=cert_path))
else:
    print('!!! You chose not to create a self-signed certificate !!!')
    print('!!! You must supply your own certificate !!!')
    print()
    print('Place certificate here: {}'.format(cert_path))
    print('Place key here: {}'.format(key_path))

print()

# Write the services/web/project/.env file
secret_key = os.urandom(48).hex()
security_password_salt = os.urandom(48).hex()
output = """SECRET_KEY={secret_key}
SECURITY_PASSWORD_SALT={security_password_salt}
""".format(secret_key=secret_key, security_password_salt=security_password_salt)

with open('./services/web/project/.env', 'w') as f:
    f.write(output)
    print('Review the Flask environment variables: ./services/web/project/.env')

print()

# Run the manage.py setup command
print('Review the setup config (and edit if necessary): ./services/web/etc/setup.ini')
answer = input('Did you review it (y/n)? ')
if answer.lower() == 'y':
    print('Erasing the database...')
    os.system('docker-compose run web python manage.py nukedb')
    os.system('docker-compose run web python manage.py setup')
