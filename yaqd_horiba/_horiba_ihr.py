import asyncio
import math
import struct

import usb.core  # type: ignore

from ._horiba_mono import (
    HoribaMono,
    IHR320_ID_PRODUCT,
    B_REQUEST_IN,
    B_REQUEST_OUT,
    BM_REQUEST_TYPE,
    READ_SLITWIDTH,
    SET_SLITWIDTH,
    READ_MIRROR,
    SET_MIRROR,
    IS_BUSY,
    READ_WAVELENGTH,
)

__all__ = ["HoribaIHR320"]


class HoribaIHR320(HoribaMono):
    _kind = "horiba-ihr320"
    _ID_PRODUCT = IHR320_ID_PRODUCT

    async def _reset_position(self):
        await super()._reset_position()
        await self._not_busy_sig.wait()
        # Initialization takes a bit of time to be able to process mirror and slit changes
        await asyncio.sleep(5)

        for i in range(2):
            self._set_mirror(i, self._state["mirrors_dest"][i])
        for i in range(4):
            self._set_slit(i, self._state["slits_dest"][i])

    def _get_slit(self, index: int):
        # this assumes 7 mm slits, may be different for 2 mm slits
        const = 7 / 1000
        data = self._dev.ctrl_transfer(
            B_REQUEST_IN, BM_REQUEST_TYPE, wIndex=READ_SLITWIDTH, data_or_wLength=4, wValue=index
        )
        return const * struct.unpack("<i", data)[0]

    def _set_slit(self, index: int, width: float):
        """Set slit with index to width (in mm)"""
        if math.isnan(width):
            return
        self._busy = True
        self._state["slits_dest"][index] = width
        const = 7 / 1000
        self._dev.ctrl_transfer(
            B_REQUEST_OUT,
            BM_REQUEST_TYPE,
            wIndex=SET_SLITWIDTH,
            data_or_wLength=struct.pack("<i", round(width / const)),
            wValue=index,
        )

    def get_front_entrance_slit(self) -> float:
        return self._state["slits"][0]

    def get_side_entrance_slit(self) -> float:
        return self._state["slits"][1]

    def get_front_exit_slit(self) -> float:
        return self._state["slits"][2]

    def get_side_exit_slit(self) -> float:
        return self._state["slits"][3]

    def set_front_entrance_slit(self, width):
        return self._set_slit(0, width)

    def set_side_entrance_slit(self, width):
        return self._set_slit(1, width)

    def set_front_exit_slit(self, width):
        return self._set_slit(2, width)

    def set_side_exit_slit(self, width):
        return self._set_slit(3, width)

    def get_slit_limits(self):
        return (0, 7)

    def get_slit_units(self):
        return "mm"

    def _get_mirror(self, index: int):
        # this assumes 2 mm slits, may be different for 7 mm slits
        data = self._dev.ctrl_transfer(
            B_REQUEST_IN, BM_REQUEST_TYPE, wIndex=READ_MIRROR, data_or_wLength=4, wValue=index
        )
        return "side" if bool(struct.unpack("<i", data)[0]) else "front"

    def _set_mirror(self, index: int, side: str):
        """Set mirror with index to front or side"""
        self._busy = True
        self._state["mirrors_dest"][index] = side
        self._dev.ctrl_transfer(
            B_REQUEST_OUT,
            BM_REQUEST_TYPE,
            wIndex=SET_MIRROR,
            data_or_wLength=struct.pack("<i", side == "side"),
            wValue=index,
        )

    def get_entrance_mirror(self):
        return self._state["mirrors"][0]

    def get_exit_mirror(self):
        return self._state["mirrors"][1]

    def set_entrance_mirror(self, side: str):
        self._busy = True
        self._set_mirror(0, side)

    def set_exit_mirror(self, side: str):
        self._busy = True
        self._set_mirror(1, side)

    async def update_state(self):
        while True:
            busy = self._dev.ctrl_transfer(
                B_REQUEST_IN, BM_REQUEST_TYPE, wIndex=IS_BUSY, data_or_wLength=4
            )
            busy = struct.unpack("<i", busy)[0]
            prev_position = self._state["position"]
            reported_position = struct.unpack(
                "<f",
                self._dev.ctrl_transfer(
                    B_REQUEST_IN, BM_REQUEST_TYPE, wIndex=READ_WAVELENGTH, data_or_wLength=4
                ),
            )[0]
            self._state["position"] = reported_position / (
                self._gratings[self._state["turret"]]["lines_per_mm"] / 1200.0
            )
            still = prev_position == self._state["position"]
            for i in range(4):
                prev_position = self._state["slits"][i]
                self._state["slits"][i] = self._get_slit(i)
                still = still and (prev_position == self._state["slits"][i])
            for i in range(2):
                self._state["mirrors"][i] = self._get_mirror(i)
            self._busy = busy or not still
            if not self._busy:
                await asyncio.sleep(0.1)
            else:
                await asyncio.sleep(0.01)
