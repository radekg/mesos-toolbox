#!/usr/bin/env bash
base="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $base/env-setup.sh

if [ -z "$MESOS_NODE_TYPE" ]; then
  fail_with_message "MESOS_NODE_TYPE has to be overriden, make sure your environment overrides it."
fi

set -e
set -u

## This program needs to be called from either setup-mesos-master.sh or setup-mesos-agent-sh

log "[$APP_LOG_NAME]: Setting up environment..."

sudo tee -a /etc/profile <<EOF
# Mesos:
export MESOS_JAVA_NATIVE_LIBRARY=$MESOS_JAVA_NATIVE_LIBRARY
export MESOS_LOG_DIR=$MESOS_LOG_DIR
EOF

log "[$APP_LOG_NAME]: Mesos directories..."

sudo mkdir -p ${MESOS_LOG_DIR}
sudo mkdir -p ${MESOS_MASTER_WORK_DIR}
sudo mkdir -p ${MESOS_SLAVE_WORK_DIR}

if [ -f /etc/redhat-release ]; then

  log "[$APP_LOG_NAME]: Installing CentOS dependencies..."

  sudo wget http://repos.fedorapeople.org/repos/dchen/apache-maven/epel-apache-maven.repo \
    -O /etc/yum.repos.d/epel-apache-maven.repo
  sudo tee /etc/yum.repos.d/wandisco-svn.repo <<'EOF'
[WANdiscoSVN]
name=WANdisco SVN Repo 1.9
enabled=1
baseurl=http://opensource.wandisco.com/centos/7/svn-1.9/RPMS/$basearch/
gpgcheck=1
gpgkey=http://opensource.wandisco.com/RPM-GPG-KEY-WANdisco
EOF

  sudo yum groupinstall "Development Tools" -y
  install_packages apache-maven python-devel python-boto java-1.8.0-openjdk-devel \
                   zlib-devel libcurl-devel openssl-devel cyrus-sasl-devel \
                   cyrus-sasl-md5 apr-devel subversion-devel apr-util-devel \
                   libevent-devel
fi

if [ -f /etc/lsb-release ]; then

  log "[$APP_LOG_NAME]: Installing Debian dependencies..."
  install_packages autoconf \
                   automake \
                   build-essential \
                   git \
                   python-boto \
                   python-dev \
                   python-software-properties \
                   software-properties-common \
                   libapr1-dev libsvn-dev \
                   libcurl4-openssl-dev \
                   libsasl2-dev \
                   libsasl2-modules \
                   libtool \
                   maven \
                   openjdk-8-jdk \
                   zlib1g \
                   zlib1g-dev \
                   zlibc \
                   libevent-dev

fi

log "[$APP_LOG_NAME]: Installing..."

install_package_from_file $MESOS_PACKAGE_LOCATION

log "[$APP_LOG_NAME]: Cleaning up after default installation..."

sudo rm -rf /etc/mesos/zk
sudo rm -rf /etc/mesos-master
sudo rm -rf /etc/mesos-slave

disable_service mesos-master
disable_service mesos-slave