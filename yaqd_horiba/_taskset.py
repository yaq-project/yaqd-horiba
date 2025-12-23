"""helper for keeping tasks from premature garbage collection
"""


import asyncio


class TaskSet(set):
    """container class for tasks to keep strong references"""

    def add(self, task: asyncio.Task):
        super().add(task)
        task.add_done_callback(self.discard)

    def from_coro(self, coro):
        """create task and add to running loop"""
        task = asyncio.get_running_loop().create_task(coro)
        self.add(task)
