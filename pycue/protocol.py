from dataclasses import dataclass
from typing import List


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
class LEDGroupSet(Message):
    led_start_index: int
    led_count: int
    mode: int


@dataclass
class LEDGroupsClear(Message):
    pass
