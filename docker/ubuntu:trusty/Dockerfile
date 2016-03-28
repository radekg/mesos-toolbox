FROM ubuntu:trusty

RUN apt-get update -y \
  && apt-get -y install git-core software-properties-common python-software-properties \
  && add-apt-repository ppa:openjdk-r/ppa \
  && apt-get update -y \
  && apt-get -y install ruby1.9.1 ruby1.9.1-dev \
                        build-essential libxslt-dev libxml2-dev \
                        wget zlibc zlib1g zlib1g-dev \
                       curl autoconf libtool python-dev python-boto \
                       libcurl4-openssl-dev libsasl2-dev maven libapr1-dev libsvn-dev \
  && apt-get install -y openjdk-8-jdk \
  && gem install fpm --no-ri --no-rdoc

ENV JAVA_HOME /usr/lib/jvm/java-1.8.0-openjdk-amd64