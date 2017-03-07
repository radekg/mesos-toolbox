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

log "[$APP_LOG_NAME]: Installing..."

install_package_from_file $MESOS_PACKAGE_LOCATION

log "[$APP_LOG_NAME]: Cleaning up after default installation..."

sudo rm -rf /etc/mesos/zk
sudo rm -rf /etc/mesos-master
sudo rm -rf /etc/mesos-slave

disable_service mesos-master
disable_service mesos-slave