#!/usr/bin/env python3

import json, os
from subprocess import PIPE, Popen
from lib.utils import Utils

LOG = Utils.get_log(__file__)
stdin_lines = Utils.read_stdin()

if len(stdin_lines) == 0:
    LOG.info( 'No data from consul.' )
    exit(0)

base                = os.path.abspath(os.path.dirname(__file__))
complete_input      = "".join( stdin_lines )
parsed_input        = json.loads( complete_input )
config_path         = "{}/{}".format( os.environ['MTHON_CONFIG_DIR'], os.environ['MTHON_CONFIG_FILE'] )
service_name        = os.environ['SVC_NAME_MARATHON']
consul_service_path = "{}/service-{}.json".format( os.environ['CONSUL_CONFIG_DIR'], service_name )

if os.path.exists( config_path ):
    exit(0)

# This watch is triggered only when mesos-master is up
# which means we have all required zookeepers

mesos_zk_path    = parsed_input[0]['Service']['Address']
marathon_zk_path = parsed_input[0]['Service']['Address'].replace( os.environ['MESOS_ZK_PATH'], os.environ['MTHON_ZK_PATH'] )

config = list()
config.append("--http_port {}".format( os.environ['MTHON_PORT'] ) )
if os.environ['MTHON_IS_HA'] == "true":
    config.append("--ha")
config.append("--master {}".format( mesos_zk_path ) )
config.append("--zk {}".format( marathon_zk_path ) )

##
## PROGRAM CONFIGURATION AND SERVICE START:
##

config_data = "\n".join( config )
LOG.info( "Marathon config is: \n{}".format(config_data) )
Utils.write_text(config_data, config_path)
LOG.info( 'Config written to: {}'.format( config_path ) )
LOG.info( 'Starting Marathon' )

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
    "port": int( os.environ['MTHON_PORT'] ),
    "address": os.environ['IPV4_PRIVATE']
} }
Utils.write_json( consul_service, consul_service_path )
LOG.info( 'Consul service written to: {}'.format( consul_service_path ) )
Utils.reload_consul(LOG)

##
## DONE:
##

LOG.info( 'Yay - DONE \o/.' )
