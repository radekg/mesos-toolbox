#!/usr/bin/python
import os, re, time
from lib.config import Config
from lib.configs.chronos_config import ChronosConfig
from lib.utils import Utils

LOG = ChronosConfig.setup(__file__)

def validate_input():
    chronos_version = ChronosConfig.chronos_version()
    if chronos_version == "":
        Utils.exit_with_cmd_error( __file__, "Chronos version not given. Run with show-releases to see what the available versions are.")
    if not chronos_version in list_releases():
        Utils.exit_with_cmd_error( __file__,
                                   "Chronos version ({}) is not supported. Run with show-releases to see what the available versions are.".format(
                                    chronos_version ))

def list_releases():
    return Utils.list_releases(LOG, ChronosConfig.chronos_repository_dir(), ChronosConfig.chronos_master_branch())

def op_build():
    if Utils.ensure_sources(LOG, ChronosConfig.chronos_repository_dir(), ChronosConfig.chronos_git_repository()):
        validate_input()
        image_name = "chronos-docker-build"
        if not Utils.is_docker_image(LOG, image_name):
            LOG.info("Docker image not found. Building...")
            Utils.exit_if_docker_image_not_built( LOG,
                                                  ChronosConfig.docker_templates_dir(),
                                                  "default",
                                                  image_name )

        build_dir    = "{}/{}".format( ChronosConfig.work_dir(),
                               ChronosConfig.chronos_version() )
        packages_dir = "{}/{}".format( ChronosConfig.packages_dir(),
                               ChronosConfig.chronos_version() )

        if os.path.exists(packages_dir):
            if not Utils.confirm("Chronos build for {} already exists. To rebuild, continue.".format(
                    ChronosConfig.chronos_version() )):
                LOG.info("You have cancelled the action.")
                exit(0)

        build_log_file = "{}.{}.log".format(build_dir, str(int(time.time())))
        LOG.info("Recording build process to {}.".format(build_log_file))
        Config.set_cmd_log(build_log_file)

        # cleanup old data:
        Utils.cmd("rm -rf {}".format(packages_dir))
        Utils.cmd("rm -rf {}".format(build_dir))

        # copy sources
        LOG.info("Fetching Chronos {} sources...".format(ChronosConfig.chronos_git_repository()))
        Utils.cmd("cp -R {} {}".format( ChronosConfig.chronos_repository_dir(), build_dir ))

        # ensure branch / tag
        Utils.exit_if_git_release_not_set( LOG, build_dir,
                                           ChronosConfig.chronos_version(),
                                           ChronosConfig.chronos_master_branch(),
                                           ChronosConfig.chronos_git_repository() )

        chronos_mvn_version = None
        if os.path.exists("{}/pom.xml".format( build_dir )):
            chronos_res = Utils.cmd("cat {}/pom.xml | grep '<version>' | head -n1 | sed 's/.*>\\(.*\\)<.*/\\1/' 2>/dev/null".format( build_dir ))
            if chronos_res['ExitCode'] != 0:
                LOG.error("Not able to establish Chronos version from the POM file. Can't continue.")
                exit(112)
            chronos_mvn_version = chronos_res['StdOut'].strip()
        else:
            LOG.error("No pom.xml file for Chronos {}. Can't continue.".format( ChronosConfig.chronos_version() ))
            exit(110)

        if chronos_mvn_version == None:
            LOG.error("Version could not be reliably established from the pom.xml file. Can't continue.")
            exit(111)

        LOG.info("Chronos version from Maven: {}".format( chronos_mvn_version ))

        docker_command = list()
        docker_command.append("docker run -ti ")
        docker_command.append("-v {}:/output ".format( os.path.dirname(packages_dir) ))
        docker_command.append("-v {}:/chronos-src ".format( build_dir ))
        docker_command.append("-v {}:/root/.m2 ".format( ChronosConfig.m2_dir() ))
        docker_command.append("-e \"BUILD_CHRONOS_VERSION={}\" ".format( ChronosConfig.chronos_version() ))
        docker_command.append("-e \"FPM_OUTPUT_VERSION={}\" ".format( chronos_mvn_version ))
        docker_command.append("-e \"ASSEMBLY_WITH_TESTS={}\" ".format( ChronosConfig.with_tests() ))
        docker_command.append("{} ".format( image_name ))
        docker_command.append("/bin/bash -c 'cd /chronos-build && ./chronos-build.sh; exit $?'")
        build_command = "".join( docker_command )
        LOG.info("Docker command: {}".format(build_command))
        LOG.info("Building Chronos {}. This will take a while...".format(ChronosConfig.chronos_version()))
        LOG.info("You can monitor the build with: tail -F {}".format(build_log_file))
        build_start_time = int(time.time())
        build_status = Utils.cmd(build_command)
        build_end_time = int(time.time())
        if build_status['ExitCode'] == 0:
            LOG.info( "Chronos {} built successfully. Build took {} seconds. Output available in {}. Cleaning up...".format(
                      ChronosConfig.chronos_version(),
                      str( build_end_time - build_start_time ),
                      packages_dir ))
            Utils.cmd("rm -rf {}".format(build_dir))
        else:
            LOG.error( "Chronos build failed. Leaving build log and temp directory for inspection. chronos={}".format( build_dir ) )
            exit(107)

def op_show_releases():
    if Utils.ensure_sources(LOG, ChronosConfig.chronos_repository_dir(), ChronosConfig.chronos_git_repository()):
        LOG.info("Releases:")
        for line in list_releases():
            if line != "":
                print line

def op_remove_build():
    validate_input()
    if not Utils.confirm("You are about to remove Chronos build for {}.".format( ChronosConfig.chronos_version() )):
        LOG.info("You have cancelled the action.")
        exit(0)
    Utils.cmd("rm -rf {}/{}".format( ChronosConfig.packages_dir(),
                                     ChronosConfig.chronos_version()))

def op_remove_sources():
    if not Utils.confirm("You are about to remove Chronos sources for {}.".format( ChronosConfig.chronos_git_repository() )):
        LOG.info("You have cancelled the action.")
        exit(0)
    Utils.cmd("rm -rf {}".format( ChronosConfig.chronos_repository_dir() ))

def op_check_this_system():
    LOG.info("Checking dependencies:")
    LOG.info(" -> Docker? : {}".format( "Yes" if Utils.is_docker_available() else "No" ))
    LOG.info(" -> Git?    : {}".format( "Yes" if Utils.is_git_available() else "No" ))

if __name__ == "__main__":

    if "build" == ChronosConfig.command(): op_build()
    if "show-releases" == ChronosConfig.command(): op_show_releases()
    if "show-builds" == ChronosConfig.command(): Utils.list_builds( LOG, ChronosConfig.packages_dir() )
    if "remove-build" == ChronosConfig.command(): op_remove_build()
    if "show-sources" == ChronosConfig.command(): Utils.list_sources(ChronosConfig.source_dir(), 'chronos')
    if "remove-sources" == ChronosConfig.command(): op_remove_sources()
    if "check-this-system" == ChronosConfig.command(): op_check_this_system()
    