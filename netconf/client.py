from netconf.client import NetconfSSHSession

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

session = NetconfSSHSession('10.1.7.64', 830, 'test', 'test')
config = session.get_config()

print(config)