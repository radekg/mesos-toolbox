#!/usr/bin/env python3

import json, os
from subprocess import PIPE, Popen
from lib.utils import Utils
from lib.deployments import Deployments

LOG = Utils.get_log(__file__)
stdin_lines = Utils.read_stdin()

if len(stdin_lines) == 0:
    LOG.info( 'No data from consul.' )
    exit(0)

base                = os.path.abspath(os.path.dirname(__file__))
complete_input      = "".join( stdin_lines )
parsed_input        = json.loads( complete_input )
service_name        = os.environ['SVC_NAME_MARATHON']

if len(parsed_input) > 0:
  marathon_host = parsed_input[0]['Service']['Address']
  marathon_port = parsed_input[0]['Service']['Port']
  marathon_address = "{}:{}".format(marathon_host, marathon_port)

  try:
    Deployments.chronos(LOG, marathon_address)
  except Exception as ex:
    LOG.error("[Chronos]: Failed to deploy: {}".format(str(ex)))

else:
  LOG.info(" =============> Marathon is not available at the moment.")