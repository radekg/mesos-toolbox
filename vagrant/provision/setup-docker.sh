#!/usr/bin/env bash
base="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $base/env-setup.sh

set -e
set -u

APP_LOG_NAME="Docker"

log "[$APP_LOG_NAME]: Adding docker repository..."
if [ -f /etc/lsb-release ]; then
  
  install_packages python-dev \
                   python-software-properties \
                   software-properties-common

  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
  sudo add-apt-repository \
     "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
     $(lsb_release -cs) \
     stable"

fi

if [ -f /etc/redhat-release ]; then

  install_packages yum-utils
  sudo yum-config-manager \
    --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo
  sudo yum-config-manager --enable docker-ce-edge
  sudo yum makecache fast
  
fi

log "[$APP_LOG_NAME]: Updating packages..."
update_packages

if [ -z "$(which docker)" ]; then
  log "[$APP_LOG_NAME]: Installing docker..."
  install_packages docker-ce
  log "[$APP_LOG_NAME]: Docker $(docker -v) installed..."
else
  log "[$APP_LOG_NAME]: Docker $(docker -v) already installed..."
fi

log "[$APP_LOG_NAME]: Using Docker provided service definition..."
sudo systemctl start docker

log "[$APP_LOG_NAME]: Done."