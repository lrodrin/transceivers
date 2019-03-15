import ast

from six.moves import configparser


def get_config(id, file):
    config = configparser.RawConfigParser()
    config.read(file)

    # Laser section
    print(config.get('laser', 'ip'))
    print(config.get('laser', 'channel'))

    # DAC/OSC section
    l = ast.literal_eval(config.get('dac_osc', 'logical_associations'))
    print(list(l))
    for elem in l:
        print(elem)

    # REST API section
    print(config.get('rest_api', 'ip'))

    if id == 2:
        # OA section
        print(config.get('oa', 'ip'))
        print(config.get('oa', 'power'))

        # WSS section
        d = ast.literal_eval(config.get('wss', 'operations'))
        print(dict(d))


if __name__ == '__main__':
    files = ["blue_bvt1.cfg", "blue_bvt2.cfg", "metro_bvt1.cfg", "metro_bvt2.cfg"]

    print("BLUE")
    get_config(1, files[0])

    print("METRO")
    get_config(2, files[2])
