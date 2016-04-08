import hashlib, os, sys, time
from lib.utils import Utils

class MesosConfigMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MesosConfigMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class MesosConfig(object):
    __metaclass__ = MesosConfigMeta

    @staticmethod
    def setup(program):
        from lib.config import Config
        Config.add_argument( "command",
                                help="Command to execute.",
                                metavar="COMMAND",
                                default="",
                                choices=[ "build", "docker",
                                          "show-releases", "show-builds", "show-mesos-sources", "show-packaging-sources",
                                          "remove-build","remove-mesos-sources", "remove-packaging-sources",
                                          "check-this-system" ] )
        Config.add_argument( "--mesos-version",
                                dest="mesos_version",
                                help="Mesos version to build.",
                                metavar="MESOS_VERSION",
                                default=Utils.env_with_default("MESOS_VERSION","") )
        Config.add_argument( "--mesos-master-branch",
                                dest="mesos_master_branch",
                                help="Mesos master branch name.",
                                metavar="MESOS_MASTER_BRANCH_NAME",
                                default=Utils.env_with_default("MESOS_MASTER_BRANCH_NAME","master") )
        Config.add_argument( "--os",
                                dest="operating_system",
                                help="Operating system to build mesos for.",
                                metavar="OPERATING_SYSTEM",
                                default=Utils.env_with_default("OPERATING_SYSTEM","") )
        Config.add_argument( "--mesos-deb-packaging",
                                dest="deb_packaging_repository",
                                help="mesos-deb-packaging git repository to use.",
                                metavar="MESOS_DEB_PACKAGING_REPOSITORY",
                                default=Utils.env_with_default("MESOS_DEB_PACKAGING_REPOSITORY", "https://github.com/mesosphere/mesos-deb-packaging.git") )
        Config.add_argument( "--mesos-deb-packaging-sha",
                                dest="deb_packaging_sha",
                                help="mesos-deb-packaging sha to use.",
                                metavar="MESOS_DEB_PACKAGING_SHA",
                                default=Utils.env_with_default("MESOS_DEB_PACKAGING_SHA", "50fa9d1ed11edc7f4c78c79e4a06bdafe46ad397") )
        Config.add_argument( "--mesos-git-repository",
                                dest="mesos_git_repository",
                                help="Mesos git repository to use.",
                                metavar="MESOS_GIT_REPOSITORY",
                                default=Utils.env_with_default("MESOS_GIT_REPOSITORY", "https://github.com/apache/mesos.git") )
        Config.add_argument( "--mesos-build-version",
                                dest="mesos_build_version",
                                help="Mesos build version.",
                                metavar="MESOS_BUILD_VERSION",
                                default=Utils.env_with_default("MESOS_BUILD_VERSION", "0.1.{}".format( str(int(time.time())) ) ) )
        Config.add_argument( "--docker-templates",
                                dest="docker_templates_dir",
                                help="Docker templates base directory.",
                                metavar="DOCKER_TEMPLATES_DIR",
                                default=Utils.env_with_default("DOCKER_TEMPLATES_DIR", "{}/docker/mesos".format(
                                    os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                                )))
        Config.add_argument( "--packaging-patches",
                                dest="packages_patches_dir",
                                help="mesos-deb-packaging patches directory.",
                                metavar="PACKAGES_PATCHES_DIR",
                                default=Utils.env_with_default("PACKAGES_PATCHES_DIR", "{}/patches/mesos-packaging".format(
                                    os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                                )))
        Config.add_argument( "--source-dir",
                                dest="source_dir",
                                help="Directory in which the Mesos sources are stored.",
                                metavar="SOURCE_DIR",
                                default=Utils.env_with_default("SOURCE_DIR", os.path.expanduser("~/.mesos-toolbox/mesos/sources") ) )
        Config.add_argument( "--packages-dir",
                                dest="packages_dir",
                                help="Directory in which packaged versions of Mesos are stored.",
                                metavar="PACKAGES_DIR",
                                default=Utils.env_with_default("PACKAGES_DIR", os.path.expanduser("~/.mesos-toolbox/mesos/packages") ) )
        Config.add_argument( "--work-dir",
                                dest="work_dir",
                                help="Directory in which this program does the work.",
                                metavar="WORK_DIR",
                                default=Utils.env_with_default("WORK_DIR", os.path.expanduser("~/.mesos-toolbox/mesos/temp") ) )

        return Config.ready(program)

    @staticmethod
    def command():
        from lib.config import Config
        return Config.args().command

    @staticmethod
    def mesos_version():
        from lib.config import Config
        return Config.args().mesos_version

    @staticmethod
    def mesos_master_branch():
        from lib.config import Config
        return Config.args().mesos_master_branch

    @staticmethod
    def operating_system():
        from lib.config import Config
        return Config.args().operating_system

    @staticmethod
    def deb_packaging_repository():
        from lib.config import Config
        return Config.args().deb_packaging_repository

    @staticmethod
    def deb_packaging_sha():
        from lib.config import Config
        return Config.args().deb_packaging_sha

    @staticmethod
    def mesos_git_repository():
        from lib.config import Config
        return Config.args().mesos_git_repository

    @staticmethod
    def mesos_build_version():
        from lib.config import Config
        return Config.args().mesos_build_version

    @staticmethod
    def docker_templates_dir():
        from lib.config import Config
        return Config.args().docker_templates_dir

    @staticmethod
    def packages_patches_dir():
        from lib.config import Config
        return Config.args().packages_patches_dir

    @staticmethod
    def source_dir():
        from lib.config import Config
        Utils.cmd("mkdir -p {}".format(Config.args().source_dir))
        return Config.args().source_dir

    @staticmethod
    def packages_dir():
        from lib.config import Config
        path = "{}/mesos".format(Config.args().packages_dir)
        Utils.cmd("mkdir -p {}".format(path))
        return path

    @staticmethod
    def work_dir():
        from lib.config import Config
        Utils.cmd("mkdir -p {}".format(Config.args().work_dir))
        return Config.args().work_dir

    ##
    ## ADDITIONAL OPERATIONS:
    ##

    @staticmethod
    def mesos_git_repository_md5():
        h = hashlib.md5()
        h.update(MesosConfig.mesos_git_repository())
        return h.hexdigest()

    @staticmethod
    def deb_packaging_repository_md5():
        h = hashlib.md5()
        h.update(MesosConfig.deb_packaging_repository())
        return h.hexdigest()

    @staticmethod
    def mesos_repository_dir():
        from lib.config import Config
        path = "{}/mesos/{}".format( Config.args().source_dir, MesosConfig.mesos_git_repository_md5() )
        Utils.cmd("mkdir -p {}".format(path))
        return path

    @staticmethod
    def deb_packaging_repository_dir():
        from lib.config import Config
        path = "{}/mesos-packaging/{}".format( Config.args().source_dir, MesosConfig.deb_packaging_repository_md5() )
        Utils.cmd("mkdir -p {}".format(path))
        return path

    @staticmethod
    def supported_operating_systems():
        from lib.config import Config
        return [ name for name in os.listdir( Config.args().docker_templates_dir ) ] + ( ["osx"] if sys.platform == "darwin" else [] )