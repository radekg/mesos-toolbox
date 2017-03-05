#!/usr/bin/env bash

base="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
chmod +x $base/*.sh
source $base/env-setup.sh

set -e
set -u

update_packages
install_packages autoconf \
  automake \
  build-essential \
  git \
  libapr1-dev libsvn-dev \
  libcurl4-openssl-dev \
  libsasl2-dev \
  libsasl2-modules \
  libtool \
  maven \
  openjdk-8-jdk \
  python-boto \
  python-dev \
  python-software-properties \
  software-properties-common \
  libevent-dev \
  ruby \
  ruby-dev \
  zlib1g \
  zlib1g-dev \
  zlibc