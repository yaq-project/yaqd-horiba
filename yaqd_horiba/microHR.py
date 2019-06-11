import asyncio

from yaq_daemon_core import hardware

from gen_py import JYMono

__all__ = ["MicroHRDaemon"]


class MicroHRDaemon(hardware.BaseHardwareDaemon):
    defaults = {
        "make": "Horiba Jobin-Yvon",
        "model": "MicroHR",
        "force_init": True,
        "emulate": False,
    }
    default_state = {"position": 0, "turret": 1}

    def __init__(self, name, config, config_filepath):
        super().__init__(name, config, config_filepath)
        self.unique_id = config["unique_id"]
        self.controller = JYMono.Monocromator()
        self.controller.Uniqueid = self.unique_id

        self._busy.set()
        self.controller.Load()
        self.controller.OpenCommunications()
        self.controller.Initialize(config["force_init"], config["emulate"], True)

        self.description = self.controller.Description
        self.serial = self.controller.SerialNumber

        loop = asyncio.get_event_loop()
        loop.call_soon(self._reset_position())

    async def _reset_position(self):
        await self._not_busy.wait()
        self.controller.MovetoTurret(
            self._turret - 1
        )  # Legacy reasons for interface being one-based index
        self.set_position(self._destinaion)

    @hardware.set_action
    def set_turret(self, index):
        if index != self._turret:
            self._turret = index
            loop = asyncio.get_event_loop()
            loop.call_soon(self._reset_position())
        # TODO limits

    def _set_position(self, position):
        self.controller.MovetoWavelength(destination)

    async def update_state(self):
        while True:
            busy = self.controller.IsBusy()
            if busy:
                self._busy.set()
            else:
                self._not_busy.set()
            self._position = self.controller.GetCurrentWavelength()
            # TODO, do we want to have timeout to poll even when no set action has been called?
            await self._busy.wait()

    def get_grating_details(self):
        return self.controller.GetCurrentGratingWithDetails()


if __name__ == "__main__":
    MicroHRDaemon.main()
