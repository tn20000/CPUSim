import argparse
from enum import Enum
from Rand48 import Rand48
import math
import heapq

class Precedence(Enum):
    END = 'END'
    BEGINNING = 'BEGINNING'

def parsing():
    parser = argparse.ArgumentParser(description='opsys simulation project')
    parser.add_argument('n', type=int, help='number of processes')
    parser.add_argument('seed', type=int, help='the seed for random number generator')
    parser.add_argument('Lambda', type=float, help='the inverse of the average of the exponential distribution')
    parser.add_argument('max', type=float, help='upper bound for random numbers')
    parser.add_argument('tcs', type=int, help='time required for context switch')
    parser.add_argument('alpha', type=float, help='constant for exponential averaging for SJF & SRT')
    parser.add_argument('tslice', type=float, help='time slice for RR')
    parser.add_argument('rradd', type=Precedence, help='whether processes are added to the END or BEGINNING in RR. The default is END', default='END', nargs='?')
    return parser.parse_args()

def main(args):
    """
    Pseudocode:
    for each algorithm:
        1. create a random number generator (reseed)
        2. for each process (1 to n):
            a. calculate the arrival time, number of bursts, and the length of 
            each burst(stored in a list) using the random number generator
            ** there will be no IO burst after the last CPU burst, so 
            len(timelist) == 2 * num_burst - 1 **
            b. create a process object with those attributes
        3. set clock to 0
        4. do a first pass to see if there's any process arriving at time 0, if
        so set cpu_state to context switching, else to idle
        5. while (True):
            ** The CPU has 3 states: CPU burst, context switching, idle. **

            a. increase clock by 1
            b. tick_down all processes (by calling tick_down)
            c. based on the return value of tick_down, put all processes ready
               into the queue 
               ** Queue would be different for different algorithms--FIFO queue,
               priority queue...**
            后面实在写不下去了
    """
def FCFS():
    pass

    rand = Rand48(args.seed, args.Lambda, args.max)
    FCFS()
    Rand48(args.seed, args.Lambda, args.max)
    SJF()
    Rand48(args.seed, args.Lambda, args.max)
    SRT()
    Rand48(args.seed, args.Lambda, args.max)
    RR()

if __name__ == '__main__':
    args = parsing()
    rand = Rand48(args.seed, args.Lambda, args.max)
    clock = 0
    arrival = math.floor(rand.next_exp())
    clock += arrival
    print(arrival)
    num_bursts = math.ceil(rand.drand48() * 100)
    print(num_bursts)
    tcs = args.tcs // 2
    for i in range(num_bursts):
        clock += tcs
        clock += math.ceil(rand.next_exp())
        print('CPU:', clock)
        clock += tcs
        if i == num_bursts - 1:
            break
        clock += 10 * math.ceil(rand.next_exp())
        print('IO:', clock)
    
    clock = 0
    arrival = math.floor(rand.next_exp())
    clock += arrival
    print(arrival)
    num_bursts = math.ceil(rand.drand48() * 100)
    print(num_bursts)
    tcs = args.tcs // 2
    for _ in range(num_bursts):
        clock += tcs
        clock += math.ceil(rand.next_exp())
        print('CPU:', clock)
        clock += tcs
        clock += 10 * math.ceil(rand.next_exp())
        print('IO:', clock)