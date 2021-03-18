from Rand48 import Rand48
from enum import Enum

class state(Enum):
    not_started = 0
    CPU = 1
    IO = 2
    waiting = 3
    terminated = 4

class Process:

    def __init__(self, name, arrival, num_bursts, timelist):
        """
        May need to add metrics(turnaround time, wait time...)
        """

        self.name = name
        self.arrival = arrival
        self.num_bursts = num_bursts
        self.timelist = timelist
        if self.arrival == 0:
            self.state = state.waiting
        else:
            self.state = state.not_started

    def tick_down():
        """
        Automatically adjust all attributes based on the current state of the
        process. Returns 0 if nothing needs to be done, 1 if this process is
        ready to be put into the queue, 2 if a processed just finished CPU
        burst, 3 if a process terminated
        """
        if self.state == state.terminated:
            return 0
        if self.state == state.not_started:
            self.arrival -= 1
            if self.arrival == 0:
                self.state = state.waiting
                return 1
            return 0
        if self.state == state.CPU or self.state == state.IO:
            timelist[0] -= 1
            if timelist[0] == 0:
                timelist.pop(0)
                self.burst -= 1
                if self.burst == 0:
                    self.state = state.terminated
                    return 3
                if self.state == state.IO:
                    self.state = state.waiting
                    return 1
                self.state = state.IO
                return 2
        return 0
