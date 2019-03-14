import ast

from six.moves import configparser

if __name__ == '__main__':
    file = "blue_bvt1.cfg"
    config = configparser.RawConfigParser()
    config.read(file)

    print(config.get('laser', 'ip'))
    print(config.get('laser', 'channel'))
    a = print(config.get('dac_osc', 'logical_associations'))

    d = ast.literal_eval(config.get('dac_osc', 'logical_associations'))
    print(list(a))
    for item in d:
        print(item)
