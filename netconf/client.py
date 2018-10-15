from netconf.client import connect_ssh

with connect_ssh('127.0.0.1', 830, 'myuser', 'mysecert') as session:
    config = session.get_config()