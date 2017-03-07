import hashlib, os, sys, time
from lib.utils import Utils
from lib.configs.defaults import Defaults

class VagrantConfigMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(VagrantConfigMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class VagrantConfig(object):
    __metaclass__ = VagrantConfigMeta

    @staticmethod
    def setup(program):
        from lib.config import Config
        Config.add_argument( "command",
                                help="Command to execute.",
                                metavar="COMMAND",
                                default="",
                                choices=[ "destroy-f", "halt", "provision",
                                          "resume", "ssh", "status", "suspend", "up",
                                          "check-this-system" ] )
        Config.add_argument( "--mesos-build",
                                dest="mesos_build",
                                help="Mesos build to use for Vagrant cluster.",
                                metavar="MESOS_BUILD",
                                default=Utils.env_with_default("MESOS_BUILD","") )
        Config.add_argument( "--marathon-build",
                                dest="marathon_build",
                                help="Marathon build to use for Vagrant cluster.",
                                metavar="MARATHON_BUILD",
                                default=Utils.env_with_default("MARATHON_BUILD","") )
        Config.add_argument( "--mesos-packages-dir",
                                dest="mesos_packages_dir",
                                help="Directory in which packaged versions of Mesos are stored.",
                                metavar="MESOS_PACKAGES_DIR",
                                default=Utils.env_with_default("MESOS_PACKAGES_DIR", Defaults.mesos_packages_dir() ) )
        Config.add_argument( "--marathon-packages-dir",
                                dest="marathon_packages_dir",
                                help="Directory in which packaged versions of Mesos are stored.",
                                metavar="MARATHON_PACKAGES_DIR",
                                default=Utils.env_with_default("MARATHON_PACKAGES_DIR", Defaults.marathon_packages_dir() ) )
        Config.add_argument( "--os",
                                dest="operating_system",
                                help="Operating system to build mesos for.",
                                metavar="OPERATING_SYSTEM",
                                default=Utils.env_with_default("OPERATING_SYSTEM","") )
        Config.add_argument( "--docker-templates",
                                dest="docker_templates_dir",
                                help="Docker templates base directory.",
                                metavar="DOCKER_TEMPLATES_DIR",
                                default=Utils.env_with_default("DOCKER_TEMPLATES_DIR", "{}/docker/mesos".format(
                                    os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                                )))
        Config.add_argument( "--machine",
                                dest="machine",
                                help="Optional machine for the Vagrant command.",
                                metavar="MACHINE",
                                default=Utils.env_with_default("MACHINE","") )
        Config.add_argument( "--deployment-name",
                                dest="deployment_name",
                                help="Deployment name.",
                                metavar="DEPLOYMENT_NAME",
                                default=Utils.env_with_default("DEPLOYMENT_NAME","vagrant") )
        Config.add_argument( "--master-ips",
                                dest="master_ips",
                                help="Master IP addresses. Comma delimited list of addresses to give to masters.",
                                metavar="MASTER_IP",
                                default=Utils.env_with_default("MASTER_IP","192.168.33.100") )
        Config.add_argument( "--agent-ips",
                                dest="agent_ips",
                                help="Agent IP addresses. Comma delimited list of addresses to give to agents.",
                                metavar="AGENT_IPS",
                                default=Utils.env_with_default("AGENT_IPS","192.168.33.101,192.168.33.102") )
        Config.add_argument( "--master-memory",
                                dest="master_memory",
                                help="Master RAM amount.",
                                metavar="MASTER_MEMORY",
                                default=Utils.env_with_default("MASTER_MEMORY","1024") )
        Config.add_argument( "--agent-memory",
                                dest="agent_memory",
                                help="Agent RAM amount.",
                                metavar="AGENT_MEMORY",
                                default=Utils.env_with_default("AGENT_MEMORY","2048") )
        return Config.ready(program)

    @staticmethod
    def command():
        from lib.config import Config
        return Config.args().command

    @staticmethod
    def mesos_build():
        from lib.config import Config
        return Config.args().mesos_build

    @staticmethod
    def mesos_packages_dir():
        from lib.config import Config
        path = "{}/".format(Config.args().mesos_packages_dir)
        Utils.cmd("mkdir -p {}".format(path))
        return path

    @staticmethod
    def marathon_build():
        from lib.config import Config
        return Config.args().marathon_build

    @staticmethod
    def marathon_packages_dir():
        from lib.config import Config
        path = "{}/".format(Config.args().marathon_packages_dir)
        Utils.cmd("mkdir -p {}".format(path))
        return path

    @staticmethod
    def operating_system():
        from lib.config import Config
        return Config.args().operating_system

    @staticmethod
    def docker_templates_dir():
        from lib.config import Config
        return Config.args().docker_templates_dir

    @staticmethod
    def machine():
        from lib.config import Config
        return Config.args().machine

    @staticmethod
    def deployment_name():
        from lib.config import Config
        return Config.args().deployment_name

    @staticmethod
    def master_ips():
        from lib.config import Config
        return Config.args().master_ips

    @staticmethod
    def agent_ips():
        from lib.config import Config
        return Config.args().agent_ips

    @staticmethod
    def master_memory():
        from lib.config import Config
        return Config.args().master_memory

    @staticmethod
    def agent_memory():
        from lib.config import Config
        return Config.args().agent_memory

    @staticmethod
    def supported_operating_systems():
        from lib.config import Config
        return Utils.list_supported_operating_systems(Config.args().docker_templates_dir)
