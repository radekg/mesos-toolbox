import os

class DefaultsMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(DefaultsMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Defaults(object):
    __metaclass__ = DefaultsMeta

    @staticmethod
    def mesos_sources_dir():
      return os.path.expanduser("~/.mesos-toolbox/mesos/sources")

    @staticmethod
    def mesos_packages_dir():
      return os.path.expanduser("~/.mesos-toolbox/mesos/packages")

    @staticmethod
    def marathon_sources_dir():
      return os.path.expanduser("~/.mesos-toolbox/marathon/sources")

    @staticmethod
    def marathon_packages_dir():
      return os.path.expanduser("~/.mesos-toolbox/marathon/packages")