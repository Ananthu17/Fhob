FROM python:3.8.11-alpine

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt

# Install postgres client
RUN apk add --update --no-cache postgresql-client

# Install individual dependencies
# so that we could avoid installing extra packages to the container
RUN apk add --update --no-cache --virtual .tmp-build-deps \
	gcc libc-dev linux-headers postgresql-dev

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

RUN apk --update add gfortran py-pip build-base wget freetype-dev \
    libpng-dev openblas-dev g++ cmake make mupdf-dev jbig2dec jbig2dec-dev \
    openjpeg-dev libxml2-dev libxslt-dev harfbuzz-dev && pip3 install --upgrade pip

RUN pip3 install -r /requirements.txt

# Remove dependencies
RUN apk del .tmp-build-deps

RUN mkdir /film_hobo
WORKDIR /film_hobo
COPY ./film_hobo /film_hobo

# [Security] Limit the scope of user who run the docker image
RUN adduser -D user

USER user
