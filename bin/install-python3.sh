#!/usr/bin/env bash

set -e
set -x

echo "Installing python3"
apt-get update && apt-get install -y build-essential checkinstall software-properties-common
apt-get update && apt-get install -y libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev

add-apt-repository -y ppa:ubuntu-toolchain-r/ppa
apt-get update && apt-get install -y python3.6

apt-get update && apt-get install -y python3-pip

echo "Making Python3 and Pip3 defaults"
rm -f /usr/bin/python && ln -s /usr/bin/python3 /usr/bin/python
rm -f /usr/bin/pip && ln -s /usr/bin/pip3 /usr/bin/pip

PYTHON_VERSION=$(python --version 2>&1)
EXPECTED_VERSION="3.6.8"
if [[ $PYTHON_VERSION != *$EXPECTED_VERSION* ]]; then
  echo "Python version $PYTHON_VERSION does not match the $EXPECTED_VERSION"
  exit 1
fi

echo "Python version verified: $EXPECTED_VERSION"
