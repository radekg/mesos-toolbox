#!/usr/bin/env bash
base="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $base/env-setup.sh
set -e
set -u
export APP_LOG_NAME="Mesos agent"
$base/setup-mesos-shared.sh

log "[$APP_LOG_NAME]: Changing default service definitions..."

sudo tee /usr/sbin/start-${SVC_NAME_MESOS_SLAVE}.sh <<EOF
#!/bin/bash
/usr/sbin/mesos-slave \$(/bin/cat /etc/mesos/slave.conf)
EOF
sudo chmod +x /usr/sbin/start-${SVC_NAME_MESOS_SLAVE}.sh

create_service service_name=${SVC_NAME_MESOS_SLAVE} \
               service_ExecStart=/usr/sbin/start-${SVC_NAME_MESOS_SLAVE}.sh \
               service_Restart=always \
               service_RestartSec=20
enable_service ${SVC_NAME_MESOS_SLAVE}

log "[$APP_LOG_NAME]: Registering Consul watch..."

create_consul_watch watch_name="watch-zookeeper-for-${SVC_NAME_MESOS_SLAVE}-service" \
                    watch_type=service \
                    watch_service=${SVC_NAME_ZOOKEEPER} \
                    watch_handler="${base}/consul/mesos-setup-watch.py"

log "[$APP_LOG_NAME]: Done."
log "[$APP_LOG_NAME]: The service will be started by mesos-setup-watch.py."