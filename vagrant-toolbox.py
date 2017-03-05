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
    if mesos_build == "":
        Utils.exit_with_cmd_error( __file__, "Mesos build version not given. Run mesos-toolbox show-builds to see what the available builds are.")
    if marathon_build == "":
        Utils.exit_with_cmd_error( __file__, "Marathon build version not given. Run marathon-toolbox show-builds to see what the available builds are.")

def signal_handler(signal, frame):
    if Utils.has_processes_running():
        Utils.stop_processes()

def vagrant_command(cmd):
    validate_input()
    signal.signal(signal.SIGINT, signal_handler)
    base = os.path.dirname(os.path.abspath(__file__))
    command = "cd {}/vagrant && vagrant {}".format(base, cmd)
    if VagrantConfig.machine() != "":
        command = "{} {}".format(command, VagrantConfig.machine())
    command = "{} 2>&1".format(command)
    status = Utils.cmd(command, True)

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