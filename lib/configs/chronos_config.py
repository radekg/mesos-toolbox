import hashlib, os, sys, time
from lib.utils import Utils

class ChronosConfigMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(ChronosConfigMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class ChronosConfig(object):
    __metaclass__ = ChronosConfigMeta

    @staticmethod
    def setup(program):
        from lib.config import Config

    @staticmethod
    def setup(program):
        from lib.config import Config
        Config.add_argument( "command",
                                help="Command to execute.",
                                metavar="COMMAND",
                                default="",
                                choices=[ "build",
                                          "show-releases", "show-builds", "show-sources",
                                          "remove-build","remove-sources",
                                          "check-this-system" ] )
        Config.add_argument( "--chronos-version",
                                dest="chronos_version",
                                help="Chronos version to build.",
                                metavar="CHRONOS_VERSION",
                                default=Utils.env_with_default("CHRONOS_VERSION","") )
        Config.add_argument( "--chronos-master-branch",
                                dest="chronos_master_branch",
                                help="Chronos master branch name.",
                                metavar="CHRONOS_MASTER_BRANCH_NAME",
                                default=Utils.env_with_default("CHRONOS_MASTER_BRANCH_NAME","master") )
        Config.add_argument( "--chronos-git-repository",
                                dest="chronos_git_repository",
                                help="Chronos git repository to use.",
                                metavar="CHRONOS_GIT_REPOSITORY",
                                default=Utils.env_with_default("CHRONOS_GIT_REPOSITORY", "https://github.com/mesos/chronos.git") )
        Config.add_argument( "--docker-templates",
                                dest="docker_templates_dir",
                                help="Docker templates base directory.",
                                metavar="DOCKER_TEMPLATES_DIR",
                                default=Utils.env_with_default("DOCKER_TEMPLATES_DIR", "{}/docker/chronos".format(
                                    os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                                )))
        Config.add_argument( "--source-dir",
                                dest="source_dir",
                                help="Directory in which the Chronos sources are stored.",
                                metavar="SOURCE_DIR",
                                default=Utils.env_with_default("SOURCE_DIR", os.path.expanduser("~/.mesos-toolbox/chronos/sources") ) )
        Config.add_argument( "--packages-dir",
                                dest="packages_dir",
                                help="Directory in which packaged versions of Chronos are stored.",
                                metavar="PACKAGES_DIR",
                                default=Utils.env_with_default("PACKAGES_DIR", os.path.expanduser("~/.mesos-toolbox/chronos/packages") ) )
        Config.add_argument( "--work-dir",
                                dest="work_dir",
                                help="Directory in which this program does the work.",
                                metavar="WORK_DIR",
                                default=Utils.env_with_default("WORK_DIR", os.path.expanduser("~/.mesos-toolbox/chronos/temp") ) )
        Config.add_argument( "--m2-dir",
                                dest="m2_dir",
                                help="Maven dependencies directory.",
                                metavar="MVN_DIR",
                                default=Utils.env_with_default("MVN_DIR", os.path.expanduser("~/.mesos-toolbox/.m2/chronos") ) )
        Config.add_argument( "--with-tests",
                                dest="with_tests",
                                help="Run unit tests when building Chronos.",
                                action="store_true" )

        return Config.ready(program)

    @staticmethod
    def command():
        from lib.config import Config
        return Config.args().command

    @staticmethod
    def chronos_version():
        from lib.config import Config
        return Config.args().chronos_version

    @staticmethod
    def chronos_master_branch():
        from lib.config import Config
        return Config.args().chronos_master_branch

    @staticmethod
    def chronos_git_repository():
        from lib.config import Config
        return Config.args().chronos_git_repository

    @staticmethod
    def source_dir():
        from lib.config import Config
        Utils.cmd("mkdir -p {}".format(Config.args().source_dir))
        return Config.args().source_dir

    @staticmethod
    def docker_templates_dir():
        from lib.config import Config
        return Config.args().docker_templates_dir

    @staticmethod
    def packages_dir():
        from lib.config import Config
        path = "{}/".format(Config.args().packages_dir)
        Utils.cmd("mkdir -p {}".format(path))
        return path

    @staticmethod
    def work_dir():
        from lib.config import Config
        Utils.cmd("mkdir -p {}".format(Config.args().work_dir))
        return Config.args().work_dir

    @staticmethod
    def m2_dir():
        from lib.config import Config
        Utils.cmd("mkdir -p {}".format(Config.args().m2_dir))
        return Config.args().m2_dir

    @staticmethod
    def with_tests():
        from lib.config import Config
        return "true" if Config.args().with_tests == True else "false"

    ##
    ## ADDITIONAL OPERATIONS:
    ##

    @staticmethod
    def chronos_git_repository_md5():
        h = hashlib.md5()
        h.update(ChronosConfig.chronos_git_repository())
        return h.hexdigest()

    @staticmethod
    def chronos_repository_dir():
        from lib.config import Config
        path = "{}/chronos/{}".format( Config.args().source_dir, ChronosConfig.chronos_git_repository_md5() )
        Utils.cmd("mkdir -p {}".format(path))
        return path
