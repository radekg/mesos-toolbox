#!/usr/bin/env bash

set -e
set -u

base="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $base/env-setup.sh

mkdir -p /tmp/install-consul && cd /tmp/install-consul
sudo mkdir -p ${CONSUL_INSTALL_DIR}/data

log "[Consul]: Downloading ${CONSUL_VERSION}..."
CONSUL_ARCHIVE=consul_${CONSUL_VERSION}_linux_amd64.zip
wget https://releases.hashicorp.com/consul/${CONSUL_VERSION}/${CONSUL_ARCHIVE}
log "[Consul]: Installing ${CONSUL_VERSION}..."
unzip ${CONSUL_ARCHIVE} >/dev/null
chmod +x consul
sudo mv consul ${CONSUL_INSTALL_DIR}/consul
sudo ln -s ${CONSUL_INSTALL_DIR}/consul /usr/bin/consul

log "[Consul]: Setting up the service..."
create_service service_name=${SVC_NAME_CONSUL} \
               service_Description="Consul agent" \
               service_Environment="GOMAXPROCS=2" \
               service_Restart=on-failure \
               service_ExecStart="/usr/bin/consul agent -ui -config-dir=${CONSUL_CONFIG_DIR}" \
               service_ExecReload="/bin/kill -HUP \$MAINPID"

log "[Consul]: Setting up configuration..."

sudo mkdir -p ${CONSUL_CONFIG_DIR}

if [ $CONSUL_DNS_IS_ENABLED = false ]; then
  export CONSUL_DNS_PORT=-1
fi
if [ $CONSUL_HTTPS_IS_ENABLED = false ]; then
  export CONSUL_PORT_HTTPS=-1
fi

if [ "$CONSUL_PRIMARY_SERVER" = "$IPV4_PRIVATE" ]; then
  log "[Consul]: Generating Bootstrap Server configuration..."
  sudo tee ${CONSUL_CONFIG_DIR}/consul.json <<EOF
{
  "node_name": "${CONSUL_NODE_NAME}",
  "rejoin_after_leave": ${CONSUL_REJOIN_AFTER_LEAVE},
  "datacenter": "${CONSUL_DATACENTER}",
  "log_level": "${CONSUL_LOG_LEVEL}",
  "data_dir": "${CONSUL_DATA_DIR}",
  "server": ${CONSUL_IS_SERVER},
  "bootstrap_expect": 1,
  "retry_join": [
    "${CONSUL_PRIMARY_SERVER}"
  ],
  "addresses": {
    "dns": "127.0.0.1",
    "http": "${IPV4_PRIVATE}",
    "https": "${IPV4_PRIVATE}",
    "rpc": "127.0.0.1"
  },
  "ports": {
    "server": ${CONSUL_PORT_SERVER},
    "serf_lan": ${CONSUL_PORT_SERF_LAN},
    "serf_wan": ${CONSUL_PORT_SERF_WAN},
    "rpc": ${CONSUL_PORT_RPC},
    "http": ${CONSUL_PORT_HTTP},
    "https": ${CONSUL_PORT_HTTPS},
    "dns": ${CONSUL_PORT_DNS}
  },
  "bind_addr": "${IPV4_PRIVATE}",
  "client_addr": "${IPV4_PRIVATE}",
  "leave_on_terminate": ${CONSUL_LEAVE_ON_TERMINATE}
}
EOF
else
  log "[Consul]: Generating Client configuration..."
  sudo tee ${CONSUL_CONFIG_DIR}/consul.json <<EOF
{
  "node_name": "${CONSUL_NODE_NAME}",
  "rejoin_after_leave": ${CONSUL_REJOIN_AFTER_LEAVE},
  "datacenter": "${CONSUL_DATACENTER}",
  "log_level": "${CONSUL_LOG_LEVEL}",
  "data_dir": "${CONSUL_DATA_DIR}",
  "server": ${CONSUL_IS_SERVER},
  "retry_join": [
    "${CONSUL_PRIMARY_SERVER}"
  ],
  "addresses": {
    "dns": "127.0.0.1",
    "http": "${IPV4_PRIVATE}",
    "https": "${IPV4_PRIVATE}",
    "rpc": "127.0.0.1"
  },
  "ports": {
    "server": ${CONSUL_PORT_SERVER},
    "serf_lan": ${CONSUL_PORT_SERF_LAN},
    "serf_wan": ${CONSUL_PORT_SERF_WAN},
    "rpc": ${CONSUL_PORT_RPC},
    "http": ${CONSUL_PORT_HTTP},
    "https": ${CONSUL_PORT_HTTPS},
    "dns": ${CONSUL_PORT_DNS}
  },
  "bind_addr": "${IPV4_PRIVATE}",
  "client_addr": "${IPV4_PRIVATE}",
  "leave_on_terminate": ${CONSUL_LEAVE_ON_TERMINATE}
}
EOF
fi

log "[Consul]: Enabling and starting..."
start_service ${SVC_NAME_CONSUL}

log "[Consul]: Running."
