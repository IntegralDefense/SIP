#!/usr/bin/env python3

import getpass
import os


"""
FLAGS
"""

BUILD_DEV = False
BUILD_TEST = False
BUILD_PROD = False

MYSQL_ERASE_DATABASE_DEV = False
MYSQL_ERASE_DATABASE_TEST = False
MYSQL_ERASE_DATABASE_PROD = False
MYSQL_SET_ROOT_PASSWORD = False
MYSQL_SET_USER_PASSWORD = False

NGINX_GENERATE_CERTIFICATE = False


"""
PATHS
"""


THIS_DIR = os.path.dirname(os.path.abspath(__file__))

MYSQL_CREATE_SQL_PATH = os.path.join(THIS_DIR, 'services', 'db', 'create.sql')
MYSQL_DOCKER_ENV_DEV = os.path.join(THIS_DIR, 'services', 'db', 'docker-DEV.env')
MYSQL_DOCKER_ENV_TEST = os.path.join(THIS_DIR, 'services', 'db', 'docker-TEST.env')
MYSQL_DOCKER_ENV_PROD = os.path.join(THIS_DIR, 'services', 'db', 'docker-PROD.env')

NGINX_CERTS_DIR = os.path.join(THIS_DIR, 'services', 'nginx', 'certs')
NGINX_CERT_PATH = os.path.join(THIS_DIR, 'services', 'nginx', 'certs', 'cert.pem')
NGINX_KEY_PATH = os.path.join(THIS_DIR, 'services', 'nginx', 'certs', 'key.pem')

WEB_DOCKER_ENV_DEV = os.path.join(THIS_DIR, 'services', 'web', 'docker-DEV.env')
WEB_DOCKER_ENV_TEST = os.path.join(THIS_DIR, 'services', 'web', 'docker-TEST.env')
WEB_DOCKER_ENV_PROD = os.path.join(THIS_DIR, 'services', 'web', 'docker-PROD.env')


"""
CONFIG
"""


MYSQL_ROOT_PASS = None
MYSQL_USER = None
MYSQL_PASS = None
MYSQL_CREATE_SQL = """CREATE DATABASE SIP;

CREATE USER '{user}'@'localhost' IDENTIFIED BY '{password}';

GRANT ALL PRIVILEGES ON SIP.* TO '{user}'@localhost;
GRANT ALL PRIVILEGES ON SIP.* TO '{user}'@'%';
"""

MYSQL_DOCKER_ENV = """MYSQL_HOST=localhost
MYSQL_ROOT_PASSWORD={root_password}
MYSQL_USER={user}
MYSQL_PASSWORD={password}
"""

FLASK_SECRET_KEY = os.urandom(48).hex()
FLASK_SECURITY_PASSWORD_SALT = os.urandom(48).hex()
WEB_DOCKER_ENV = """FLASK_APP=project
FLASK_ENV={environment}
APP_SETTINGS={config}
DATABASE_URL=mysql+mysqldb://{user}:{password}@db:3306/SIP?charset=utf8mb4
SECRET_KEY={secret_key}
SECURITY_PASSWORD_SALT={salt}
"""


"""
ENVIRONMENT SETUP
"""


confirm = input('Build a DEV environment (y/N)? ')
if confirm.lower() == 'y':
    BUILD_DEV = True
    BUILD_TEST = True

confirm = input('Build a PRODUCTION environment (y/N)? ')
if confirm.lower() == 'y':
    BUILD_PROD = True
    BUILD_TEST = True

print()


"""
MYSQL SETUP
"""


# MYSQL: Erase any existing databases
if os.path.exists(MYSQL_CREATE_SQL_PATH):

    if BUILD_DEV:
        confirm = input('Erase any existing DEV database (y/N)? ')
        if confirm.lower() == 'y':
            MYSQL_ERASE_DATABASE_DEV = True
            os.system('docker-compose -f docker-compose-DEV.yml down -v')
            os.system('docker-compose -f docker-compose-TEST.yml down -v')
            print()

    if BUILD_PROD:
        confirm = input('Erase any existing PRODUCTION database (y/N)? ')
        if confirm.lower() == 'y':
            confirm2 = input('Are you sure (y/N)? ')
            if confirm2.lower() == 'y':
                MYSQL_ERASE_DATABASE_PROD = True
                os.system('docker-compose -f docker-compose-PROD.yml down -v')
                os.system('docker-compose -f docker-compose-TEST.yml down -v')
                print()
else:
    MYSQL_ERASE_DATABASE_DEV = True
    MYSQL_ERASE_DATABASE_TEST = True
    MYSQL_ERASE_DATABASE_PROD = True

# MYSQL: Reset the root password
if not os.path.exists(MYSQL_CREATE_SQL_PATH) or input('MYSQL: Reset the root password (y/N)? ').lower() == 'y':
    MYSQL_SET_ROOT_PASSWORD = True
    MYSQL_ROOT_PASS = True
    mysql_root_pass2 = False
    while MYSQL_ROOT_PASS != mysql_root_pass2:
        MYSQL_ROOT_PASS = getpass.getpass('MYSQL root password: ')
        mysql_root_pass2 = getpass.getpass('Confirm: ')
    print()

# MYSQL: Reset the username and password
if not os.path.exists(MYSQL_CREATE_SQL_PATH) or input('MYSQL: Reset the username and password (y/N)? ').lower() == 'y':
    MYSQL_SET_USER_PASSWORD = True
    MYSQL_USER = input('MYSQL username: ')
    MYSQL_PASS = True
    mysql_pass2 = False
    while MYSQL_PASS != mysql_pass2:
        MYSQL_PASS = getpass.getpass('MYSQL password: ')
        mysql_pass2 = getpass.getpass('Confirm: ')
    print()

# MYSQL: Write the create.sql file
if not os.path.exists(MYSQL_CREATE_SQL_PATH) or MYSQL_SET_USER_PASSWORD:
    output = MYSQL_CREATE_SQL.format(user=MYSQL_USER, password=MYSQL_PASS)
    with open(MYSQL_CREATE_SQL_PATH, 'w') as f:
        f.write(output)

# MYSQL: Write the docker.env files
if BUILD_DEV:
    if not os.path.exists(MYSQL_DOCKER_ENV_DEV) or MYSQL_SET_ROOT_PASSWORD or MYSQL_SET_USER_PASSWORD:
        output = MYSQL_DOCKER_ENV.format(root_password=MYSQL_ROOT_PASS, user=MYSQL_USER, password=MYSQL_PASS)
        with open(MYSQL_DOCKER_ENV_DEV, 'w') as f:
            f.write(output)

if BUILD_TEST:
    if not os.path.exists(MYSQL_DOCKER_ENV_TEST) or MYSQL_SET_ROOT_PASSWORD or MYSQL_SET_USER_PASSWORD:
        output = MYSQL_DOCKER_ENV.format(root_password=MYSQL_ROOT_PASS, user=MYSQL_USER, password=MYSQL_PASS)
        with open(MYSQL_DOCKER_ENV_TEST, 'w') as f:
            f.write(output)

if BUILD_PROD:
    if not os.path.exists(MYSQL_DOCKER_ENV_PROD) or MYSQL_SET_ROOT_PASSWORD or MYSQL_SET_USER_PASSWORD:
        output = MYSQL_DOCKER_ENV.format(root_password=MYSQL_ROOT_PASS, user=MYSQL_USER, password=MYSQL_PASS)
        with open(MYSQL_DOCKER_ENV_PROD, 'w') as f:
            f.write(output)


"""
NGINX SETUP
"""


# NGINX: Generate a certificate
if not os.path.exists(NGINX_CERTS_DIR):
    os.makedirs(NGINX_CERTS_DIR)
confirm = input('NGINX: Generate a self-signed certificate (y/N)? ')
if confirm.lower() == 'y':
    print()
    os.system('openssl req -x509 -newkey rsa:2048 -nodes -keyout {key} -out {cert} -days 1095'.format(key=NGINX_KEY_PATH, cert=NGINX_CERT_PATH))
    print()
else:
    if not os.path.exists(NGINX_CERT_PATH) or not os.path.exists(NGINX_KEY_PATH):
        print('!!! You chose not to create a self-signed certificate !!!')
        print('!!! You must supply your own certificate !!!')
        print()
        print('Place certificate here: {}'.format(NGINX_CERT_PATH))
        print('Place key here: {}'.format(NGINX_KEY_PATH))
        print()


"""
WEB SETUP
"""


# WEB: Write the docker.env files
if BUILD_DEV:
    if not os.path.exists(WEB_DOCKER_ENV_DEV) or MYSQL_SET_USER_PASSWORD:
        output = WEB_DOCKER_ENV.format(environment='development',
                                       config='project.config.DevelopmentConfig',
                                       user=MYSQL_USER,
                                       password=MYSQL_PASS,
                                       secret_key=FLASK_SECRET_KEY,
                                       salt=FLASK_SECURITY_PASSWORD_SALT)
        with open(WEB_DOCKER_ENV_DEV, 'w') as f:
            f.write(output)

if BUILD_TEST:
    if not os.path.exists(WEB_DOCKER_ENV_TEST) or MYSQL_SET_USER_PASSWORD:
        output = WEB_DOCKER_ENV.format(environment='production',
                                       config='project.config.TestingConfig',
                                       user=MYSQL_USER,
                                       password=MYSQL_PASS,
                                       secret_key=FLASK_SECRET_KEY,
                                       salt=FLASK_SECURITY_PASSWORD_SALT)
        with open(WEB_DOCKER_ENV_TEST, 'w') as f:
            f.write(output)

if BUILD_PROD:
    if not os.path.exists(WEB_DOCKER_ENV_PROD) or MYSQL_SET_USER_PASSWORD:
        output = WEB_DOCKER_ENV.format(environment='production',
                                       config='project.config.ProductionConfig',
                                       user=MYSQL_USER,
                                       password=MYSQL_PASS,
                                       secret_key=FLASK_SECRET_KEY,
                                       salt=FLASK_SECURITY_PASSWORD_SALT)
        with open(WEB_DOCKER_ENV_PROD, 'w') as f:
            f.write(output)


"""
BUILD DOCKER CONTAINERS
"""


if BUILD_DEV:
    os.system('docker-compose -f docker-compose-DEV.yml build')

if BUILD_TEST:
    os.system('docker-compose -f docker-compose-TEST.yml build')

if BUILD_PROD:
    os.system('docker-compose -f docker-compose-PROD.yml build')


"""
SUMMARY MESSAGES
"""

print()
print()

print('===  SUMMARY  ===')
print()

print('MYSQL: Review create.sql: {}'.format(MYSQL_CREATE_SQL_PATH))

if BUILD_DEV:
    print('MYSQL: Review the DEV environment variables: {}'.format(MYSQL_DOCKER_ENV_DEV))

if BUILD_TEST:
    print('MYSQL: Review the TEST environment variables: {}'.format(MYSQL_DOCKER_ENV_TEST))

if BUILD_PROD:
    print('MYSQL: Review the PRODUCTION environment variables: {}'.format(MYSQL_DOCKER_ENV_PROD))

print()

if os.path.exists(NGINX_CERT_PATH):
    print('NGINX: Certificate: {}'.format(NGINX_CERT_PATH))
else:
    print('NGINX: MISSING CERTIFICATE: {}'.format(NGINX_CERT_PATH))

if os.path.exists(NGINX_KEY_PATH):
    print('NGINX: Certificate key: {}'.format(NGINX_KEY_PATH))
else:
    print('NGINX: MISSING CERTIFICATE KEY: {}'.format(NGINX_CERT_PATH))

print()

if BUILD_DEV:
    print('WEB: Review the DEV environment variables: {}'.format(WEB_DOCKER_ENV_DEV))

if BUILD_TEST:
    print('WEB: Review the TEST environment variables: {}'.format(WEB_DOCKER_ENV_TEST))

if BUILD_PROD:
    print('WEB: Review the PRODUCTION environment variables: {}'.format(WEB_DOCKER_ENV_PROD))

if BUILD_DEV and MYSQL_ERASE_DATABASE_DEV:
    print()
    print('===  FINISH DEV SETUP  ===')
    os.system(os.path.join(THIS_DIR, 'bin', 'initialize-DEV.sh'))

if BUILD_PROD and MYSQL_ERASE_DATABASE_PROD:
    print()
    print('===  FINISH PROD SETUP  ===')
    os.system(os.path.join(THIS_DIR, 'bin', 'initialize-PROD.sh'))
