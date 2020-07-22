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
class LEDGroupsClear(Message):
    pass
