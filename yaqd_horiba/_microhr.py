import asyncio
import struct

import usb.core  # type: ignore

from ._horiba_mono import HoribaMono, MICRO_HR_ID_PRODUCT

__all__ = ["MicroHR"]


class MicroHR(HoribaMono):
    _kind = "horiba-micro-hr"
    _ID_PRODUCT = MICRO_HR_ID_PRODUCT
