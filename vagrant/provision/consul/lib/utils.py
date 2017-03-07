import json, logging, os, sys
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
    def cmd(command):
        output  = list()
        process = Popen(args=command, stdout=PIPE, stderr=PIPE, shell=True)
        for line in process.stdout:
            output.append(line)
        process.wait()
        return { 'ExitCode': process.returncode,
                 'Success': (process.returncode == 0),
                 'StdOut': "".join(output),
                 'StdErr': process.stderr.read() }

    @staticmethod
    def read_stdin():
        stdin_lines = list()
        for line in sys.stdin: stdin_lines.append( line )
        return stdin_lines

    @staticmethod
    def source_provisioner_env():
        # get the provisioner directory
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        process = Popen( args="$(which bash) -c 'source {}/env-setup.sh; env'".format(base),
                         stdout=PIPE, stderr=PIPE,
                         shell=True )
        for line in process.stdout:
            ( key, _, value ) = line.strip().partition("=")
            os.environ[key] = value
        process.wait()
        if process.returncode != 0:
            exit(200)

    @staticmethod
    def get_log(program):
        Utils.source_provisioner_env()

        log = logging.getLogger(os.path.basename(program))
        log.setLevel(logging.INFO)
        # create handlers
        file_handler    = logging.FileHandler(os.environ['PROVISIONING_LOG_FILE'])
        file_handler.setLevel(logging.INFO)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        # create loggin format:
        formatter = logging.Formatter("[@:%(created)f]:[%(name)s]: %(message)s")
        # set formatter
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        # add handlers
        log.addHandler(file_handler)
        log.addHandler(console_handler)
        # return the log
        return log

    @staticmethod
    def arbitrary_systemctl_cmd(command, name, _type):
        result = Utils.cmd("systemctl {} {}.{}".format(command, name, _type))
        return result

    @staticmethod
    def start_service(service_name):
        return Utils.arbitrary_systemctl_cmd('start', service_name, 'service')

    @staticmethod
    def stop_service(service_name):
        return Utils.arbitrary_systemctl_cmd('stop', service_name, 'service')

    @staticmethod
    def restart_service(service_name):
        return Utils.arbitrary_systemctl_cmd('restart', service_name, 'service')

    @staticmethod
    def reload_service(service_name):
        return Utils.arbitrary_systemctl_cmd('reload', service_name, 'service')

    @staticmethod
    def reload_consul(LOG):
        LOG.info("Reloading Consul service")
        result = Utils.cmd("systemctl reload {}".format( os.environ['SVC_NAME_CONSUL'] ))
        return result

    @staticmethod
    def write_text(data, path):
        with open(path, "w") as f:
             f.write( data )

    @staticmethod
    def write_json(data, path):
        with open(path, "w") as f:
             f.write( json.dumps(data, indent=4) )
