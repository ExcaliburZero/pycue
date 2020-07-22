from dataclasses import dataclass
from typing import List

import enum


class Response:
    pass


@dataclass
class Ok(Response):
    pass


class Message:
    pass


@dataclass
class LEDTrigger(Message):
    pass


@dataclass
class LEDClear(Message):
    pass


@dataclass
class LEDGroupSet(Message):
    led_start_index: int
    led_count: int
    mode: int


@dataclass
class LEDGroupsClear(Message):
    pass


class ChannelMode(enum.Enum):
    # No lighting is active for the channel. The LEDs will not be updated.
    Disabled = 0x00

    # The Hardware Playback uses lighting effects defined by LEDGroups and LEDController renders the effects themself.
    # This mode works even without an USB connection.
    HardwarePlayback = 0x01

    # All lighting effects are rendered by iCUE and only the RGB values are transferred via USB to the device. This
    # requires an USB connection.
    SoftwarePlayback = 0x02


@dataclass
class LEDMode(Message):
    channel_mode: ChannelMode


class PortType(enum.Enum):
    # WS2812B used by all new Corsair devices
    WS2812B = 0x01

    # UCS1903 only used for the SP fan
    UCS1903 = 0x02


@dataclass
class LEDPortType(Message):
    port_type: PortType
