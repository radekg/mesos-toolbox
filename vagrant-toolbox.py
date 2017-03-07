#!/usr/bin/python
import os, signal, sys, time
from lib.config import Config
from lib.configs.vagrant_config import VagrantConfig
from lib.utils import Utils

LOG = VagrantConfig.setup(__file__)

def validate_input():
    mesos_build = VagrantConfig.mesos_build()
    marathon_build = VagrantConfig.marathon_build()
    operating_system = VagrantConfig.operating_system()

    if operating_system not in VagrantConfig.supported_operating_systems():
        Utils.exit_with_cmd_error( __file__,
                                   "Operating system ({}) is not supported. Available values: {}".format(
                                    operating_system,
                                    str(VagrantConfig.supported_operating_systems()) ))
    
    if mesos_build == "":
        Utils.exit_with_cmd_error( __file__, "Mesos build version not given. Run mesos-toolbox show-builds to see what the available builds are.")
    if marathon_build == "":
        Utils.exit_with_cmd_error( __file__, "Marathon build version not given. Run marathon-toolbox show-builds to see what the available builds are.")
    mesos_build_name = "{}-{}".format(VagrantConfig.mesos_build(), VagrantConfig.operating_system().replace(":", "-"))
    if mesos_build_name not in Utils.list_builds("{}/mesos".format(VagrantConfig.mesos_packages_dir())):
        Utils.exit_with_cmd_error( __file__, "Mesos build {} does not exist. Please build that version first with mesos-toolbox.".format(mesos_build_name))
    if VagrantConfig.marathon_build() not in Utils.list_builds(VagrantConfig.marathon_packages_dir()):
        Utils.exit_with_cmd_error( __file__, "Marathon build {} does not exist. Please build that version first with mesos-toolbox.".format(VagrantConfig.marathon_build()))
    exit(100)

def signal_handler(signal, frame):
    if Utils.has_processes_running():
        Utils.stop_processes()

def get_exports_from_config():
    exports = dict()
    exports['DEPLOYMENT_NAME'] = VagrantConfig.deployment_name()
    exports['MASTER_IP'] = VagrantConfig.master_ip()
    agent_ips = VagrantConfig.agent_ips().split(",")
    idx = 1
    for agent_ip in agent_ips:
        exports["AGENT{}_IP".format(idx)] = agent_ip
        idx = idx + 1
    exports['MASTER_MEMORY'] = VagrantConfig.master_memory()
    exports['AGENT_MEMORY'] = VagrantConfig.agent_memory()
    exports['TARGET_OS'] = VagrantConfig.operating_system()
    exports['MESOS_VERSION'] = VagrantConfig.mesos_build()
    exports['MARATHON_VERSION'] = VagrantConfig.marathon_build().replace("v", "", 1)
    exports['MESOS_BUILD_DIR'] = "{}/mesos/{}-{}".format(VagrantConfig.mesos_packages_dir(),
                                                         VagrantConfig.mesos_build(),
                                                         VagrantConfig.operating_system().replace(":", "-"))
    exports['MARATHON_BUILD_DIR'] = "{}/{}".format(VagrantConfig.marathon_packages_dir(),
                                                   VagrantConfig.marathon_build())
    print(str(exports))
    exit(100)
    return exports

def vagrant_command(cmd):
    validate_input()
    signal.signal(signal.SIGINT, signal_handler)
    base = os.path.dirname(os.path.abspath(__file__))

    command = "cd {}/vagrant".format(base)
    exports = get_exports_from_config()
    for key, value in exports.iteritems():
        command = "{}; export {}={}".format(command, key, value)
    command = "{}; vagrant {}".format(command, cmd)
    if VagrantConfig.machine() != "":
        command = "{} {}".format(command, VagrantConfig.machine())
    result = Utils.cmd(command, True)
    if result['ExitCode'] != 0:
        Utils.print_result_error(LOG, "Vagrant command execution has failed.", result)

## ----------------------------------------------------------------------------------------------
## OPERATIONS:
## ----------------------------------------------------------------------------------------------

def op_destroy():   vagrant_command("destroy -f")
def op_halt():      vagrant_command("halt")
def op_provision(): vagrant_command("provision")
def op_resume():    vagrant_command("resume")
def op_ssh():       vagrant_command("ssh")
def op_status():    vagrant_command("status")
def op_suspend():   vagrant_command("suspend")
def op_up():        vagrant_command("up")

def op_check_this_system():
    LOG.info("Checking dependencies:")
    LOG.info(" -> Vagrant? : {}".format( "Yes" if Utils.is_vagrant_available() else "No" ))

if __name__ == "__main__":

    if "destroy-f" == VagrantConfig.command(): op_destroy()
    if "halt" == VagrantConfig.command(): op_halt()
    if "provision" == VagrantConfig.command(): op_provision()
    if "resume" == VagrantConfig.command(): op_resume()
    if "ssh" == VagrantConfig.command(): op_ssh()
    if "status" == VagrantConfig.command(): op_status()
    if "suspend" == VagrantConfig.command(): op_suspend()
    if "up" == VagrantConfig.command(): op_up()
    if "check-this-system" == VagrantConfig.command(): op_check_this_system()