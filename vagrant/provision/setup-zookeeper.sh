#!/usr/bin/env bash

base="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $base/env-setup.sh

set -e
set -u

APP_LOG_NAME="ZooKeeper"
INSTALL_DIR=$ZOOKEEPER_INSTALL_DIR
DATA_DIR=$ZOOKEEPER_DATA_DIR
LOG_DIR=$ZOOKEEPER_LOG_DIR
SVC_NAME=$SVC_NAME_ZOOKEEPER
CLIENT_PORT=$ZOOKEEPER_CLIENT_PORT
ZK_SERVER_ID=$(($SERVER_INDEX + 1))

if [ -f /etc/redhat-release ]; then
  log "[$APP_LOG_NAME]: Installing CentOS dependencies..."
  install_packages java-1.8.0-openjdk-devel
fi
if [ -f /etc/lsb-release ]; then
  log "[$APP_LOG_NAME]: Installing Debian dependencies..."
  install_packages openjdk-8-jdk
fi

log "[$APP_LOG_NAME]: Downloading ${ZOOKEEPER_VERSION}..."
install_zookeeper zk_version=${ZOOKEEPER_VERSION} \
                  zk_install_directory=${INSTALL_DIR} \
                  zk_data_directory=${DATA_DIR} \
                  zk_id=${ZK_SERVER_ID}

log "[$APP_LOG_NAME]: Setting up the service..."
create_service service_name=${SVC_NAME} \
               service_Description=${APP_LOG_NAME} \
               service_Type=forking \
               service_Restart=on-failure \
               service_Environment="ZOO_LOG_DIR=${LOG_DIR} JMXPORT=${ZOOKEEPER_JMX_PORT}" \
               service_ExecStart="${INSTALL_DIR}/bin/zkServer.sh start" \
               service_ExecStop="${INSTALL_DIR}/bin/zkServer.sh stop"

log "[$APP_LOG_NAME]: Enabling the service..."
enable_service ${SVC_NAME}

log "[$APP_LOG_NAME]: Setting up Consul service..."
create_consul_service service_name=${SVC_NAME} \
                      service_id=zookeeper.${ZK_SERVER_ID} \
                      service_address=${IPV4_PRIVATE} \
                      service_port=${CLIENT_PORT}

log "[$APP_LOG_NAME]: Setting up Consul watch..."
create_consul_watch watch_name=watch-${SVC_NAME}-service \
                    watch_type=service \
                    watch_service=${SVC_NAME} \
                    watch_handler=${base}/consul/watch-zookeeper.py

reload_consul

log "[$APP_LOG_NAME]: Done."
log "[$APP_LOG_NAME]: The service will be started by the watch."
