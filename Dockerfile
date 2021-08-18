# pull official base image
FROM python:3.8.3-alpine

# set work directory
WORKDIR /usr/src/film_hobo

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev libffi-dev openssl-dev cargo

# install cryptography dependencies
RUN apk add --no-cache \
        libressl-dev \
        musl-dev \
        libffi-dev && \
    pip install --no-cache-dir cryptography==2.1.4 && \
    apk del \
        libressl-dev \
        musl-dev \
        libffi-dev

# install other dependencies
RUN apk --update add \
    build-base \
    jpeg-dev \
    zlib-dev

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy entrypoint.sh
COPY ./film_hobo/entrypoint.sh .

# copy project
COPY . .

# run entrypoint.sh
ENTRYPOINT ["/usr/src/film_hobo/film_hobo/entrypoint.sh"]
