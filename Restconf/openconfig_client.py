import json
import requests


def local_channel_assigment(host, params):
    """
    Creates a logical assignation between a Client and an Optical Channel.

    :param host: ip REST OPENCONFIG Adapter server
    :type host: str
    :param params: client and the optical channel to be assigned
    :type params: dict
    :return: successful assignation message if not exists internal errors
    :rtype:
    """
    request = requests.post('http://%s:5001/api/v1/openconfig/logical_channel_assignment' % host, headers=headers,
                            data=json.dumps(params))
    return request.json()


def optical_channel_configuration(host, params):
    """
    Configure an Optical Channel by setting frequency, power and mode.

    :param host: ip REST OPENCONFIG Adapter server
    :type host: str
    :param params: parameters of the Optical Channel to be configured
    :type params: dict
    :return: successful configuration message if not exists internal errors and average BER
    :rtype:
    """
    request = requests.post('http://%s:5001/api/v1/openconfig/optical_channel' % host, headers=headers,
                            data=json.dumps(params))
    return request.json()


def remove_optical_channel(host, och):
    """
    Disable Laser and Amplifier.

    :param host: ip REST OPENCONFIG Adapter server
    :type host: str
    :param och: Optical Channel ID
    :type: int
    :return: removed configuration message if not exists internal errors
    :rtype:
    """
    request = requests.delete('http://%s:5001/api/v1/openconfig/optical_channel/%s' % (host, och), headers=headers)
    return request.json()


def remove_logical_channel_assigment(host, client):
    """
    Remove logical assignations between specified client and Optical Channel assigned.

    :param host: ip REST OPENCONFIG Adapter server
    :type host: str
    :param client: Client ID
    :type: int
    :return: removed logical channel assignations message if not exists internal errors
    :rtype:
    """
    request = requests.delete('http://%s:5001/api/v1/openconfig/logical_channel_assignment/%s' % (host, client),
                              headers=headers)
    print(request.json())


if __name__ == '__main__':
    host_1 = "10.1.7.65"
    host_2 = "10.1.7.67"
    headers = {"Content-Type": "application/json"}
    params_lca_host_1 = {'name': 'c1', 'och': 'channel-101', 'status': 'enabled', 'type': 'client'}
    params_lca_host_2 = {'name': 'c3', 'och': 'channel-101', 'status': 'enabled', 'type': 'client'}
    params_occ = {'frequency': 193400000, 'mode': '111', 'name': 'channel-101', 'power': -1.3, 'status': 'enabled',
                  'type': 'optical_channel'}

    # local channel assignment and optical channel configuration c1 - och1
    print(local_channel_assigment(host_1, params_lca_host_1))
    print(optical_channel_configuration(host_1, params_occ))

    # local channel assignment and optical channel configuration c3 - och1
    print(local_channel_assigment(host_2, params_lca_host_2))
    print(optical_channel_configuration(host_2, params_occ))

    # remove optical_channel configuration and remove local channel assignment c1 - och1
    print(remove_optical_channel(host_1, params_lca_host_1['och']))
    print(remove_logical_channel_assigment(host_1, params_lca_host_1['name']))

    # remove optical_channel configuration and remove local channel assignment c3 - och1
    print(remove_optical_channel(host_2, params_lca_host_2['och']))
    print(remove_logical_channel_assigment(host_2, params_lca_host_2['name']))
