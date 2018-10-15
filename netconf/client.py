from netconf.client import NetconfSSHSession

session = NetconfSSHSession('127.0.0.1', 830, 'admin', 'admin')
config = session.get()