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
        process = Popen(args=command, stdout=PIPE, stderr=PIPE, shell=True)
        # TODO: implement forwarding stdout / stderr to a build specific log file
        process.wait()
        return { 'ExitCode': process.returncode, 'StdOut': process.stdout.read(), 'StdErr': process.stderr.read() }

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