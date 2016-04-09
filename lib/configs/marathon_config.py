import hashlib, os, sys, time
from lib.utils import Utils

class MarathonConfigMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MarathonConfigMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class MarathonConfig(object):
    __metaclass__ = MarathonConfigMeta

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
        Config.add_argument( "--marathon-version",
                                dest="marathon_version",
                                help="Marathon version to build.",
                                metavar="MARATHON_VERSION",
                                default=Utils.env_with_default("MARATHON_VERSION","") )
        Config.add_argument( "--marathon-master-branch",
                                dest="marathon_master_branch",
                                help="Marathon master branch name.",
                                metavar="MARATHON_MASTER_BRANCH_NAME",
                                default=Utils.env_with_default("MARATHON_MASTER_BRANCH_NAME","master") )
        Config.add_argument( "--marathon-git-repository",
                                dest="marathon_git_repository",
                                help="Marathon git repository to use.",
                                metavar="MARATHON_GIT_REPOSITORY",
                                default=Utils.env_with_default("MARATHON_GIT_REPOSITORY", "https://github.com/mesosphere/marathon.git") )
        Config.add_argument( "--docker-templates",
                                dest="docker_templates_dir",
                                help="Docker templates base directory.",
                                metavar="DOCKER_TEMPLATES_DIR",
                                default=Utils.env_with_default("DOCKER_TEMPLATES_DIR", "{}/docker/marathon".format(
                                    os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                                )))
        Config.add_argument( "--source-dir",
                                dest="source_dir",
                                help="Directory in which the Marathon sources are stored.",
                                metavar="SOURCE_DIR",
                                default=Utils.env_with_default("SOURCE_DIR", os.path.expanduser("~/.mesos-toolbox/marathon/sources") ) )
        Config.add_argument( "--packages-dir",
                                dest="packages_dir",
                                help="Directory in which packaged versions of Mesos are stored.",
                                metavar="PACKAGES_DIR",
                                default=Utils.env_with_default("PACKAGES_DIR", os.path.expanduser("~/.mesos-toolbox/marathon/packages") ) )
        Config.add_argument( "--work-dir",
                                dest="work_dir",
                                help="Directory in which this program does the work.",
                                metavar="WORK_DIR",
                                default=Utils.env_with_default("WORK_DIR", os.path.expanduser("~/.mesos-toolbox/marathon/temp") ) )
        Config.add_argument( "--ivy2-dir",
                                dest="ivy2_dir",
                                help="Ivy2 dependencies directory.",
                                metavar="IVY2_DIR",
                                default=Utils.env_with_default("IVY2_DIR", os.path.expanduser("~/.mesos-toolbox/.ivy2/marathon") ) )
        Config.add_argument( "--with-tests",
                                dest="with_tests",
                                help="Run unit tests when building Marathon.",
                                action="store_true" )
        Config.add_argument( "--no-haproxy-marathon-bridge",
                                dest="no_haproxy_marathon_bridge",
                                help="Do not package haproxy-marathon-bridge when packaging Marathon.",
                                action="store_false" )

        return Config.ready(program)

    @staticmethod
    def command():
        from lib.config import Config
        return Config.args().command

    @staticmethod
    def marathon_version():
        from lib.config import Config
        return Config.args().marathon_version

    @staticmethod
    def marathon_master_branch():
        from lib.config import Config
        return Config.args().marathon_master_branch

    @staticmethod
    def marathon_git_repository():
        from lib.config import Config
        return Config.args().marathon_git_repository

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
    def ivy2_dir():
        from lib.config import Config
        Utils.cmd("mkdir -p {}".format(Config.args().ivy2_dir))
        return Config.args().ivy2_dir

    @staticmethod
    def with_tests():
        from lib.config import Config
        return "true" if Config.args().with_tests == True else "false"

    @staticmethod
    def no_haproxy_marathon_bridge():
        from lib.config import Config
        return "true" if Config.args().no_haproxy_marathon_bridge == True else "false"

    ##
    ## ADDITIONAL OPERATIONS:
    ##

    @staticmethod
    def marathon_git_repository_md5():
        h = hashlib.md5()
        h.update(MarathonConfig.marathon_git_repository())
        return h.hexdigest()

    @staticmethod
    def marathon_repository_dir():
        from lib.config import Config
        path = "{}/marathon/{}".format( Config.args().source_dir, MarathonConfig.marathon_git_repository_md5() )
        Utils.cmd("mkdir -p {}".format(path))
        return path
