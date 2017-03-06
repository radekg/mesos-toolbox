#!/usr/bin/env bash
base="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $base/env-setup.sh
set -e
set -u
export APP_LOG_NAME="Marathon"

sudo mkdir -p ${MTHON_CONFIG_DIR}

log "[$APP_LOG_NAME]: Installing Marathon..."

install_package_from_file $MARATHON_PACKAGE_LOCATION

log "[$APP_LOG_NAME]: Creating service definitions..."

sudo tee /usr/sbin/marathon-start.sh <<EOF
#!/bin/bash
/opt/marathon/bin/start \$(/bin/cat ${MTHON_CONFIG_DIR}/${MTHON_CONFIG_FILE})
EOF
sudo chmod +x /usr/sbin/marathon-start.sh
sudo tee /usr/sbin/marathon-post-start.sh <<EOF
#!/bin/bash
consul event -http-addr ${IPV4_PRIVATE}:${CONSUL_PORT_HTTP} -name marathon_svc_event -node ${CONSUL_NODE_NAME} start
EOF
sudo chmod +x /usr/sbin/marathon-post-start.sh
sudo tee /usr/sbin/marathon-post-stop.sh <<EOF
#!/bin/bash
consul event -http-addr ${IPV4_PRIVATE}:${CONSUL_PORT_HTTP} -name marathon_svc_event -node ${CONSUL_NODE_NAME} stop
EOF
sudo chmod +x /usr/sbin/marathon-post-stop.sh

create_service service_name=${SVC_NAME_MARATHON} \
               service_ExecStart="/usr/sbin/marathon-start.sh" \
               service_ExecStartPost="/usr/sbin/marathon-post-start.sh" \
               service_ExecStopPost="/usr/sbin/marathon-post-stop.sh" \
               service_Restart=always \
               service_RestartSec=20

log "[$APP_LOG_NAME]: Enabling service..."

enable_service ${SVC_NAME_MARATHON}

log "[$APP_LOG_NAME]: Registering Consul watch..."

create_consul_watch watch_name="watch-zookeeper-for-${SVC_NAME_ZOOKEEPER}-service" \
                    watch_type=service \
                    watch_service=${SVC_NAME_MESOS_MASTER_ZK} \
                    watch_handler="${base}/consul/marathon-setup-watch.py"

log "[$APP_LOG_NAME]: Reloading Consul..."

reload_consul