FROM ubuntu:14.04.5

RUN apt-get update
RUN apt-get -y install software-properties-common
RUN add-apt-repository ppa:jonathonf/python-3.5
RUN apt-get update
RUN apt-get install -y python3.5 python3.5-dev
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

RUN rm -f /usr/bin/python3 && ln -s /usr/bin/python3.5 /usr/bin/python3
RUN rm -f /usr/bin/python3-config && ln -s /usr/bin/python3.5-config /usr/bin/python3-config
RUN rm -f /usr/bin/python3m && ln -s /usr/bin/python3.5m /usr/bin/python3m
RUN rm -f /usr/bin/python3m-config && ln -s /usr/bin/python3.5m-config /usr/bin/python3m-config

RUN pip3 install -U pip setuptools
RUN pip3 install -r requirements/dev.txt
