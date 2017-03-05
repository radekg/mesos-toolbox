#!/usr/bin/env python

import json, os, re, select, sys
from subprocess import PIPE, Popen
from lib.utils import Utils

LOG = Utils.get_log(__file__)
stdin_lines = Utils.read_stdin()

if len(stdin_lines) == 0:
    LOG.info( 'No data from consul.' )
    exit(0)

base                       = os.path.abspath(os.path.dirname(__file__))
expected_consensus_servers = os.environ['EXPECTED_CONSENSUS_SERVERS']
service_name               = os.environ['SVC_NAME_ZOOKEEPER']
client_port                = os.environ['ZOOKEEPER_CLIENT_PORT']
install_dir                = os.environ['ZOOKEEPER_INSTALL_DIR']
data_dir                   = os.environ['ZOOKEEPER_DATA_DIR']
log_dir                    = os.environ['ZOOKEEPER_LOG_DIR']
server_index               = os.environ['SERVER_INDEX']

##
## LOCAL
##

config_path    = "{}/conf/zoo.cfg".format( install_dir )
myid_path      = "{}/myid".format( data_dir )
complete_input = "".join( stdin_lines )
parsed_input   = json.loads( complete_input )

if os.path.exists( config_path ):
    exit(0)

if str(len(parsed_input)) == expected_consensus_servers:

    LOG.info( 'Required number of {} {} services is available. Configuring Zookeeper...'.format(len(parsed_input), service_name) )
    config = list()
    config.append("tickTime={}".format( os.environ['ZOOKEEPER_TICK_TIME'] ))
    config.append("dataDir={}".format( data_dir ))
    config.append("clientPort={}".format( client_port ))
    config.append("initLimit={}".format( os.environ['ZOOKEEPER_INIT_LIMIT'] ))
    config.append("syncLimit={}".format( os.environ['ZOOKEEPER_SYNC_LIMIT'] ))
    for service_def in parsed_input:
        config.append("{}={}:2888:3888".format( re.sub(r"(.*)(\.\d)", r"server\2", service_def['Service']['ID']), service_def['Service']['Address'] ))

    ##
    ## PROGRAM CONFIGURATION AND SERVICE START:
    ##

    config_data = "\n".join( config )
    LOG.info( "Zookeeper config is: \n{}".format(config_data) )
    Utils.write_text( config_data, config_path )
    Utils.write_text( str(int(server_index)+1), myid_path )
    LOG.info( 'Config written to: {}'.format( config_path ) )
    LOG.info( 'myid   written to: {}'.format( myid_path ) )
    LOG.info( 'Starting {}...'.format( service_name ) )

    start_status = Utils.start_service( service_name )
    if not start_status['Success']:
        LOG.error( "Starting {} failed with exit code {}.".format( service_name, start_status['ExitCode'] ) )
        exit(101)

    ##
    ## DONE:
    ##

    LOG.info( 'Yay - DONE \o/.' )

else:
    LOG.warn( 'Not enough {} services: {} vs expected {}.'.format(
                                  service_name,
                                  len(parsed_input),
                                  expected_consensus_servers ) )
