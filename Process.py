from Rand48 import Rand48

class Process:
    """
    A Process class to represent a process
    """

    def __init__(self, name, arrival, num_bursts, timelist,tau):
        """
        @param name: the name of the process, A-Z
        @param arrival: the arrival time of the process
        @num_bursts: the total number of CPU bursts for the process
        @timelist: a list of times of CPU bursts and IO. Note that these two
        times are interleaved, i.e. timelist = [tcpu, tio, tcpu, tio, tcpu...],
        and the last number is always cpu time, 
        and len(timelist) == 2 * num_bursts - 1
        """

        self.name = name
        self.arrival = arrival
        self.num_bursts = num_bursts
        self.timelist = timelist
        self.tau=tau
        self.wait = []

    def __str__(self):
        """
        Method for printing
        @return str: the name of the process
        """
        return self.name

    def __lt__(self, value):
        """
        Method to compare two processes by their name. Useful for sorting a list
        of processes
        @param value: the rhs of the comparison
        @return comp: whether the name of the process occurs alphabetically
        before value.name
        """
        return self.name < value.name