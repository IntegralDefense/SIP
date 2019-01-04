FROM python:3.7-alpine

RUN apk update && \
	apk add --virtual build-deps gcc python-dev musl-dev && \
	apk add postgresql-dev && \
	apk add netcat-openbsd

WORKDIR /usr/src/app

COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

COPY ./entrypoint.sh /usr/src/app/entrypoint.sh
COPY . /usr/src/app

CMD ["/usr/src/app/entrypoint.sh"]
