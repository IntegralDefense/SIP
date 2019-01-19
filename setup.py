#!/usr/bin/env python3

import getpass
import os

this_dir = os.path.dirname(os.path.abspath(__file__))

# Generate a certificate
cert_path = os.path.join(this_dir, 'services', 'nginx', 'certs', 'cert.pem')
key_path = os.path.join(this_dir, 'services', 'nginx', 'certs', 'key.pem')
generate = input('Generate a self-signed certificate (y/n)? ')
print()
if generate.lower() == 'y':
    os.system('openssl req -x509 -newkey rsa:2048 -nodes -keyout {key} -out {cert} -days 1095'.format(key=key_path, cert=cert_path))
else:
    if not os.path.exists(cert_path) or not os.path.exists(key_path):
        print('!!! You chose not to create a self-signed certificate !!!')
        print('!!! You must supply your own certificate !!!')
        print()
        print('Place certificate here: {}'.format(cert_path))
        print('Place key here: {}'.format(key_path))
        print()

# Set the MySQL root password
mysql_root_pass = True
mysql_root_pass2 = False
while mysql_root_pass != mysql_root_pass2:
    mysql_root_pass = getpass.getpass('Password for MySQL root user: ')
    mysql_root_pass2 = getpass.getpass('Confirm password: ')

# Set the MySQL username/password
mysql_user = input('User for MySQL database: ')
mysql_pass = True
mysql_pass2 = False
while mysql_pass != mysql_pass2:
    mysql_pass = getpass.getpass('Password for MySQL user: ')
    mysql_pass2 = getpass.getpass('Confirm password: ')

print()

# Write the services/db/create.sql file
output = """CREATE DATABASE SIP;
CREATE DATABASE SIP_test;

CREATE USER '{user}'@'localhost' IDENTIFIED BY '{password}';

GRANT ALL PRIVILEGES ON SIP.* TO '{user}'@localhost;
GRANT ALL PRIVILEGES ON SIP.* TO '{user}'@'%';
GRANT ALL PRIVILEGES ON SIP_test.* TO '{user}'@localhost;
GRANT ALL PRIVILEGES ON SIP_test.* TO '{user}'@'%';
""".format(user=mysql_user, password=mysql_pass)

with open('./services/db/create.sql', 'w') as f:
    f.write(output)
    print('Review the create.sql: ./services/db/create.sql')

# Write the services/db/.env file
output = """MYSQL_HOST=localhost
MYSQL_ROOT_PASSWORD={root_password}
MYSQL_USER={user}
MYSQL_PASSWORD={password}
""".format(root_password=mysql_root_pass, user=mysql_user, password=mysql_pass)

output = """MYSQL_HOST=localhost
MYSQL_ROOT_PASSWORD={root_password}
""".format(root_password=mysql_root_pass)

with open('./services/db/.env', 'w') as f:
    f.write(output)
    print('Review the environment variables: ./services/db/.env')

# Write the services/web/docker.env file
output = """FLASK_ENV=production
APP_SETTINGS=project.config.ProductionConfig
DATABASE_URL=mysql+pymysql://{user}:{password}@db:3306/SIP
DATABASE_TEST_URL=mysql+pymysql://{user}:{password}@db:3306/SIP_test
""".format(user=mysql_user, password=mysql_pass)

with open('./services/web/docker.env', 'w') as f:
    f.write(output)
    print('Review the environment variables: ./services/web/docker.env')

# Write the services/web/project/docker.env file
secret_key = os.urandom(48).hex()
security_password_salt = os.urandom(48).hex()
output = """SECRET_KEY={secret_key}
SECURITY_PASSWORD_SALT={security_password_salt}
""".format(secret_key=secret_key, security_password_salt=security_password_salt)

with open('./services/web/project/docker.env', 'w') as f:
    f.write(output)
    print('Review the Flask environment variables: ./services/web/project/docker.env')

print()

# Erase any existing database
answer = input('Erase any existing database (y/n)? ')
if answer.lower() == 'y':
    os.system('docker-compose down -v')

# Build the containers
os.system('docker-compose build')
