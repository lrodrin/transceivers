import json
import logging

import requests

logging.basicConfig(level=logging.DEBUG)


def local_channel_assigment(host, params):
    """
    Creates a logical assignation between a Client and an Optical Channel

    :param host: ip REST Agent Adapter
    :type host: str
    :param params:
    :type params: dict
    :return:
    """
    request = requests.post('http://%s:5001/api/v1/openconfig/logical_channel_assignment' % host, headers=headers,
                            data=json.dumps(params))
    return request.json()


def optical_channel_configuration(host, params):
    """
    Creates a configuration of an Optical Channel by setting frequency, power and mode

    :param host: ip REST Agent Adapter
    :type host: str
    :param params:
    :type params: dict
    :return:
    """
    request = requests.post('http://%s:5001/api/v1/openconfig/optical_channel' % host, headers=headers,
                            data=json.dumps(params))
    return request.json()


def disconnect(host, och):
    """
    Disable Laser and Amplifier

    :param host: ip REST Agent Adapter
    :type host: str
    :param och: id that identify the Optical Channel configuration to be removed
    :type: int
    :return:
    """
    request = requests.delete('http://%s:5001/api/v1/openconfig/optical_channel/%s' % (host, och), headers=headers)
    return request.json()


def remove_logical_channel_assigment(host, client):
    """
    Remove logical assignations for the Client specified by client

    :param host: ip REST Agent Adapter
    :type host: str
    :param client: id to identify the Client assigned into logical assignations to be deleted
    :type: int
    :return:
    """
    request = requests.delete(
        'http://%s:5001/api/v1/openconfig/logical_channel_assignment/%s' % (host, client),
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

    # disconnect and remove local channel assignment c1 - och1
    print(disconnect(host_1, params_lca_host_1['och']))
    print(remove_logical_channel_assigment(host_1, params_lca_host_1['name']))

    # disconnect and remove local channel assignment c3 - och1
    print(disconnect(host_2, params_lca_host_2['och']))
    print(remove_logical_channel_assigment(host_2, params_lca_host_2['name']))
