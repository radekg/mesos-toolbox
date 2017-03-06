#!/usr/bin/env bash
base="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $base/env-setup.sh
set -e
set -u
export APP_LOG_NAME="Mesos master"
$base/setup-mesos-shared.sh

log "[$APP_LOG_NAME]: Changing default service definitions..."

sudo tee /usr/sbin/start-${SVC_NAME_MESOS_MASTER}.sh <<EOF
#!/bin/bash
/usr/sbin/mesos-master \$(/bin/cat /etc/mesos/master.conf)
EOF
sudo chmod +x /usr/sbin/start-${SVC_NAME_MESOS_MASTER}.sh

create_service service_name=${SVC_NAME_MESOS_MASTER} \
               service_ExecStart=/usr/sbin/start-${SVC_NAME_MESOS_MASTER}.sh \
               service_Restart=always \
               service_RestartSec=20
enable_service ${SVC_NAME_MESOS_MASTER}

log "[$APP_LOG_NAME]: Registering Consul watch..."

create_consul_watch watch_name="watch-zookeeper-for-${SVC_NAME_MESOS_MASTER}-service" \
                    watch_type=service \
                    watch_service=${SVC_NAME_ZOOKEEPER} \
                    watch_handler="${base}/consul/mesos-setup-watch.py"

log "[$APP_LOG_NAME]: Done."
log "[$APP_LOG_NAME]: The service will be started by mesos-setup-watch.py."