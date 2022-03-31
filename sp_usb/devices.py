from argparse import Namespace
import errno
import functionfs
import os
from functionfs.gadget import Gadget, ConfigFunctionKernel


class ACMFunction(ConfigFunctionKernel):
    type_name = "acm"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ECMFunction(ConfigFunctionKernel):
    type_name = "ecm"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MassStorageFunction(ConfigFunctionKernel):
    type_name = "mass_storage"

    def __init__(self, lun_list, name=None):
        self._lun_list = lun_list
        self._lun_dir_list = []

        super().__init__(
            config_dict={"stall": "1"},
            name=name,
        )

    def start(self, path):
        lun_dir_list = self._lun_dir_list
        for index, lun in enumerate(self._lun_list):
            lun_dir = os.path.join(path, "lun.%i" % index)
            if not os.path.exists(lun_dir):
                os.mkdir(lun_dir)
                lun_dir_list.append(lun_dir)
            with open(os.path.join(lun_dir, "file"), "w") as lun_file:
                lun_file.write(lun)
        super().start(path)

    def kill(self):
        for lun_path in self._lun_dir_list:
            os.rmdir(lun_path)
        # In the off-chance that it does something someday.
        super().kill()


class RNDISFunction(ConfigFunctionKernel):
    type_name = "rndis"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ACMGadget(Gadget):
    def __init__(self):

        super().__init__(
            config_list=[
                {
                    "function_list": [ACMFunction()],
                    "MaxPower": 250,
                    "lang_dict": {0x409: {"configuration": "Gadgeteer ACM"}},
                }
            ],
            idVendor=0x1D6B,  # Linux Foundation
            idProduct=0x0104,  # Multifunction Composite Gadget
            lang_dict={
                0x409: {"product": "GadgeteerACM", "manufacturer": "Gadgeteer"}
            },
            name="gadgeteer_acm",
        )


class ECMGadget(Gadget):
    def __init__(self, dev_addr="", host_addr=""):

        super().__init__(
            config_list=[
                {
                    "function_list": [
                        ECMFunction(
                            config_dict={"dev_addr": dev_addr, "host_addr": host_addr}
                        )
                    ],
                    "MaxPower": 250,
                    "lang_dict": {0x409: {"configuration": "Gadgeteer ECM"}},
                }
            ],
            idVendor=0x1D6B,  # Linux Foundation
            idProduct=0x0104,  # Multifunction Composite Gadget
            lang_dict={
                0x409: {"product": "GadgeteerECM", "manufacturer": "Gadgeteer"}
            },
            name="gadgeteer_ecm",
        )


class MassStorageGadget(Gadget):
    def __init__(self, lun_list=[]):

        super().__init__(
            config_list=[
                {
                    "function_list": [MassStorageFunction(lun_list=lun_list)],
                    "MaxPower": 250,
                    "lang_dict": {0x409: {"configuration": "Gadgeteer Mass Storage"}},
                }
            ],
            idVendor=0x1D6B,  # Linux Foundation
            idProduct=0x0104,  # Multifunction Composite Gadget
            lang_dict={
                0x409: {
                    "product": "GadgeteerMS",
                    "manufacturer": "Gadgeteer",
                }
            },
            name="gadgeteer_ms",
        )


class RNDISGadget(Gadget):
    def __init__(self, dev_addr="", host_addr=""):

        super().__init__(
            config_list=[
                {
                    "function_list": [
                        RNDISFunction(
                            config_dict={"dev_addr": dev_addr, "host_addr": host_addr}
                        )
                    ],
                    "MaxPower": 250,
                    "lang_dict": {0x409: {"configuration": "Gadgeteer RNDIS"}},
                }
            ],
            bDeviceClass=0xEF,
            bDeviceSubClass=0x02,
            bDeviceProtocol=0x01,
            # os_desc={
            #   "use": 1,
            #   "b_vendor_code": 0xcd,
            #   "qw_sign": "MSFT100"
            # },
            idVendor=0x1D6B,  # Linux Foundation
            idProduct=0x0104,  # Multifunction Composite Gadget
            lang_dict={
                0x409: {"product": "GadgeteerRNDIS", "manufacturer": "Gadgeteer"}
            },
            name="gadgeteer_rndis",
        )


def get_first_udc() -> str:
    for li in os.listdir(Gadget.class_udc_path):
        return li
    return ""
