#!/usr/bin/python
import os, re, time
from lib.config import Config
from lib.configs.marathon_config import MarathonConfig
from lib.utils import Utils

LOG = MarathonConfig.setup(__file__)

def validate_input():
    marathon_version = MarathonConfig.marathon_version()
    if marathon_version == "":
        Utils.exit_with_cmd_error( __file__, "Marathon version not given. Run with show-releases to see what the available versions are.")
    if not marathon_version in list_releases():
        Utils.exit_with_cmd_error( __file__,
                                   "Marathon version ({}) is not supported. Run with show-releases to see what the available versions are.".format(
                                    marathon_version ))

def list_releases():
    return Utils.list_releases(LOG, MarathonConfig.marathon_repository_dir(), MarathonConfig.marathon_master_branch())

def op_build():
    if Utils.ensure_sources(LOG, MarathonConfig.marathon_repository_dir(), MarathonConfig.marathon_git_repository()):
        validate_input()
        image_name = "marathon-docker-build"
        if not Utils.is_docker_image(LOG, image_name):
            LOG.info("Docker image not found. Building...")
            Utils.exit_if_docker_image_not_built( LOG,
                                                  MarathonConfig.docker_templates_dir(),
                                                  "default",
                                                  image_name )

        build_dir    = "{}/{}".format( MarathonConfig.work_dir(),
                               MarathonConfig.marathon_version() )
        packages_dir = "{}/{}".format( MarathonConfig.packages_dir(),
                               MarathonConfig.marathon_version() )

        if os.path.exists(packages_dir):
            if not Utils.confirm("Marathon build for {} already exists. To rebuild, continue.".format(
                    MarathonConfig.marathon_version() )):
                exit(0)

        build_log_file = "{}.{}.log".format(build_dir, str(int(time.time())))
        LOG.info("Recording build process to {}.".format(build_log_file))
        Config.set_cmd_log(build_log_file)

        # cleanup old data:
        Utils.cmd("rm -rf {}".format(packages_dir))
        Utils.cmd("rm -rf {}".format(build_dir))

        # copy sources
        LOG.info("Fetching Marathon {} sources...".format(MarathonConfig.marathon_git_repository()))
        Utils.cmd("cp -R {} {}".format( MarathonConfig.marathon_repository_dir(), build_dir ))

        # ensure branch / tag
        Utils.exit_if_git_release_not_set( LOG, build_dir,
                                           MarathonConfig.marathon_version(),
                                           MarathonConfig.marathon_master_branch(),
                                           MarathonConfig.marathon_git_repository() )

        marathon_sbt_version = None
        raw_sbt_file_content = None
        if os.path.exists("{}/version.sbt".format( build_dir )):
            with open("{}/version.sbt".format( build_dir ), 'r') as sbt_file:
                raw_sbt_file_content = sbt_file.read().replace('\n', '')
                match_obj = re.match(r'.*"(.*)".*', raw_sbt_file_content)
                if match_obj:
                    marathon_sbt_version = match_obj.group(1)
        else:
            LOG.error("No version.sbt file for Marathon {}. Can't continue.".format( MarathonConfig.marathon_version() ))
            exit(110)

        if marathon_sbt_version == None:
            LOG.error("Version could not be reliably established from the version.sbt file. Raw content: {}. Can't continue.".format( raw_sbt_file_content ))
            exit(111)

        LOG.info("Marathon version from SBT: {}".format( marathon_sbt_version ))

        # TODO: Actual build
        build_command = "docker run -ti -v {}:/output -v {}:/marathon-src -v {}:/root/.ivy2 -e \"BUILD_MARATHON_VERSION={}\" -e \"FPM_OUTPUT_VERSION={}\" -e \"ASSEMBLY_WITH_TESTS={}\" {} /bin/bash -c 'cd /marathon-build && ./marathon-build.sh; exit $?'".format(
                                    os.path.dirname(packages_dir),
                                    build_dir,
                                    MarathonConfig.ivy2_dir(),
                                    MarathonConfig.marathon_version(),
                                    marathon_sbt_version,
                                    MarathonConfig.with_tests(),
                                    image_name )
        
        Utils.cmd("echo '{}'".format(build_command.replace("'", "\\'")))
        LOG.info("Building Marathon {}. This will take a while...".format(MarathonConfig.marathon_version()))
        build_start_time = int(time.time())
        build_status = Utils.cmd(build_command)
        build_end_time = int(time.time())
        if build_status['ExitCode'] == 0:
            LOG.info( "Marathon {} built successfully. Build took {} seconds. Output available in {}. Cleaning up...".format(
                      MarathonConfig.marathon_version(),
                      str( build_end_time - build_start_time ),
                      packages_dir ))
            Utils.cmd("rm -rf {}".format(build_dir))
        else:
            LOG.error( "Marathon build failed. Leaving build log and temp directory for inspection. marathon={}".format( build_dir ) )
            exit(107)

def op_show_releases():
    if Utils.ensure_sources(LOG, MarathonConfig.marathon_repository_dir(), MarathonConfig.marathon_git_repository()):
        LOG.info("Releases:")
        for line in list_releases():
            if line != "":
                print line

def op_remove_build():
    validate_input()
    if not Utils.confirm("You are about to remove Marathon build for {}.".format( MarathonConfig.marathon_version() )):
        exit(0)
    Utils.cmd("rm -rf {}/{}".format( MarathonConfig.packages_dir(),
                                     MarathonConfig.marathon_version()))

def op_remove_sources():
    if not Utils.confirm("You are about to remove Marathon sources for {}.".format( MarathonConfig.marathon_git_repository() )):
        exit(0)
    Utils.cmd("rm -rf {}".format( MarathonConfig.marathon_repository_dir() ))

if __name__ == "__main__":

    if "build" == MarathonConfig.command(): op_build()
    if "show-releases" == MarathonConfig.command(): op_show_releases()
    if "show-builds" == MarathonConfig.command(): Utils.list_builds( LOG, MarathonConfig.packages_dir() )
    if "remove-build" == MarathonConfig.command(): op_remove_build()
    if "show-sources" == MarathonConfig.command(): Utils.list_sources(MarathonConfig.source_dir(), 'marathon')
    if "remove-sources" == MarathonConfig.command(): op_remove_sources()
    