import os, sys
from subprocess import PIPE, Popen

class UtilsMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(UtilsMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Utils(object):
    __metaclass__ = UtilsMeta

    @staticmethod
    def env_with_default(varname, default):
        return os.getenv(varname, default)

    @staticmethod
    def cmd(command):
        from config import Config
        log     = None if Config.cmd_log() == None else open(Config.cmd_log(), 'a', 0)
        output  = list()
        process = Popen(args=command, stdout=PIPE, stderr=PIPE, shell=True)
        for line in process.stdout:
            if log != None:
                log.write(line)
            output.append(line)
        process.wait()
        if log != None: log.close()
        return { 'ExitCode': process.returncode, 'StdOut': "".join(output), 'StdErr': process.stderr.read() }

    @staticmethod
    def exit_with_cmd_error(file, error):
        from config import Config
        Config.print_help()
        print >>sys.stderr, "{}: {}".format( os.path.basename(file), error)
        exit(102)

    @staticmethod
    def confirm(message):
        from config import Config
        if Config.args().auto_accept == True:
            return True
        response = raw_input("{}\nAre you sure you want to proceed? (y or yes to continue): ".format( message ))
        if response == "yes" or response == "y":
            return True
        return False

    @staticmethod
    def print_result_error(LOG, message, result):
        LOG.error("{} Exit code {}.".format(message, result['ExitCode']))
        LOG.debug(result['StdOut'])
        LOG.debug(result['StdErr'])

    @staticmethod
    def platform():
        return sys.platform

    @staticmethod
    def list_builds(LOG, directory):
        for name in [ name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name)) ]:
            print name

    @staticmethod
    def list_releases(LOG, repo_dir, master_branch):
        result = Utils.cmd("cd {} && git tag -l".format(repo_dir))
        if result['ExitCode'] == 0:
            releases = result['StdOut'].split("\n")
            releases.append(master_branch)
            return releases
        else:
            Utils.print_result_error(LOG, "Failed listing releases.", result)
            return []

    @staticmethod
    def list_sources(sources_dir, kind):
        path = "{}/{}/".format(sources_dir, kind)
        for name in os.listdir(path):
            full_path  = os.path.join(path, name)
            git_config = "{}/.git/config".format(full_path)
            if os.path.isfile(git_config):
                file = open(git_config, 'r')
                data = Utils.parse_git_config( file.readlines() )
                file.close()
                if 'remote "origin"' in data:
                    if 'url' in data['remote "origin"']:
                        print "{} in directory {}".format(
                            data['remote "origin"']['url'],
                            full_path )

    ##
    ## GIT RELATED OPERATIONS:
    ##

    @staticmethod
    def parse_git_config(lines):
        response = dict()
        last_section = None
        for line in lines:
            line = line.strip()
            if line.startswith("[") and line.endswith("]"):
                last_section = line[1:-1]
                response[ last_section ] = dict()
            else:
                if last_section != None:
                    prop, value = line.split(" = ")
                    response[ last_section ][ prop.strip() ] = value.strip()
        return response

    @staticmethod
    def ensure_sources(LOG, repo_dir, repo_addr):
        if os.path.isdir("{}/.git".format(repo_dir)):
            LOG.info("Updating sources for {}...".format(repo_addr))
            result = Utils.cmd("cd {} && git fetch origin".format(repo_dir))
            if result['ExitCode'] == 0:
                LOG.info("Done.")
                return True
            else:
                Utils.print_result_error(LOG, "Failed.", result)
                return False
        else:
            LOG.info("No sources for {} found. Cloning...".format(repo_addr))
            result = Utils.cmd("cd {} && git clone {} .".format(repo_dir, repo_addr))
            if result['ExitCode'] == 0:
                LOG.info("Done.")
                return True
            else:
                Utils.print_result_error(LOG, "Failed.", result)
                return False

    @staticmethod
    def exit_if_git_release_not_set(LOG, build_dir, release, master_branch, git_repo):
        LOG.info("Ensuring Git version {}...".format(release))
        result = Utils.cmd("sleep 5 && cd {} && git checkout {}".format(build_dir, release))
        if result['ExitCode'] == 0:
            if release == master_branch:
                LOG.info("Updating source code for {}...".format(release))
                result = Utils.cmd("cd {} && git pull origin {}".format(build_dir, release))
                if result['ExitCode'] != 0:
                    Utils.print_result_error( LOG,
                                              "Git version {} could not be updated from {}.".format( release, git_repo ),
                                              result )
                    exit(201)
                else:
                    LOG.info("Done.")
        else:
            Utils.print_result_error(LOG, "Version {} could not be checked out from {}.".format(
                                          release, git_repo ), result )
            exit(202)

    ##
    ## DEPENDENCY CHECKS:
    ##

    @staticmethod
    def is_docker_available():
        # Simply make sure we have docker operational
        # On OSX, when using docker machine, which docker will actually return a path
        # even if docker env is not sourced
        result = Utils.cmd("docker images >/dev/null")
        return result['ExitCode'] == 0

    @staticmethod
    def is_git_available():
        result = Utils.cmd("which git")
        return result['ExitCode'] == 0

    @staticmethod
    def is_brew_available():
        result = Utils.cmd("which brew")
        return result['ExitCode'] == 0

    @staticmethod
    def is_autoconf_available():
        result = Utils.cmd("which autoconf")
        return result['ExitCode'] == 0

    @staticmethod
    def is_automake_available():
        result = Utils.cmd("which automake")
        return result['ExitCode'] == 0

    @staticmethod
    def is_libtool_available():
        result = Utils.cmd("which libtool")
        return result['ExitCode'] == 0

    @staticmethod
    def is_xcode_available():
        result = Utils.cmd("xcode-select -p")
        return result['ExitCode'] == 0

    @staticmethod
    def is_apr_available():
        if Utils.is_brew_available():
            result = Utils.cmd("brew info apr")
            return result['ExitCode'] == 0
        else:
            return False

    @staticmethod
    def is_svn_available():
        result = Utils.cmd("which svn")
        if result['ExitCode'] == 0:
            result = Utils.cmd("svn --version | head -n 1 | awk '{print $3}'")
            return result['StdOut'].startswith("1.9.")
        else:
            return False

    @staticmethod
    def is_java_available():
        result = Utils.cmd("which java")
        if result['ExitCode'] == 0:
            result = Utils.cmd("java -version 2>&1 | head -n 1")
            return "1.8." in result['StdOut']
        else:
            return False

    ##
    ## DOCKER OPERATIONS:
    ##

    @staticmethod
    def is_docker_image(LOG, image_name):
        Utils.exit_if_docker_unavailable(LOG)
        LOG.info("Checking for Docker image...")
        result = Utils.cmd("docker images | grep -w {}".format(image_name))
        return result['StdOut'] != ""

    @staticmethod
    def exit_if_docker_unavailable(LOG):
        if not Utils.is_docker_available():
            Utils.print_result_error(LOG, "Not able to list Docker images. Is Docker installed and running?", result)
            exit(301)

    @staticmethod
    def exit_if_docker_image_not_built(LOG, templates_dir, item, image_name):
        result = Utils.cmd( "cd {}/{} && docker build --no-cache --force-rm=true -t {} .".format( templates_dir, item, image_name ) )
        if result['ExitCode'] != 0:
            Utils.print_result_error(LOG, "Docker image creation failed. Is Docker installed and running?", result)
            exit(302)
