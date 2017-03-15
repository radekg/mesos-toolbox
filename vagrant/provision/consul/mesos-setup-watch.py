#!/usr/bin/env python3

import json, os
from subprocess import PIPE, Popen
from lib.utils import Utils

LOG = Utils.get_log(__file__)
stdin_lines = Utils.read_stdin()

if len(stdin_lines) == 0:
    LOG.info( 'No data from consul.' )
    exit(0)

base                   = os.path.abspath(os.path.dirname(__file__))
complete_input         = "".join( stdin_lines )
parsed_input           = json.loads( complete_input )
config_path            = "/etc/mesos/{}.conf".format( os.environ['MESOS_NODE_TYPE'] )
service_name           = ( os.environ['SVC_NAME_MESOS_MASTER'] if os.environ['MESOS_NODE_TYPE'] == "master" else os.environ['SVC_NAME_MESOS_SLAVE'] )
service_name_zk        = os.environ['SVC_NAME_ZOOKEEPER']
service_name_master_zk = os.environ['SVC_NAME_MESOS_MASTER_ZK']
consul_service_path    = "{}/service-{}.json".format( os.environ['CONSUL_CONFIG_DIR'],
                                                      service_name )
consul_service_zk_path = "{}/service-{}.json".format( os.environ['CONSUL_CONFIG_DIR'],
                                                      service_name_master_zk )

if os.path.exists( config_path ):
    exit(0)

if len(parsed_input) == int(os.environ['EXPECTED_CONSENSUS_SERVERS']):

    LOG.info( 'Required number of {} {} services is available. Configuring Mesos...'.format(len(parsed_input), service_name_zk) )
    zk_addresses = list()
    for service_def in parsed_input:
        zk_addresses.append("{}:{}".format( service_def['Service']['Address'], service_def['Service']['Port'] ))
    zk_str = ",".join( zk_addresses )
    LOG.info( 'Zookeepers: {}'.format( zk_str ) )

    config = list()
    if os.environ['MESOS_NODE_TYPE'] == 'master':
        if os.environ['MESOS_HOSTNAME'] != "":
            config.append("--hostname={}".format(os.environ['MESOS_HOSTNAME']) )
        config.append("--log_dir={}".format( os.environ['MESOS_LOG_DIR'] ) )
        config.append("--ip={}".format( os.environ['IPV4_PRIVATE'] ) )
        config.append("--port={}".format( os.environ['MESOS_MASTER_PORT'] ) )
        config.append("--work_dir={}".format( os.environ['MESOS_MASTER_WORK_DIR'] ) )
        config.append("--zk=zk://{}{}".format( zk_str, os.environ['MESOS_ZK_PATH'] ) )
        config.append("--cluster={}".format( os.environ['CONSUL_DATACENTER'] ) )
        config.append("--registry=in_memory" )
    elif os.environ['MESOS_NODE_TYPE'] == 'slave':
        if os.environ['MESOS_HOSTNAME'] != "":
            config.append("--hostname={}".format(os.environ['MESOS_HOSTNAME']) )
        config.append("--log_dir={}".format( os.environ['MESOS_LOG_DIR'] ) )
        config.append("--ip={}".format( os.environ['IPV4_PRIVATE'] ) )
        config.append("--port={}".format( os.environ['MESOS_SLAVE_PORT'] ) )
        config.append("--work_dir={}".format( os.environ['MESOS_SLAVE_WORK_DIR'] ) )
        config.append("--master=zk://{}{}".format( zk_str, os.environ['MESOS_ZK_PATH'] ) )
        config.append("--containerizers=docker,mesos" )
        config.append("--executor_registration_timeout=5mins" )
    else:
        LOG.error( 'Unknown Mesos node type: {}'.format( os.environ['MESOS_NODE_TYPE'] ) )

    if len( config ) > 0:

        ##
        ## PROGRAM CONFIGURATION AND SERVICE START:
        ##

        config_data = "\n".join( config )
        LOG.info( "Mesos {} config is: \n{}".format(os.environ['MESOS_NODE_TYPE'], config_data) )
        Utils.write_text(config_data, config_path)
        LOG.info( 'Config written to: {}'.format( config_path ) )
        LOG.info( 'Starting Mesos {}...'.format( os.environ['MESOS_NODE_TYPE'] ) )
        
        start_status = Utils.start_service( service_name )
        if not start_status['Success']:
            LOG.error( "Starting {} failed with exit code {}.".format( service_name, start_status['ExitCode'] ) )
            exit(101)
        
        ##
        ## CONSUL SERVICES:
        ##

        consul_service = { "service": {
            "id": "{}-{}".format( service_name, os.environ['SERVER_INDEX'] ),
            "name": service_name,
            "port": int( os.environ['MESOS_{}_PORT'.format( os.environ['MESOS_NODE_TYPE'].upper() )] ),
            "address": os.environ['IPV4_PRIVATE']
        } }
        
        consul_service_zk = { "service": {
            "id": service_name_master_zk,
            "name": service_name_master_zk,
            "port": 0,
            "address": "zk://{}{}".format( zk_str, os.environ['MESOS_ZK_PATH'] )
        } }

        Utils.write_json(consul_service, consul_service_path)
        Utils.write_json(consul_service_zk, consul_service_zk_path)
        LOG.info( 'Consul service written to: {}'.format( consul_service_path ) )
        LOG.info( 'Consul Mesos master zookeeper service written to: {}'.format( consul_service_zk_path ) )
        Utils.reload_consul(LOG)

        ##
        ## DONE:
        ##

        LOG.info( 'Yay - DONE \o/.' )
    else:
        LOG.error( 'No config to write.' )
        exit(102)
        
else:
    LOG.warn( 'Not enough {} services: {} vs expected {}.'.format(
                             service_name_zk,
                             len(parsed_input),
                             os.environ['EXPECTED_CONSENSUS_SERVERS'] ) )
