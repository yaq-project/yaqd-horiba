import asyncio
import struct

import usb.core  # type: ignore

from yaqd_core import HasTurret, IsHomeable, HasLimits, HasPosition, IsDaemon


__all__ = ["MicroHR"]


LANG_ID_US_ENGLISH = 0x409

# Identifiers of the product in USB spec
JOBIN_YVON_ID_VENDOR = 0xC9B
MICRO_HR_ID_PRODUCT = 0x100

# Parameters for ctrl_transfer
BM_REQUEST_TYPE = 0xB3
B_REQUEST_OUT = 0x40
B_REQUEST_IN = 0xC0

# wIndex values for USB commands
INITIALIZE = 0
SET_WAVELENGTH = 4
READ_WAVELENGTH = 2
SET_TURRET = 17
READ_TURRET = 16
IS_BUSY = 5


class MicroHR(HasTurret, IsHomeable, HasLimits, HasPosition, IsDaemon):
    _kind = "micro-hr"

    def __init__(self, name, config, config_filepath):
        # TODO: Support multiple monos on the same machine
        super().__init__(name, config, config_filepath)
        self._dev = usb.core.find(idVendor=JOBIN_YVON_ID_VENDOR, idProduct=MICRO_HR_ID_PRODUCT)

        self._busy = True

        # Lie to the device that it speaks US English
        # Without this, the strings read from USB don't work
        self._dev._langids = (LANG_ID_US_ENGLISH,)
        self.description = self._dev.product
        self.serial = self._dev.serial_number
        self._gratings = config["gratings"]
        self._units = "nm"

        self.home()

    async def _reset_position(self):
        self.logger.debug("in reset_position")

        if self._busy:
            await self._not_busy_sig.wait()
        self.logger.debug(self._state["turret"])
        self._dev.ctrl_transfer(
            B_REQUEST_OUT,
            BM_REQUEST_TYPE,
            wIndex=SET_TURRET,
            data_or_wLength=struct.pack("<i", self._state["turret"]),
        )
        self._busy = True
        await self._not_busy_sig.wait()
        self.set_position(self._state["destination"])
        # _, lo, hi = self.controller.IsTargetWithinLimits(0, 0)
        # self._limits = [(lo, hi)]

    def home(self):
        # Send "Initialize command, which homes the motor"
        self._dev.ctrl_transfer(0x40, 0xB3, wValue=0, wIndex=0)
        loop = asyncio.get_event_loop()
        loop.create_task(self._reset_position())

    def set_turret(self, index):
        self._busy = True
        self.logger.debug(self._state["turret"], index)
        if index != self._state["turret"]:
            self._state["turret"] = index
            loop = asyncio.get_event_loop()
            loop.create_task(self._reset_position())
            self._state["hw_limits"] = (0, 1580 * 1200 / self._gratings[index])

    def get_turret(self):
        return self._state["turret"]

    def _set_position(self, position):
        # Mono assumes 1200 lines/mm, adjust accordingly
        self.logger.debug(position)
        position = position * self._gratings[self._state["turret"]] / 1200.0
        self.logger.debug(position)
        self._dev.ctrl_transfer(
            B_REQUEST_OUT,
            BM_REQUEST_TYPE,
            wIndex=SET_WAVELENGTH,
            data_or_wLength=struct.pack("<f", position),
        )

    async def update_state(self):
        while True:
            busy = self._dev.ctrl_transfer(
                B_REQUEST_IN, BM_REQUEST_TYPE, wIndex=IS_BUSY, data_or_wLength=4
            )
            self._busy = struct.unpack("<i", busy)[0]
            self._state["position"] = struct.unpack(
                "<f",
                self._dev.ctrl_transfer(
                    B_REQUEST_IN, BM_REQUEST_TYPE, wIndex=READ_WAVELENGTH, data_or_wLength=4
                ),
            )[0]
            self._state["position"] = self._state["position"] / (
                self._gratings[self._state["turret"]] / 1200.0
            )
            await asyncio.sleep(0.01)
            await self._busy_sig.wait()
