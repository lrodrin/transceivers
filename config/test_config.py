from six.moves import configparser
import ast

if __name__ == '__main__':
    file = "blue_bvt1.cfg"
    config = configparser.RawConfigParser()
    config.read(file)

    print(config.get('laser', 'ip'))
    print(config.get('laser', 'channel'))

    l = ast.literal_eval(config.get('dac_osc', 'logical_associations'))
    print(list(l))
    for elem in l:
        print(elem)
