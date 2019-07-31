import asyncio
import struct

import usb.core

from yaqd_core import hardware


__all__ = ["MicroHRDaemon"]


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


class MicroHRDaemon(hardware.ContinuousHardwareDaemon):
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

        self._busy.set()

        # Lie to the device that it speaks US English
        # Without this, the strings reading from USB don't work
        self._dev._langids = (LANG_ID_US_ENGLISH,)
        self.description = self._dev.product
        self.serial = self._dev.serial_number

        self.home()

    async def _reset_position(self):
        print("in reset_position")
        if self._busy.is_set():
            await self._not_busy.wait()
        print(self._turret)
        self._dev.ctrl_transfer(
            B_REQUEST_OUT,
            BM_REQUEST_TYPE,
            wIndex=SET_TURRET,
            data_or_wLength=struct.pack("<i", self._turret),
        )
        self._busy.set()
        await self._not_busy.wait()
        self.set_position(self._destination)
        # _, lo, hi = self.controller.IsTargetWithinLimits(0, 0)
        # self._limits = [(lo, hi)]

    def home(self):
        # Send "Initialize command, which homes the motor"
        self._dev.ctrl_transfer(0x40, 0xB3, wValue=0, wIndex=0)
        loop = asyncio.get_event_loop()
        loop.create_task(self._reset_position())

    @hardware.set_action
    def set_turret(self, index):
        print(self._turret, index)
        if index != self._turret:
            self._turret = index
            loop = asyncio.get_event_loop()
            loop.create_task(self._reset_position())

    def _set_position(self, position):
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
            busy = struct.unpack("<i", busy)[0]
            if busy:
                self._busy.set()
            else:
                self._not_busy.set()
            self._position = struct.unpack(
                "<f",
                self._dev.ctrl_transfer(
                    B_REQUEST_IN, BM_REQUEST_TYPE, wIndex=READ_WAVELENGTH, data_or_wLength=4
                ),
            )[0]
            await asyncio.sleep(0.01)
            await self._busy.wait()

    def get_state(self):
        state = super().get_state()
        state["turret"] = self._turret
        return state

    def _load_state(self, state):
        super()._load_state(state)
        self._turret = state.get("turret", 0)


if __name__ == "__main__":
    MicroHRDaemon.main()
