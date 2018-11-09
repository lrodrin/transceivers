__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

def print_current_config(config):
    print("\n========== CURRENT RUNNING CONFIG: ==========\n")
    return config

def module_changes(config, old_val, new_val):
    print("\n========== CONFIG HAS CHANGED, CURRENT RUNNING CONFIG: ==========\n")
    print_current_config(config)
    print("\n========== CHANGES: =============================================\n")
    # iterfind()


def caller(config, funtion):
    return funtion(config)
