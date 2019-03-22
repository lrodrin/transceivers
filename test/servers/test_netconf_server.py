from netconf.client import NetconfSSHSession

# connexion parameters
host = '10.1.7.64'
port = 830
username = "root"
password = "netlabN."

# connexion to NETCONF Server
session = NetconfSSHSession(host, port, username, password)

# NETCONF Server capabilities
c = session.capabilities
print(c)

session.close()
