from dataclasses import dataclass

import usb.core

from . import protocol


class Interface:
    def send(self, command: protocol.Message) -> protocol.Response:
        raise NotImplementedError()


@dataclass
class USBInterface(Interface):
    id_vendor: int
    id_product: int
    device: usb.core.Device
    endpoint: usb.core.Endpoint

    # TODO: consider supporting devices other than Lightning Node Pro
    def __init__(
        self, id_vendor: int = 0x1B1C, id_product: int = 0x0C0B, activate: bool = True
    ) -> None:
        self.id_vendor = id_vendor
        self.id_product = id_product

        if activate:
            self.activate()

    def activate(self) -> None:
        """
        Activates the connection to the USB device so that we can communicate with it.
        """
        usb_dev = usb.core.find(idVendor=self.id_vendor, idProduct=self.id_product)

        if usb_dev is None:
            raise ValueError(
                f"device not found: id_vendor={self.id_vendor}, id_product={self.id_product}"
            )
        else:
            self.device = usb_dev

        self.device.set_configuration()

        device_config = self.device.get_active_configuration()
        interface = device_config[(0, 0)]

        self.endpoint = usb.util.find_descriptor(
            interface,
            # match the first OUT endpoint
            custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress)
            == usb.util.ENDPOINT_OUT,
        )

    def send(self, command: protocol.Message) -> protocol.Response:
        pass
