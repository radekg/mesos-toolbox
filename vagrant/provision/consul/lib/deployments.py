import json, os, time
from lib.utils import Utils

class DeploymentsMeta(type):
  _instances = {}
  def __call__(cls, *args, **kwargs):
    if cls not in cls._instances:
      cls._instances[cls] = super(DeploymentsMeta, cls).__call__(*args, **kwargs)
    return cls._instances[cls]

class Deployments(object):
  __metaclass__ = DeploymentsMeta

  @staticmethod
  def chronos(LOG, marathon_address, max_tries=10, try_interval=10):

    mesos_zk_address = None
    zk_hosts = None

    LOG.info("[Chronos]: Attempting deployment...")

    result = Utils.consul_service_data(os.environ['SVC_NAME_MESOS_MASTER_ZK'])
    if result['ExitCode'] == 0:
      consul_data = json.loads(result['StdOut'])
      mesos_zk_address = consul_data[0]['ServiceAddress']
    else:
      LOG.error("[Chronos]: Expected {} service in Consul catalog but found none.".format(os.environ['SVC_NAME_MESOS_MASTER_ZK']))

    result = Utils.consul_service_data(os.environ['SVC_NAME_ZOOKEEPER'])
    if result['ExitCode'] == 0:
      consul_data = json.loads(result['StdOut'])
      if str(len(consul_data)) == os.environ['EXPECTED_CONSENSUS_SERVERS']:
        zk_hosts = ",".join([ "{}:{}".format(x['ServiceAddress'], x['ServicePort']) for x in consul_data ])
      else:
        LOG.error("[Chronos]: Expected {} consensus servers but got {}.".format(os.environ['EXPECTED_CONSENSUS_SERVERS'], str(len(consul_data))))
    else:
      LOG.error("[Chronos]: Expected {} service in Consul catalog but found none.".format(os.environ['SVC_NAME_ZOOKEEPER']))

    if mesos_zk_address != None and zk_hosts != None:
      current_attempt = 1
      while current_attempt <= max_tries:
        LOG.info("[Chronos]: Deploying with ZK hosts: {} and Mesos ZK address {}. Attempt {} of {}...".format(
          zk_hosts,
          mesos_zk_address,
          current_attempt,
          max_tries))
        marathon_app_definition = json.dumps({
          "id": "/chronos",
          "cpus": 0.1,
          "instances": 1,
          "mem": 256,
          "args": [
            "--zk_hosts", zk_hosts,
            "--master", mesos_zk_address
          ],
          "portDefinitions": [{
            "name": "http-api",
            "protocol": "tcp"
          },{
            "name": "libprocess",
            "protocol": "tcp"
          }],
          "container": {
            "type": "DOCKER",
            "docker": {
              "image": "mesosphere/chronos:v3.0.2",
              "network": "HOST",
              "forcePullImage": False
            }
          }
        })
        result = Utils.deploy_marathon_app(marathon_address, marathon_app_definition)
        if result['ExitCode'] == 0:
          LOG.info("[Chronos]: Deployed.")
          break
        else:
          LOG.error("[Chronos]: Failed to deploy at attempt {}. Reason: {}".format(current_attempt, result['StdErr']))
          current_attempt = current_attempt + 1
          time.sleep(try_interval)

    else:
      LOG.error("[Chronos]: Service dependencies not loaded from Consul.")