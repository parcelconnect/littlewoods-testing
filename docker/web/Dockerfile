FROM heroku/heroku:18

SHELL ["/bin/bash", "-c"]

ENV DEBIAN_FRONTEND=noninteractive

RUN mkdir /tmp/bin
COPY ./bin /tmp/bin

RUN apt-get update && apt-get install -y build-essential libpq-dev
RUN /tmp/bin/install-python3.sh

ENV PYTHONUNBUFFERED 1

RUN apt-get install -y python3.7-venv && python -m venv /mnt/venv
ENV PATH /mnt/venv/bin/:${PATH}

RUN mkdir /code
WORKDIR /code

RUN pip install -q -U pip setuptools
RUN mkdir /tmp/requirements
COPY ./requirements /tmp/requirements
RUN python -m pip install --no-cache-dir -q -r /tmp/requirements/dev.txt

COPY . /code/
