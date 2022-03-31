import threading
import time
from . import devices


class GadgetManager:
    def __init__(self) -> None:
        self.types = {
            "acm": (devices.ACMGadget, []),
            "ecm": (devices.ECMGadget, ["dev_addr", "host_addr"]),
            "mass_storage": (devices.MassStorageGadget, ["lun_list"]),
            "rndis": (devices.RNDISGadget, ["dev_addr", "host_addr"]),
        }
        self.running = True
        self.activated = False
        self._active = None

    @property
    def active(self):
        if self._active:
            return self._active
        return "none"

    def deactivate(self):
        """Stop the currently active gadget"""
        if self.activated:
            self.activated = False
        if self._active:
            self._active = None

    def run(self, g_type, **kwargs):
        """Set a new gadget to be active"""
        if g_type not in self.types.keys():
            return False

        thread_kwargs = {}
        thread_kwargs["gadget"] = self.types[g_type][0]
        thread_kwargs["g_type"] = g_type
        thread_kwargs["gadget_kwargs"] = kwargs

        thread = threading.Thread(target=self._run_usb_gadget, kwargs=thread_kwargs)
        thread.daemon = True
        self.deactivate()
        time.sleep(0.5)
        thread.start()

    def _run_usb_gadget(self, gadget=None, g_type="", gadget_kwargs={}):
        print("Started USB Gadget Thread for {} Device".format(g_type))

        try:
            with gadget(**gadget_kwargs) as g:
                self.activated = True
                self._active = g_type
                while self.activated and self.running:
                    time.sleep(0.1)
        except OSError:
            print(
                "An OSError occurred; probably crashed and failed to remove the configFS.\n"
                "A reboot should fix this."
            )
            return False

        print("Exiting USB Gadget Thread for {} Device".format(g_type))
