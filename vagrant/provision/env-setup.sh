#!/usr/bin/env bash

base="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ -f $base/vars-file ]; then
  source $base/vars-file
  source $VARS_FILE
fi

export PROVISIONING_LOG_FILE=/var/log/provisioning.log

if [ ! -f $PROVISIONING_LOG_FILE ]; then
  # only create the file once, prevent further sudo tty issues
  sudo touch $PROVISIONING_LOG_FILE
  sudo chmod 0666 $PROVISIONING_LOG_FILE
fi

chmod +x $base/consul/*.py

log() {
  local str="[@:`date +%s`]:$1"
  echo -e $str
  echo -e $str >> $PROVISIONING_LOG_FILE
}

##
## SYSTEM DEFAULTS - SERVICE NAMES
##

export SVC_NAME_PREFIX=vagrant-mesos-
export SVC_NAME_CONSUL=${SVC_NAME_PREFIX}consul
export SVC_NAME_DOCKER=${SVC_NAME_PREFIX}docker
export SVC_NAME_MARATHON=${SVC_NAME_PREFIX}marathon
export SVC_NAME_MESOS_MASTER=${SVC_NAME_PREFIX}mesos-master
export SVC_NAME_MESOS_SLAVE=${SVC_NAME_PREFIX}mesos-slave
export SVC_NAME_MESOS_MASTER_ZK=${SVC_NAME_PREFIX}mesos-master-zk
export SVC_NAME_ZOOKEEPER=${SVC_NAME_PREFIX}zookeeper

##
## SYSTEM DEFAULTS - OTHERS
##

export SERVER_INDEX=${SERVER_INDEX-0}
export EXPECTED_CONSENSUS_SERVERS=${EXPECTED_CONSENSUS_SERVERS-3}

##
## CONSUL DEFAULTS
##

export CONSUL_NODE_NAME=${CONSUL_NODE_NAME-undefined_node_name}
export CONSUL_DATACENTER=${CONSUL_DATACENTER-undefined_datacenter}
export CONSUL_VERSION=${CONSUL_VERSION-0.7.5}
export CONSUL_CONFIG_DIR=${CONSUL_CONFIG_DIR-"/etc/consul.d"}
export CONSUL_INSTALL_DIR=${CONSUL_INSTALL_DIR-"/opt/consul"}
export CONSUL_DATA_DIR=${CONSUL_DATA_DIR-"$CONSUL_INSTALL_DIR/data"}
export CONSUL_IS_SERVER=${CONSUL_IS_SERVER-false}
export CONSUL_LOG_LEVEL=${CONSUL_LOG_LEVEL-INFO}
export CONSUL_REJOIN_AFTER_LEAVE=${CONSUL_REJOIN_AFTER_LEAVE-true}
export CONSUL_LEAVE_ON_TERMINATE=${CONSUL_LEAVE_ON_TERMINATE-true}
# Set CONSUL_DNS_IS_ENABLED to false if planning on using mesos-dns
export CONSUL_DNS_IS_ENABLED=${CONSUL_DNS_IS_ENABLED-true}
export CONSUL_HTTPS_IS_ENABLED=${CONSUL_HTTPS_IS_ENABLED-false}
export CONSUL_PORT_SERVER=${CONSUL_PORT_SERVER-8300}
export CONSUL_PORT_SERF_LAN=${CONSUL_PORT_SERF_LAN-8301}
export CONSUL_PORT_SERF_WAN=${CONSUL_PORT_SERF_WAN-8302}
export CONSUL_PORT_RPC=${CONSUL_PORT_HTTP-8400}
export CONSUL_PORT_HTTP=${CONSUL_PORT_HTTP-8500}
export CONSUL_PORT_HTTPS=${CONSUL_PORT_HTTPS-44300}
export CONSUL_PORT_DNS=${CONSUL_PORT_DNS-8600}

##
## MARATHON DEFAULTS
##

# Env variables starting with MARATHON_ are automagically picked up by Marathon
export MTHON_CONFIG_DIR=${MTHON_CONFIG_DIR-"/etc/marathon"}
export MTHON_CONFIG_FILE=${MTHON_CONFIG_FILE-"marathon.conf"}
export MTHON_PORT=${MTHON_PORT-8080}
export MTHON_IS_HA=${MTHON_IS_HA-true}
export MTHON_ZK_PATH=${MTHON_ZK_PATH-"/marathon"}

##
## MESOS DEFAULTS
##

export MESOS_NODE_TYPE=${MESOS_NODE_TYPE-""}
export MESOS_MASTER_PORT=${MESOS_MASTER_PORT-5050}
export MESOS_SLAVE_PORT=${MESOS_SLAVE_PORT-5051}
export MESOS_LOG_DIR=${MESOS_LOG_DIR-"/var/log/mesos"}
export MESOS_MASTER_WORK_DIR=${MESOS_MASTER_WORK_DIR-"/var/lib/mesos-master/workplace"}
export MESOS_SLAVE_WORK_DIR=${MESOS_SLAVE_WORK_DIR-"/var/lib/mesos-slave/workplace"}
export MESOS_ZK_PATH=${MESOS_ZK_PATH-"/mesos"}
export MESOS_JAVA_NATIVE_LIBRARY=${MESOS_JAVA_NATIVE_LIBRARY-/usr/lib/libmesos.so}
export MESOS_LOG_DIR=${MESOS_LOG_DIR-/var/log/mesos}

##
## ZOOKEPER DEFAULTS
##

export ZOOKEEPER_CLIENT_PORT=${ZOOKEEPER_CLIENT_PORT-2181}
export ZOOKEEPER_DATA_DIR=${ZOOKEEPER_DATA_DIR-"/var/lib/zookeeper-local"}
export ZOOKEEPER_LOG_DIR=${ZOOKEEPER_LOG_DIR-"$ZOOKEEPER_DATA_DIR/log"}
export ZOOKEEPER_INSTALL_DIR=${ZOOKEEPER_INSTALL_DIR-"/opt/zookeeper/local"}
export ZOOKEEPER_VERSION=${ZOOKEEPER_VERSION-3.4.9}
export ZOOKEEPER_TICK_TIME=${ZOOKEEPER_TICK_TIME-2000}
export ZOOKEEPER_INIT_LIMIT=${ZOOKEEPER_INIT_LIMIT-5}
export ZOOKEEPER_SYNC_LIMIT=${ZOOKEEPER_SYNC_LIMIT-2}
export ZOOKEEPER_JMX_PORT=${ZOOKEEPER_JMX_PORT-9500}

##
## UTILITY
##

function create_service() {
  set +u

  # capture arguments:
  #local __vs=""; while [[ $# -gt 0 ]]; do local "$1"; __vn="$( cut -d '=' -f 1 <<< "$1" )"; __vs=$__vs,$__vn; shift; done
  while [[ $# -gt 0 ]]; do local "$1"; shift; done
  
  if [ -z ${service_name+x} ]; then
    log "[Service] service_name is missing"
    exit 100
  fi

  local service_file_exists=false
  local service_file=/etc/systemd/system/${service_name}.service
  if [ -f $service_file ]; then
    service_file_exists=true
  fi

  log "[Service] Writing service file $service_file..."
  sudo touch $service_file
  sudo truncate -s 0 $service_file
  
  # https://www.freedesktop.org/software/systemd/man/systemd.unit.html
  echo "[Unit]" | sudo tee --append $service_file
  if [ -n "$service_Description" ]; then
    echo "Description=${service_Description}" | sudo tee --append $service_file
  else
    echo "Description=Service: ${service_name}" | sudo tee --append $service_file
  fi
  if [ -n "$service_Requires" ]; then
    echo "Requires=${service_Requires}" | sudo tee --append $service_file
  else
    echo "Requires=network-online.target" | sudo tee --append $service_file
  fi
  if [ -n "$service_After" ]; then
    echo "After=${service_After}" | sudo tee --append $service_file
  else
    echo "After=network-online.target" | sudo tee --append $service_file
  fi
  echo "" | sudo tee --append $service_file

  # https://www.freedesktop.org/software/systemd/man/systemd.service.html
  echo "[Service]" | sudo tee --append $service_file
  if [ -n "$service_Type" ]; then
    echo "Type=${service_Type}" | sudo tee --append $service_file
  fi
  if [ -n "$service_Environment" ]; then
    echo "Environment=${service_Environment}" | sudo tee --append $service_file
  fi
  if [ -n "$service_RemainAfterExit" ]; then
    echo "RemainAfterExit=${service_RemainAfterExit}" | sudo tee --append $service_file
  fi
  if [ -n "$service_GuessMainPID" ]; then
    echo "GuessMainPID=${service_GuessMainPID}" | sudo tee --append $service_file
  fi
  if [ -n "$service_PIDFile" ]; then
    echo "PIDFile=${service_PIDFile}" | sudo tee --append $service_file
  fi
  if [ -n "$service_BusName" ]; then
    echo "PIDFile=${service_BusName}" | sudo tee --append $service_file
  fi
  if [ -n "$service_ExecStart" ]; then
    echo "ExecStart=${service_ExecStart}" | sudo tee --append $service_file
  fi
  if [ -n "$service_ExecStartPre" ]; then
    echo "ExecStartPre=${service_ExecStartPre}" | sudo tee --append $service_file
  fi
  if [ -n "$service_ExecStartPost" ]; then
    echo "ExecStartPost=${service_ExecStartPost}" | sudo tee --append $service_file
  fi
  if [ -n "$service_ExecReload" ]; then
    echo "ExecReload=${service_ExecReload}" | sudo tee --append $service_file
  fi
  if [ -n "$service_ExecStop" ]; then
    echo "ExecStop=${service_ExecStop}" | sudo tee --append $service_file
  fi
  if [ -n "$service_ExecStopPost" ]; then
    echo "ExecStopPost=${service_ExecStopPost}" | sudo tee --append $service_file
  fi
  if [ -n "$service_RestartSec" ]; then
    echo "RestartSec=${service_RestartSec}" | sudo tee --append $service_file
  fi
  if [ -n "$service_TimeoutStartSec" ]; then
    echo "TimeoutStartSec=${service_TimeoutStartSec}" | sudo tee --append $service_file
  fi
  if [ -n "$service_TimeoutSec" ]; then
    echo "TimeoutSec=${service_TimeoutSec}" | sudo tee --append $service_file
  fi
  if [ -n "$service_RuntimeMaxSec" ]; then
    echo "RuntimeMaxSec=${service_RuntimeMaxSec}" | sudo tee --append $service_file
  fi
  if [ -n "$service_WatchdogSec" ]; then
    echo "WatchdogSec=${service_WatchdogSec}" | sudo tee --append $service_file
  fi
  if [ -n "$service_Restart" ]; then
    echo "Restart=${service_Restart}" | sudo tee --append $service_file
  fi
  if [ -n "$service_StartLimitBurst" ]; then
    echo "StartLimitBurst=${service_StartLimitBurst}" | sudo tee --append $service_file
  fi
  if [ -n "$service_KillSignal" ]; then
    echo "KillSignal=${service_KillSignal}" | sudo tee --append $service_file
  else
    echo "KillSignal=SIGINT" | sudo tee --append $service_file
  fi
  if [ -n "$service_SuccessExitStatus" ]; then
    echo "SuccessExitStatus=${service_SuccessExitStatus}" | sudo tee --append $service_file
  fi
  if [ -n "$service_RestartPreventExitStatus" ]; then
    echo "RestartPreventExitStatus=${service_RestartPreventExitStatus}" | sudo tee --append $service_file
  fi
  if [ -n "$service_RestartForceExitStatus" ]; then
    echo "RestartForceExitStatus=${service_RestartForceExitStatus}" | sudo tee --append $service_file
  fi
  if [ -n "$service_PermissionsStartOnly" ]; then
    echo "PermissionsStartOnly=${service_PermissionsStartOnly}" | sudo tee --append $service_file
  fi
  if [ -n "$service_RootDirectoryStartOnly" ]; then
    echo "RootDirectoryStartOnly=${service_RootDirectoryStartOnly}" | sudo tee --append $service_file
  fi
  if [ -n "$service_NonBlocking" ]; then
    echo "NonBlocking=${service_NonBlocking}" | sudo tee --append $service_file
  fi
  if [ -n "$service_NotifyAccess" ]; then
    echo "NotifyAccess=${service_NotifyAccess}" | sudo tee --append $service_file
  fi
  if [ -n "$service_Sockets" ]; then
    echo "Sockets=${service_Sockets}" | sudo tee --append $service_file
  fi
  if [ -n "$service_FailureAction" ]; then
    echo "FailureAction=${service_FailureAction}" | sudo tee --append $service_file
  fi
  if [ -n "$service_FileDescriptorStoreMax" ]; then
    echo "FileDescriptorStoreMax=${service_FileDescriptorStoreMax}" | sudo tee --append $service_file
  fi
  if [ -n "$service_USBFunctionDescriptors" ]; then
    echo "USBFunctionDescriptors=${service_USBFunctionDescriptors}" | sudo tee --append $service_file
  fi
  if [ -n "$service_USBFunctionStrings" ]; then
    echo "USBFunctionStrings=${service_USBFunctionStrings}" | sudo tee --append $service_file
  fi
  echo "" | sudo tee --append $service_file

  echo "[Install]" | sudo tee --append $service_file
  if [ -n "$service_WantedBy" ]; then
    echo "WantedBy=${service_WantedBy}" | sudo tee --append $service_file
  else
    echo "WantedBy=multi-user.target" | sudo tee --append $service_file
  fi

  if $service_file_exists; then
    log "[Service] ${service_name} already existed. Reloading daemon..."
    sudo systemctl daemon-reload
  fi

  #__vs="${__vs:1:${#__vs}-1}"; OIFS=$IFS; IFS=','; for n in $__vs; do echo "unsetting $n"; unset "$n"; done; IFS=$OIFS
  set -u
}

function create_timer() {
  set +u
  while [[ $# -gt 0 ]]; do local "$1"; shift; done
  if [ -z ${timer_name+x} ]; then
    log "[Timer] timer_name is missing"
    exit 100
  fi
  if [ -z ${timer_executable+x} ]; then
    log "[Timer] timer_executable is missing"
    exit 100
  fi
  if [ -z ${timer_description+x} ]; then
    log "[Timer] timer_description is missing"
    exit 100
  fi
  if [ -z ${timer_OnCalendar+x} ]; then
    log "[Timer] timer_OnCalendar is missing"
    exit 100
  fi
  sudo tee /etc/systemd/system/${timer_name}.service <<EOF
[Unit]
Description=${timer_description}
[Service]
Type=simple
ExecStart=${timer_executable}
EOF
  sudo tee /etc/systemd/system/${timer_name}.timer <<EOF
[Unit]
Description=${timer_description} - timer
[Timer]
OnCalendar=${timer_OnCalendar}
Unit=${timer_name}.service
[Install]
WantedBy=multi-user.target
EOF
  set -u
}

function disable_service() {
  set +u
  log "[Service] Disabling service $1.service"
  sudo systemctl disable $1.service
  set -u
}

function enable_service() {
  if [ -f /etc/systemd/system/$1.service ]; then
    log "[Service] Enabling service $1.service"
    sudo systemctl enable $1.service
  else
    log "[Service] There is no service file for $1.service. Nothing to enable."
  fi
}

function start_service() {
  if [ -f /etc/systemd/system/$1.service ]; then
    enable_service $1
    log "[Service] Starting service $1.service"
    sudo systemctl start $1.service
  else
    log "[Service] There is no service file for $1.service. Nothing to start."
  fi
}

function enable_timer() {
  if [ -f /etc/systemd/system/$1.timer ]; then
    log "[Timer] Enabling timer $1.timer"
    sudo systemctl enable $1.timer
  else
    log "[Timer] There is no timer file for $1.timer. Nothing to enable."
  fi
}
function start_timer() {
  if [ -f /etc/systemd/system/$1.timer ]; then
    enable_timer $1
    log "[Timer] Starting timer $1.timer"
    sudo systemctl start $1.timer
  else
    log "[Timer] There is no timer file for $1.timer. Nothing to enable."
  fi
}

function update_packages() {
  if [ -n "$(which yum)" ]; then
    sudo yum install -y update
  fi
  if [ -n "$(which apt)" ]; then
    sudo apt-get update -y
  fi
}

function install_packages() {
  if [ -n "$(which yum)" ]; then
    sudo yum install -y $@
  fi
  if [ -n "$(which apt)" ]; then
    sudo apt-get install -y $@
  fi
}

function install_package_from_file() {
  if [ -n "$(which rpm)" ]; then
    sudo rpm -i --replacefiles $1
  fi
  if [ -n "$(which dpkg)" ]; then
    sudo dpkg -i $1
  fi
}

function deploy_program() {
  while [[ $# -gt 0 ]]; do local "$1"; shift; done
  if [ -z ${program_name+x} ]; then
    log "[Program] program_name is missing"
    exit 100
  fi
  if [ -z ${program_destination+x} ]; then
    log "[Program] program_destination is missing"
    exit 100
  fi
  local target=$(dirname $program_destination)
  sudo mkdir -p $target
  sudo cp $base/programs/$program_name $program_destination
  sudo chmod +x $program_destination
}

function create_consul_watch() {
  set +u
  local watch_element_name=undefined
  local watch_element_data=undefined
  while [[ $# -gt 0 ]]; do local "$1"; shift; done
  if [ -z ${watch_name+x} ]; then
    log "[Consul Watch] watch_name is missing"
    exit 100
  fi
  if [ -z ${watch_type+x} ]; then
    log "[Consul Watch] watch_type is missing"
    exit 100
  fi
  if [ -z ${watch_handler+x} ]; then
    log "[Consul Watch] watch_handler is missing"
    exit 100
  fi
  if [ "$watch_type" == "service" ]; then
    if [ -z ${watch_service+x} ]; then
      log "[Consul Watch] watch_service is missing"
      exit 100
    fi
    watch_element_name=service
    watch_element_data=$watch_service
  elif [ "$watch_type" == "event" ]; then
    if [ -z ${watch_event+x} ]; then
      log "[Consul Watch] watch_event is missing"
      exit 100
    fi
    watch_element_name=name
    watch_element_data=$watch_event
  fi
  sudo tee ${CONSUL_CONFIG_DIR}/${watch_name}.json <<EOF
{
  "watches": [{
    "type": "${watch_type}",
    "${watch_element_name}": "${watch_element_data}",
    "handler": "${watch_handler}"
  }]
}
EOF
  set -u
}

function create_consul_service() {
  set +u
  while [[ $# -gt 0 ]]; do local "$1"; shift; done
  if [ -z ${service_name+x} ]; then
    log "[Consul Service] service_name is missing"
    exit 100
  fi
  if [ -z ${service_id+x} ]; then
    log "[Consul Service] service_id is missing"
    exit 100
  fi
  if [ -z ${service_address+x} ]; then
    log "[Consul Service] service_address is missing"
    exit 100
  fi
  if [ -z ${service_port+x} ]; then
    log "[Consul Service] service_port is missing"
    exit 100
  fi
  local service_file_name=${service_name}
  if [ -n "${service_file}" ]; then
    service_file_name=$service_file
  fi
  local service_tags_local=""
  if [ -n "${service_tags}" ]; then
    service_tags_local=$service_tags
  fi
  sudo tee ${CONSUL_CONFIG_DIR}/${service_file_name}.json <<EOF
{
  "service": {
    "id": "${service_id}",
    "name": "${service_name}",
    "port": ${service_port},
    "address": "${service_address}",
    "tags": [${service_tags_local}]
  }
}
EOF
  set -u
}

function create_consul_check() {
  set +u
  while [[ $# -gt 0 ]]; do local "$1"; shift; done
  if [ -z ${check_id+x} ]; then
    log "[Consul Check] check_id is missing"
    exit 100
  fi
  if [ -z ${check_name+x} ]; then
    log "[Consul Check] check_name is missing"
    exit 100
  fi
  if [ -z ${check_script+x} ]; then
    log "[Consul Check] check_script is missing"
    exit 100
  fi
  if [ -z ${check_interval+x} ]; then
    log "[Consul Check] check_interval is missing"
    exit 100
  fi
  if [ -z ${check_timeout+x} ]; then
    log "[Consul Check] check_timeout is missing"
    exit 100
  fi
  sudo tee ${CONSUL_CONFIG_DIR}/${check_id}.json <<EOF
{
  "check": {
    "id": "${check_id}",
    "name": "${check_name}",
    "script": "${check_script}",
    "interval": "${check_interval}",
    "timeout": "${check_interval}"
  }
}
EOF
  set -u
}

function install_zookeeper() {
  while [[ $# -gt 0 ]]; do local "$1"; shift; done
  if [ -z ${zk_version+x} ]; then
    log "[Zookeeper installation] zk_version is missing"
    exit 100
  fi
  if [ -z ${zk_install_directory+x} ]; then
    log "[Zookeeper installation] zk_install_directory is missing"
    exit 100
  fi
  if [ -z ${zk_data_directory+x} ]; then
    log "[Zookeeper installation] zk_data_directory is missing"
    exit 100
  fi
  if [ -z ${zk_id+x} ]; then
    log "[Zookeeper installation] zk_id is missing"
    exit 100
  fi
  sudo wget http://apache.lauf-forum.at/zookeeper/zookeeper-${zk_version}/zookeeper-${zk_version}.tar.gz -O /tmp/zookeeper-${zk_version}.tar.gz
  sudo mkdir -p ${zk_install_directory}
  sudo tar -xf /tmp/zookeeper-${zk_version}.tar.gz -C ${zk_install_directory} --strip 1
  sudo rm -rf /tmp/zookeeper-${zk_version}.tar.gz

  sudo mkdir -p ${zk_data_directory}/log
  echo $zk_id | sudo tee ${DATA_DIR}/myid
  sudo chmod -R 0644 ${zk_data_directory}
}

function reload_consul() {
  log "[Consul]: Reloading Consul..."
  sudo systemctl reload ${SVC_NAME_CONSUL}
}

function fail_with_message() {
  log "[Error]: $1"
  exit 1
}

