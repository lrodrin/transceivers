__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

def print_current_config(config):
    print("\n========== CURRENT RUNNING CONFIG: ==========\n")
    print(config)

def module_changes(config):
    print("\n========== CONFIG HAS CHANGED================\n")
    print_current_config(config)
    print("\n========== CHANGES: =============================================\n")
    # iterfind()
    print("\n========== END OF CHANGES ====================================\n")

def caller(config, funtion):
    funtion(config)
