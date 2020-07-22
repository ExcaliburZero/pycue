from dataclasses import dataclass
from types import TracebackType
from typing import List, Optional, Type

import usb.core

from . import protocol


class Interface:
    def send(self, message: protocol.Message) -> protocol.Response:
        raise NotImplementedError()


MESSAGE_N_BYTES: int = 64
RESPONSE_N_BYTES: int = 16

WRITE_LED_TRIGGER: int = 0x33
WRITE_LED_CLEAR: int = 0x34
WRITE_LED_GROUP_SET: int = 0x35
WRITE_LED_GROUPS_CLEAR: int = 0x37
WRITE_LED_MODE: int = 0x38
WRITE_LED_PORT_TYPE: int = 0x3B

PROTOCOL_RESPONSE_OK: int = 0x00


@dataclass
class USBConnection:
    device: usb.core.Device
    endpoint: usb.core.Endpoint


@dataclass
class USBInterface(Interface):
    id_vendor: int
    id_product: int
    debug: bool
    connection: Optional[USBConnection]

    # TODO: consider supporting devices other than Lightning Node Pro
    def __init__(
        self, id_vendor: int = 0x1B1C, id_product: int = 0x0C0B, debug: bool = False,
    ) -> None:
        self.id_vendor = id_vendor
        self.id_product = id_product
        self.debug = debug
        self.connection = None

    def __enter__(self) -> "USBInterface":
        self.connect()

        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        self.disconnect()

        return None

    def connect(self) -> None:
        """
        Activates the connection to the USB device so that we can communicate with it.
        """
        device = usb.core.find(idVendor=self.id_vendor, idProduct=self.id_product)

        if device is None:
            raise ValueError(
                f"device not found: id_vendor={self.id_vendor}, id_product={self.id_product}"
            )

        device.reset()
        device.set_configuration()

        device_config = device.get_active_configuration()
        interface = device_config[(0, 0)]

        usb.util.claim_interface(device, interface)

        endpoint = usb.util.find_descriptor(
            interface,
            # match the first OUT endpoint
            custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress)
            == usb.util.ENDPOINT_OUT,
        )

        self.connection = USBConnection(device=device, endpoint=endpoint)

    def disconnect(self) -> None:
        if self.connection is None:
            raise RuntimeError(
                "This USBInterface has not yet been connected to the USB device."
            )

        usb.util.dispose_resources(self.connection.device)

    def send(self, message: protocol.Message) -> protocol.Response:
        if self.connection is None:
            raise RuntimeError(
                "This USBInterface has not yet been connected to the USB device."
            )

        payload = self.message_to_bytes(message)
        packet = self.pad_to_64(payload)

        if self.debug:
            print(f"Sending: {message}")
            print("\t" + ", ".join([hex(b) for b in payload]))

        self.connection.endpoint.write(bytes(packet))
        response_packet = self.connection.endpoint.read(RESPONSE_N_BYTES)

        response = self.bytes_to_response(list(response_packet))

        if self.debug:
            print(f"Recieved: {response}")
            print("\t" + ", ".join([hex(b) for b in response_packet]))

        return response

    @staticmethod
    def message_to_bytes(message: protocol.Message) -> List[int]:
        if isinstance(message, protocol.LEDTrigger):
            return [WRITE_LED_TRIGGER]
        elif isinstance(message, protocol.LEDClear):
            return [WRITE_LED_CLEAR]
        elif isinstance(message, protocol.LEDGroupsClear):
            return [WRITE_LED_GROUPS_CLEAR]
        elif isinstance(message, protocol.LEDPortType):
            return [WRITE_LED_PORT_TYPE, 0x00, message.port_type.value]
        elif isinstance(message, protocol.LEDMode):
            return [WRITE_LED_MODE, 0x00, message.channel_mode.value]
        elif isinstance(message, protocol.LEDGroupSet):
            return [
                WRITE_LED_GROUP_SET,
                0x00,
                message.led_start_index,
                message.led_count,
                message.mode,
                0x01,
                0x01,
            ]
        else:
            raise NotImplementedError(
                f"Sending {type(message)} is not implemented for USBInterface. ({message})"
            )

    @staticmethod
    def pad_to_64(payload: List[int]) -> List[int]:
        return payload + [0] * (MESSAGE_N_BYTES - len(payload))

    @staticmethod
    def bytes_to_response(response_bytes: List[int]) -> protocol.Response:
        if response_bytes[0] == PROTOCOL_RESPONSE_OK:
            return protocol.Ok()
        else:
            raise NotImplementedError(f"Unrecognized response: {response_bytes}")
