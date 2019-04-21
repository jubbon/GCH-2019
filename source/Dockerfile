FROM python:3.7.2

RUN apt-get update

RUN pip install --upgrade pip

WORKDIR /usr/src/packages

ENV PYTHONPATH /usr/src/packages

COPY ./packages .
