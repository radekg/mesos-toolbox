#!/usr/bin/env bash
base="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $base/env-setup.sh

set -e
set -u

APP_LOG_NAME="Docker"

log "[$APP_LOG_NAME]: Adding docker repository key..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

log "[$APP_LOG_NAME]: Adding docker repository..."
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

log "[$APP_LOG_NAME]: Updating packages..."
update_packages

if [ -z "$(which docker)" ]; then
  log "[$APP_LOG_NAME]: Installing docker..."
  install_packages docker-ce
  log "[$APP_LOG_NAME]: Docker $(docker -v) installed..."
else
  log "[$APP_LOG_NAME]: Docker $(docker -v) already installed..."
fi

log "[$APP_LOG_NAME]: Setting up the service..."
create_service service_name=${SVC_NAME_DOCKER} \
               service_Description=${APP_LOG_NAME} \
               service_Restart=on-failure \
               service_ExecStart="/usr/bin/docker daemon --storage-driver=overlay -H fd://"

log "[$APP_LOG_NAME]: Enabling the service..."
enable_service ${SVC_NAME_DOCKER}

log "[$APP_LOG_NAME]: Done."