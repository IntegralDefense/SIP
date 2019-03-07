.. _setup:

Setup
*****

.. contents::
  :backlinks: none

Configuration
-------------

Before you run the included setup script, you should review the setup configuration file:

::

    services/web/etc/setup.ini

This file contains a list of initial values that will be added to the database during setup.

The values include:

- Indicator confidences (first value will be used as the default)
- Indicator impacts (first value will be used as the default)
- Indicator statuses (first value will be used as the default)
- Indicator types
- Intel sources

Setup Script
------------

The included setup script will walk you through the installation and configuration of SIP:

::

   $ ./setup.py

The setup script will walk you through:

- Creating dev/test/production Docker environments
- Setting the MySQL root user password
- Creating a non-root MySQL user and password
- Creating an optional self-signed HTTPS certificate

If you choose not to create a self-signed certificate, the script will notify you that you must supply your own certificate and where to place it.

Once you answer the setup script's questions, it will generate files containing the environment variables for the MySQL and Flask Docker containers. The paths to these files will be shown by the setup script for you to review.

**MAKE SURE TO NOTE THE RANDOM ADMIN PASSWORD REPORTED AT THE END BY THE SETUP SCRIPT!**

Example
-------

Example output from the setup script is shown below:

::

   Build a DEV environment (y/N)? y
   Build a PRODUCTION environment (y/N)? n

   MYSQL root password:
   Confirm:

   MYSQL username: SIP
   MYSQL password:
   Confirm:

   NGINX: Generate a self-signed certificate (y/N)? y

   Generating a 2048 bit RSA private key
   ....................................+++
   ................+++
   writing new private key to '/home/dev/SIP/services/nginx/certs/key.pem'
   -----
   You are about to be asked to enter information that will be incorporated
   into your certificate request.
   What you are about to enter is what is called a Distinguished Name or a DN.
   There are quite a few fields but you can leave some blank
   For some fields there will be a default value,
   If you enter '.', the field will be left blank.
   -----
   Country Name (2 letter code) [AU]:US
   State or Province Name (full name) [Some-State]:Somewhere
   Locality Name (eg, city) []:Someplace
   Organization Name (eg, company) [Internet Widgits Pty Ltd]:Integral Defense
   Organizational Unit Name (eg, section) []:
   Common Name (e.g. server FQDN or YOUR name) []:sip.local
   Email Address []:

   Building db-dev
   Step 1/3 : FROM mysql:8.0.15
    ---> 81f094a7e4cc
   Step 2/3 : ADD create.sql /docker-entrypoint-initdb.d
    ---> Using cache
    ---> e7a82071400a
   Step 3/3 : ADD conf.d/ /etc/mysql/conf.d
    ---> Using cache
    ---> 7a89a9af0aef
   Successfully built 7a89a9af0aef
   Successfully tagged sip_db-dev:latest
   Building web-dev
   Step 1/8 : FROM pypy:3
    ---> dc6a60638123
   Step 2/8 : RUN apt-get update && apt-get install -y mysql-client
    ---> Using cache
    ---> 824a8a8c41b8
   Step 3/8 : WORKDIR /usr/src/app
    ---> Using cache
    ---> 31e50c746580
   Step 4/8 : COPY ./requirements.txt /usr/src/app/requirements.txt
    ---> Using cache
    ---> bf7180697bde
   Step 5/8 : RUN pip install -r requirements.txt
    ---> Using cache
    ---> e5db87e9dfca
   Step 6/8 : COPY ./entrypoint-DEV.sh /usr/src/app/entrypoint-DEV.sh
    ---> Using cache
    ---> 18ad61b7f770
   Step 7/8 : COPY . /usr/src/app
    ---> 74a7f1ef420e
   Step 8/8 : CMD ["/usr/src/app/entrypoint-DEV.sh"]
    ---> Running in 3751f57a9945
   Removing intermediate container 3751f57a9945
    ---> adb4c05e4380
   Successfully built adb4c05e4380
   Successfully tagged sip_web-dev:latest
   Building nginx-dev
   Step 1/4 : FROM nginx:1.15.6-alpine
    ---> d3dcc25e0dc4
   Step 2/4 : RUN rm /etc/nginx/conf.d/default.conf
    ---> Using cache
    ---> 0a7e23e8e331
   Step 3/4 : COPY ./server-DEV.conf /etc/nginx/conf.d
    ---> Using cache
    ---> 9711b1acf628
   Step 4/4 : ADD certs/ /etc/nginx/certs
    ---> Using cache
    ---> a7d1430078a5
   Successfully built a7d1430078a5
   Successfully tagged sip_nginx-dev:latest
   Building db-test
   Step 1/3 : FROM mysql:8.0
    ---> 81f094a7e4cc
   Step 2/3 : ADD create.sql /docker-entrypoint-initdb.d
    ---> Using cache
    ---> e7a82071400a
   Step 3/3 : ADD conf.d/ /etc/mysql/conf.d
    ---> Using cache
    ---> 7a89a9af0aef
   Successfully built 7a89a9af0aef
   Successfully tagged sip_db-test:latest
   Building web-test
   Step 1/8 : FROM pypy:3
    ---> dc6a60638123
   Step 2/8 : RUN apt-get update && apt-get install -y mysql-client
    ---> Using cache
    ---> 824a8a8c41b8
   Step 3/8 : WORKDIR /usr/src/app
    ---> Using cache
    ---> 31e50c746580
   Step 4/8 : COPY ./requirements.txt /usr/src/app/requirements.txt
    ---> Using cache
    ---> bf7180697bde
   Step 5/8 : RUN pip install -r requirements.txt
    ---> Using cache
    ---> e5db87e9dfca
   Step 6/8 : COPY ./entrypoint-TEST.sh /usr/src/app/entrypoint-TEST.sh
    ---> Using cache
    ---> b8e995a98fb7
   Step 7/8 : COPY . /usr/src/app
    ---> 0fe5d3d26f63
   Step 8/8 : CMD ["/usr/src/app/entrypoint-TEST.sh"]
    ---> Running in b0d24537eb35
   Removing intermediate container b0d24537eb35
    ---> 2fd2f016e9ee
   Successfully built 2fd2f016e9ee
   Successfully tagged sip_web-test:latest
   Building nginx-test
   Step 1/4 : FROM nginx:1.15.6-alpine
    ---> d3dcc25e0dc4
   Step 2/4 : RUN rm /etc/nginx/conf.d/default.conf
    ---> Using cache
    ---> 0a7e23e8e331
   Step 3/4 : COPY ./server-TEST.conf /etc/nginx/conf.d
    ---> Using cache
    ---> aababc77bff6
   Step 4/4 : ADD certs/ /etc/nginx/certs
    ---> Using cache
    ---> 19b43be1c9b2
   Successfully built 19b43be1c9b2
   Successfully tagged sip_nginx-test:latest


   ===  SUMMARY  ===

   MYSQL: Review create.sql: /home/dev/SIP/services/db/create.sql
   MYSQL: Review the DEV environment variables: /home/dev/SIP/services/db/docker-DEV.env
   MYSQL: Review the TEST environment variables: /home/dev/SIP/services/db/docker-TEST.env

   NGINX: Certificate: /home/dev/SIP/services/nginx/certs/cert.pem
   NGINX: Certificate key: /home/dev/SIP/services/nginx/certs/key.pem

   WEB: Review the DEV environment variables: /home/dev/SIP/services/web/docker-DEV.env
   WEB: Review the TEST environment variables: /home/dev/SIP/services/web/docker-TEST.env

   ===  FINISH DEV SETUP  ===
   Creating network "sip_dev" with driver "bridge"
   Creating volume "sip_mysql-dev" with local driver
   Creating sip_db-dev_1 ...
   Creating sip_db-dev_1 ... done
   Creating sip_web-dev_1 ...
   Creating sip_web-dev_1 ... done
   Creating sip_nginx-dev_1 ...
   Creating sip_nginx-dev_1 ... done
   Waiting for SIP (DEV) to start...
   Waiting for SIP (DEV) to start...
   Waiting for SIP (DEV) to start...
   Waiting for SIP (DEV) to start...
   Waiting for SIP (DEV) to start...
   Waiting for SIP (DEV) to start...
   Waiting for SIP (DEV) to start...
   Waiting for SIP (DEV) to start...
   Waiting for SIP (DEV) to start...
   Waiting for SIP (DEV) to start...
   Waiting for SIP (DEV) to start...
   Waiting for SIP (DEV) to start...
   Waiting for SIP (DEV) to start...
   Waiting for SIP (DEV) to start...
   Waiting for SIP (DEV) to start...
   Stopping sip_nginx-dev_1 ... done
   Stopping sip_web-dev_1   ... done
   Stopping sip_db-dev_1    ... done
   Removing sip_nginx-dev_1 ... done
   Removing sip_web-dev_1   ... done
   Removing sip_db-dev_1    ... done
   Removing network sip_dev
   Creating network "sip_dev" with driver "bridge"
   Creating sip_db-dev_1 ...
   Creating sip_db-dev_1 ... done
   Starting sip_db-dev_1 ... done
   [2019-03-07 15:53:22,746] INFO in __init__: SIP starting
   [2019-03-07 15:53:23,102] INFO in __init__: SIP starting
   [2019-03-07 15:53:23,191] INFO in manage: SETUP: Created user role: admin
   [2019-03-07 15:53:23,209] INFO in manage: SETUP: Created user role: analyst
   [2019-03-07 15:53:23,227] INFO in manage: SETUP: Created indicator confidence: LOW
   [2019-03-07 15:53:23,244] INFO in manage: SETUP: Created indicator confidence: MEDIUM
   [2019-03-07 15:53:23,262] INFO in manage: SETUP: Created indicator confidence: HIGH
   [2019-03-07 15:53:23,280] INFO in manage: SETUP: Created indicator impact: LOW
   [2019-03-07 15:53:23,297] INFO in manage: SETUP: Created indicator impact: MEDIUM
   [2019-03-07 15:53:23,315] INFO in manage: SETUP: Created indicator impact: HIGH
   [2019-03-07 15:53:23,332] INFO in manage: SETUP: Created indicator status: NEW
   [2019-03-07 15:53:23,350] INFO in manage: SETUP: Created indicator status: FA
   [2019-03-07 15:53:23,368] INFO in manage: SETUP: Created indicator status: IN PROGRESS
   [2019-03-07 15:53:23,386] INFO in manage: SETUP: Created indicator status: ANALYZED
   [2019-03-07 15:53:23,404] INFO in manage: SETUP: Created indicator status: INFORMATIONAL
   [2019-03-07 15:53:23,423] INFO in manage: SETUP: Created indicator status: DEPRECATED
   [2019-03-07 15:53:23,440] INFO in manage: SETUP: Created indicator type: Address - ipv4-addr
   [2019-03-07 15:53:23,458] INFO in manage: SETUP: Created indicator type: Email - Address
   [2019-03-07 15:53:23,476] INFO in manage: SETUP: Created indicator type: Email - Content
   [2019-03-07 15:53:23,494] INFO in manage: SETUP: Created indicator type: Email - Subject
   [2019-03-07 15:53:23,511] INFO in manage: SETUP: Created indicator type: Hash - MD5
   [2019-03-07 15:53:23,529] INFO in manage: SETUP: Created indicator type: Hash - SHA1
   [2019-03-07 15:53:23,547] INFO in manage: SETUP: Created indicator type: Hash - SHA256
   [2019-03-07 15:53:23,566] INFO in manage: SETUP: Created indicator type: URI - Domain Name
   [2019-03-07 15:53:23,584] INFO in manage: SETUP: Created indicator type: URI - Path
   [2019-03-07 15:53:23,601] INFO in manage: SETUP: Created indicator type: URI - URL
   [2019-03-07 15:53:23,619] INFO in manage: SETUP: Created intel source: OSINT
   [2019-03-07 15:53:23,679] INFO in manage: SETUP: Created admin user with password: o@eV5x=oU{W][4T>o?_m