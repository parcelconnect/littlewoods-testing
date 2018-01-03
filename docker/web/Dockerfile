FROM heroku/heroku:16

RUN apt-get update
RUN apt-get install -y python3-pip

RUN mkdir /code
WORKDIR /code

RUN pip3 install -U pip setuptools
RUN mkdir /tmp/requirements
COPY ./requirements /tmp/requirements
RUN pip3 install --no-cache-dir -r /tmp/requirements/dev.txt

COPY . /code/
