FROM ubuntu:14.04.5

RUN apt-get update
RUN apt-get -y install software-properties-common
RUN add-apt-repository ppa:jonathonf/python-3.6
RUN apt-get update
RUN apt-get install -y python3.6 python3.6-dev
RUN apt-get install -y build-essential python3-pip
RUN apt-get install -y libpq-dev python3-psycopg2
RUN apt-get install -y libssl-dev libffi-dev

ENV PYTHONUNBUFFERED 1

RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

ADD . /code
WORKDIR /code

RUN pip3 install -U pip setuptools
RUN pip3 install -r requirements/dev.txt
