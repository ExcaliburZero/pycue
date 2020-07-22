from typing import List

import argparse
import sys

from . import interfaces


def main(argv: List[str]) -> None:
    parser = argparse.ArgumentParser()

    args = parser.parse_args(argv)

    usb_interface = interfaces.USBInterface()


if __name__ == "__main__":
    main(sys.argv[1:])
