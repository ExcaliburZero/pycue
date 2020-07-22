from typing import List

import argparse
import sys

from . import interfaces
from . import protocol


def main(argv: List[str]) -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("num_fans", type=int)

    args = parser.parse_args(argv)

    usb_interface = interfaces.USBInterface(debug=True)

    leds_per_fan = 16

    messages = [
        protocol.LEDGroupsClear(),
        protocol.LEDGroupSet(0, args.num_fans * leds_per_fan, 0),
        protocol.LEDTrigger(),
    ]

    for msg in messages:
        response = usb_interface.send(msg)
        print(response)

        assert isinstance(response, protocol.Ok)


if __name__ == "__main__":
    main(sys.argv[1:])
