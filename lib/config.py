import argparse, ConfigParser, errno, logging, os, sys

class ConfigMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(ConfigMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Config(object):
    __metaclass__ = ConfigMeta

    def __init__(self):
        self._arguments = []
        self._ready = False
        logging.basicConfig()

    def __ready__(self):
        if not self._ready:
            self.argparse = argparse.ArgumentParser()
            self.provided_args()
            self.standard_args()
            self.args = self.argparse.parse_args()
            self._ready = True

    @staticmethod
    def ready(program):
        Config().__ready__()
        l = logging.getLogger(os.path.basename(program))
        l.setLevel( getattr(logging, Config.args().log_level.upper() ) )
        return l

    @staticmethod
    def add_argument(*opt_str, **kwargs):
        Config()._arguments.append( [ opt_str, kwargs ] )

    def standard_args(self):
        self.argparse.add_argument( "--yes",
                                    dest="auto_accept",
                                    help="Automatically accept all confirmations.",
                                    action="store_true" )
        self.argparse.add_argument( "--log-level",
                                    dest="log_level",
                                    help="Log level",
                                    metavar="STRING",
                                    default="INFO")

    def provided_args(self):
        for opt in self._arguments:
            opt_str, kwargs = opt
            self.argparse.add_argument( *opt_str, **kwargs )

    @staticmethod
    def args():
        return Config().args

    @staticmethod
    def auto_accept():
        return Config().args.auto_accept

    @staticmethod
    def log_level():
        return Config().args.log_level.upper()

    @staticmethod
    def print_help():
        Config().argparse.print_help()