def print_current_config(config):
    print("\n========== CURRENT RUNNING CONFIG: ==========\n")
    return config
    # return value

def module_changes(config):
    print("\n========== CONFIG HAS CHANGED, CURRENT RUNNING CONFIG: ==========\n")
    print_current_config(config)


def caller(config, funtion):
    return funtion(config)
