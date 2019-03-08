"""This module generates the dataset
"""
import pyangbind.lib.pybindJSON as pybindJSON
import sys

from Netconf.bindings.bindingConfiguration import blueSPACE_DRoF_configuration


def make_DRoF_configuration(status, NCF, FEC, equalization, subcarrier_id, bps, pps):
    """

    :return:
    """
    model = blueSPACE_DRoF_configuration()
    model.DRoF_configuration._set_status(status)
    model.DRoF_configuration._set_nominal_central_frequency(NCF)
    model.DRoF_configuration.constellation._set_subcarrier_id(subcarrier_id)
    model.DRoF_configuration.constellation._set_bitsxsymbol(bps)
    model.DRoF_configuration.constellation._set_powerxsymbol(pps)
    model.DRoF_configuration._set_FEC(FEC)
    model.DRoF_configuration._set_equalization(equalization)
    # model.DRoF_configuration.monitor._set_subcarrier_id(subcarrier_id)
    # model.DRoF_configuration.monitor._set_SNR(SNR)
    # model.DRoF_configuration._set_BER(BER)
    return pybindJSON.dumps(model)


def main():
    configuration = make_DRoF_configuration("active", "NCF", "HD-FEC", "MMSE", "1", "2", "3")
    print(configuration)

    f = open("blueSPACE_DRoF_configuration.json", "w")
    f.write(configuration)


if __name__ == '__main__':
    sys.exit(main())
