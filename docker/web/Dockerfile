FROM heroku/heroku:16

RUN apt-get update && apt-get install -y python3-pip
RUN apt-get autoclean && rm -rf /var/lib/apt/lists/*

RUN mkdir /code
WORKDIR /code

RUN pip3 install -q -U pip setuptools
RUN mkdir /tmp/requirements
COPY ./requirements /tmp/requirements
RUN pip3 install --no-cache-dir -q -r /tmp/requirements/dev.txt

COPY . /code/
