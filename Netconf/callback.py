import logging

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"


def print_current_config(config):
    logging.debug("\n========== CURRENT RUNNING CONFIG: ==========\n")
    logging.debug(config)


def module_changes(config):
    logging.debug("\n========== CONFIG HAS CHANGED================\n")
    print_current_config(config)
    logging.debug("\n========== CHANGES: =============================================\n")
    # iterfind()
    logging.debug("\n========== END OF CHANGES ====================================\n")


def caller(config, funtion):
    funtion(config)
