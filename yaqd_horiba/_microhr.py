import asyncio
import struct

import usb.core  # type: ignore

from yaqd_core import ContinuousHardware, logging

from .__version__ import __branch__


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


class MicroHR(ContinuousHardware):
    _kind = "micro-hr"
    _version = "1.0.0" + f"+{__branch__}" if __branch__ else ""
    traits = ["has-turret", "is-homeable"]
    defaults = {
        "make": "Horiba Jobin-Yvon",
        "model": "MicroHR",
        "force_init": True,
        "emulate": False,
    }

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
        self._gratings = [{"lines_per_mm": 1200}, {"lines_per_mm": 1200}]
        [g.update(c) for g, c in zip(self._gratings, config.get("gratings"))]

        self.home()

    async def _reset_position(self):
        self.logger.debug("in reset_position")

        if self._busy:
            await self._not_busy_sig.wait()
        self.logger.debug(self._turret)
        self._dev.ctrl_transfer(
            B_REQUEST_OUT,
            BM_REQUEST_TYPE,
            wIndex=SET_TURRET,
            data_or_wLength=struct.pack("<i", self._turret),
        )
        self._busy = True
        await self._not_busy_sig.wait()
        self.set_position(self._destination)
        # _, lo, hi = self.controller.IsTargetWithinLimits(0, 0)
        # self._limits = [(lo, hi)]

    def home(self):
        # Send "Initialize command, which homes the motor"
        self._dev.ctrl_transfer(0x40, 0xB3, wValue=0, wIndex=0)
        loop = asyncio.get_event_loop()
        loop.create_task(self._reset_position())

    def set_turret(self, index):
        self._busy = True
        self.logger.debug(self._turret, index)
        if index != self._turret:
            self._turret = index
            loop = asyncio.get_event_loop()
            loop.create_task(self._reset_position())

    def _set_position(self, position):
        # Mono assumes 1200 lines/mm, adjust accordingly
        self.logger.debug(position)
        position = position * self._gratings[self._turret]["lines_per_mm"] / 1200.0
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
            self._position = struct.unpack(
                "<f",
                self._dev.ctrl_transfer(
                    B_REQUEST_IN, BM_REQUEST_TYPE, wIndex=READ_WAVELENGTH, data_or_wLength=4
                ),
            )[0]
            self._position = self._position / (
                self._gratings[self._turret]["lines_per_mm"] / 1200.0
            )
            await asyncio.sleep(0.01)
            await self._busy_sig.wait()

    def get_state(self):
        state = super().get_state()
        state["turret"] = self._turret
        return state

    def _load_state(self, state):
        super()._load_state(state)
        self._turret = state.get("turret", 0)


if __name__ == "__main__":
    MicroHR.main()
