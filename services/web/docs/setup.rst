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

- Event attack vectors
- Event dispositions (first value will be used as the default)
- Event prevention tools
- Event remediations
- Event statuses (first value will be used as the default)
- Event types
- Indicator confidences (first value will be used as the default)
- Indicator impacts (first value will be used as the default)
- Indicator statuses (first value will be used as the default)
- Indicator types
- Intel sources
- Malware types

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
    ---> adf5d5cee3b1
   Step 8/8 : CMD ["/usr/src/app/entrypoint-DEV.sh"]
    ---> Running in 5e35098b74e0
   Removing intermediate container 5e35098b74e0
    ---> 85357ee46ca2
   Successfully built 85357ee46ca2
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
    ---> 39be5399dbd1
   Successfully built 39be5399dbd1
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
    ---> 3b1298a3f8f4
   Step 8/8 : CMD ["/usr/src/app/entrypoint-TEST.sh"]
    ---> Running in da5963ccd374
   Removing intermediate container da5963ccd374
    ---> 70ffc212cf88
   Successfully built 70ffc212cf88
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
    ---> 783fe60f3cb5
   Successfully built 783fe60f3cb5
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
   sip_db-dev_1 is up-to-date
   Creating sip_web-dev_1 ...
   Creating sip_web-dev_1 ... done
   Creating sip_nginx-dev_1 ...
   Creating sip_nginx-dev_1 ... done
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
   [2019-03-01 23:15:46,027] INFO in __init__: SIP starting
   [2019-03-01 23:15:46,496] INFO in __init__: SIP starting
   [2019-03-01 23:15:46,652] INFO in manage: SETUP: Created user role: admin
   [2019-03-01 23:15:46,682] INFO in manage: SETUP: Created user role: analyst
   [2019-03-01 23:15:46,716] INFO in manage: SETUP: Created event attack vector: UNKNOWN
   [2019-03-01 23:15:46,735] INFO in manage: SETUP: Created event attack vector: CORPORATE EMAIL
   [2019-03-01 23:15:46,753] INFO in manage: SETUP: Created event attack vector: USB
   [2019-03-01 23:15:46,772] INFO in manage: SETUP: Created event attack vector: WEB BROWSING
   [2019-03-01 23:15:46,790] INFO in manage: SETUP: Created event attack vector: WEBMAIL
   [2019-03-01 23:15:46,808] INFO in manage: SETUP: Created event disposition: UNKNOWN
   [2019-03-01 23:15:46,826] INFO in manage: SETUP: Created event disposition: FALSE POSITIVE
   [2019-03-01 23:15:46,843] INFO in manage: SETUP: Created event disposition: IGNORE
   [2019-03-01 23:15:46,861] INFO in manage: SETUP: Created event disposition: REVIEWED
   [2019-03-01 23:15:46,878] INFO in manage: SETUP: Created event disposition: GRAYWARE
   [2019-03-01 23:15:46,896] INFO in manage: SETUP: Created event disposition: POLICY VIOLATION
   [2019-03-01 23:15:46,913] INFO in manage: SETUP: Created event disposition: RECONNAISSANCE
   [2019-03-01 23:15:46,931] INFO in manage: SETUP: Created event disposition: WEAPONIZATION
   [2019-03-01 23:15:46,949] INFO in manage: SETUP: Created event disposition: DELIVERY
   [2019-03-01 23:15:46,966] INFO in manage: SETUP: Created event disposition: EXPLOITATION
   [2019-03-01 23:15:46,984] INFO in manage: SETUP: Created event disposition: INSTALLATION
   [2019-03-01 23:15:47,002] INFO in manage: SETUP: Created event disposition: COMMAND AND CONTROL
   [2019-03-01 23:15:47,020] INFO in manage: SETUP: Created event disposition: EXFIL
   [2019-03-01 23:15:47,038] INFO in manage: SETUP: Created event disposition: DAMAGE
   [2019-03-01 23:15:47,055] INFO in manage: SETUP: Created event prevention tool: RESPONSE TEAM
   [2019-03-01 23:15:47,073] INFO in manage: SETUP: Created event prevention tool: IPS
   [2019-03-01 23:15:47,090] INFO in manage: SETUP: Created event prevention tool: FIREWALL
   [2019-03-01 23:15:47,108] INFO in manage: SETUP: Created event prevention tool: PROXY
   [2019-03-01 23:15:47,125] INFO in manage: SETUP: Created event prevention tool: ANTIVIRUS
   [2019-03-01 23:15:47,142] INFO in manage: SETUP: Created event prevention tool: EMAIL FILTER
   [2019-03-01 23:15:47,160] INFO in manage: SETUP: Created event prevention tool: APPLICATION WHITELIST
   [2019-03-01 23:15:47,177] INFO in manage: SETUP: Created event prevention tool: USER
   [2019-03-01 23:15:47,195] INFO in manage: SETUP: Created event remediation: NOT REMEDIATED
   [2019-03-01 23:15:47,212] INFO in manage: SETUP: Created event remediation: REMOVED FROM MAILBOX
   [2019-03-01 23:15:47,230] INFO in manage: SETUP: Created event remediation: CLEANED WITH ANTIVIRUS
   [2019-03-01 23:15:47,248] INFO in manage: SETUP: Created event remediation: CLEANED MANUALLY
   [2019-03-01 23:15:47,266] INFO in manage: SETUP: Created event remediation: REIMAGED
   [2019-03-01 23:15:47,284] INFO in manage: SETUP: Created event remediation: CREDENTIALS RESET
   [2019-03-01 23:15:47,302] INFO in manage: SETUP: Created event remediation: NOT APPLICABLE
   [2019-03-01 23:15:47,319] INFO in manage: SETUP: Created event status: OPEN
   [2019-03-01 23:15:47,336] INFO in manage: SETUP: Created event status: CLOSED
   [2019-03-01 23:15:47,354] INFO in manage: SETUP: Created event status: IGNORE
   [2019-03-01 23:15:47,371] INFO in manage: SETUP: Created event type: PHISH
   [2019-03-01 23:15:47,389] INFO in manage: SETUP: Created event type: RECONNAISSANSE
   [2019-03-01 23:15:47,407] INFO in manage: SETUP: Created event type: HOST COMPROMISE
   [2019-03-01 23:15:47,424] INFO in manage: SETUP: Created event type: CREDENTIAL COMPROMISE
   [2019-03-01 23:15:47,441] INFO in manage: SETUP: Created event type: WEB BROWSING
   [2019-03-01 23:15:47,460] INFO in manage: SETUP: Created indicator confidence: LOW
   [2019-03-01 23:15:47,477] INFO in manage: SETUP: Created indicator confidence: MEDIUM
   [2019-03-01 23:15:47,495] INFO in manage: SETUP: Created indicator confidence: HIGH
   [2019-03-01 23:15:47,525] INFO in manage: SETUP: Created indicator impact: LOW
   [2019-03-01 23:15:47,555] INFO in manage: SETUP: Created indicator impact: MEDIUM
   [2019-03-01 23:15:47,573] INFO in manage: SETUP: Created indicator impact: HIGH
   [2019-03-01 23:15:47,591] INFO in manage: SETUP: Created indicator status: NEW
   [2019-03-01 23:15:47,609] INFO in manage: SETUP: Created indicator status: FA
   [2019-03-01 23:15:47,626] INFO in manage: SETUP: Created indicator status: IN PROGRESS
   [2019-03-01 23:15:47,643] INFO in manage: SETUP: Created indicator status: ANALYZED
   [2019-03-01 23:15:47,661] INFO in manage: SETUP: Created indicator status: INFORMATIONAL
   [2019-03-01 23:15:47,679] INFO in manage: SETUP: Created indicator status: DEPRECATED
   [2019-03-01 23:15:47,696] INFO in manage: SETUP: Created indicator type: Address - ipv4-addr
   [2019-03-01 23:15:47,714] INFO in manage: SETUP: Created indicator type: Email - Address
   [2019-03-01 23:15:47,732] INFO in manage: SETUP: Created indicator type: Email - Content
   [2019-03-01 23:15:47,750] INFO in manage: SETUP: Created indicator type: Email - Subject
   [2019-03-01 23:15:47,768] INFO in manage: SETUP: Created indicator type: Hash - MD5
   [2019-03-01 23:15:47,786] INFO in manage: SETUP: Created indicator type: Hash - SHA1
   [2019-03-01 23:15:47,804] INFO in manage: SETUP: Created indicator type: Hash - SHA256
   [2019-03-01 23:15:47,822] INFO in manage: SETUP: Created indicator type: URI - Domain Name
   [2019-03-01 23:15:47,840] INFO in manage: SETUP: Created indicator type: URI - Path
   [2019-03-01 23:15:47,858] INFO in manage: SETUP: Created indicator type: URI - URL
   [2019-03-01 23:15:47,875] INFO in manage: SETUP: Created intel source: OSINT
   [2019-03-01 23:15:47,893] INFO in manage: SETUP: Created malware type: UNKNOWN
   [2019-03-01 23:15:47,911] INFO in manage: SETUP: Created malware type: CREDENTIAL HARVESTING
   [2019-03-01 23:15:47,929] INFO in manage: SETUP: Created malware type: BOTNET
   [2019-03-01 23:15:47,946] INFO in manage: SETUP: Created malware type: CLICK FRAUD
   [2019-03-01 23:15:47,964] INFO in manage: SETUP: Created malware type: DOWNLOADER
   [2019-03-01 23:15:47,982] INFO in manage: SETUP: Created malware type: INFOSTEALER
   [2019-03-01 23:15:47,999] INFO in manage: SETUP: Created malware type: KEYLOGGER
   [2019-03-01 23:15:48,018] INFO in manage: SETUP: Created malware type: MALVERTISING
   [2019-03-01 23:15:48,036] INFO in manage: SETUP: Created malware type: RANSOMWARE
   [2019-03-01 23:15:48,053] INFO in manage: SETUP: Created malware type: RAT
   [2019-03-01 23:15:48,071] INFO in manage: SETUP: Created malware type: ROOTKIT
   [2019-03-01 23:15:48,123] INFO in manage: SETUP: Created admin user with password: -7eg"kH20Ug%O{5AZ)p1