FROM pypy:3

RUN apt-get update && apt-get install -y mysql-client

WORKDIR /usr/src/app

COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

COPY ./entrypoint.sh /usr/src/app/entrypoint.sh
COPY . /usr/src/app

CMD ["/usr/src/app/entrypoint.sh"]
