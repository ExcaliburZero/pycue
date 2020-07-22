from typing import List

import argparse
import sys

from . import interfaces
from . import protocol


def main(argv: List[str]) -> None:
    parser = argparse.ArgumentParser()

    args = parser.parse_args(argv)

    usb_interface = interfaces.USBInterface(debug=True)

    messages = [
        protocol.LEDGroupsClear(),
    ]

    for msg in messages:
        response = usb_interface.send(msg)
        print(response)

        assert isinstance(response, protocol.Ok)


if __name__ == "__main__":
    main(sys.argv[1:])
