from enum import Enum
from Rand48 import Rand48
from Process import Process
from Queue import Queue
import argparse
import math
import copy

class Precedence(Enum):
    """
    A precedence enum for parsing
    """
    END = 'END'
    BEGINNING = 'BEGINNING'

def parsing():
    """
    A method to parse all arguments
    @return args: a NameSpace containing all argument values 
    """
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

def create_processes(rand, n,tau):
    """
    A method to create all processes objects once and for all.
    @param rand: rand48 generator
    @param n: number of processes needed to be generated
    @return processes: list of processes generated
    """
    name = 'A'
    processes = []
    for _ in range(n):
        arrival = math.floor(rand.next_exp())
        num_bursts = math.ceil(rand.drand48() * 100)
        timelist = []
        for _ in range(num_bursts - 1):
            timelist.append(math.ceil(rand.next_exp()))
            timelist.append(math.ceil(rand.next_exp()) * 10)
        timelist.append(math.ceil(rand.next_exp()))
        processes.append(Process(name, arrival, num_bursts, timelist,int(tau)))
        name = chr(ord(name) + 1)
    return processes
def FCFS(processes, tcs, simout):
    """
    The FCFS algorithm
    @param processes: list of processes to be scheduled
    @param tcs: time required to perform **HALF** context switches, i.e. time
    needed to for either switching in or switching out
    @param simout: the out file object
    """

    # print all processes
    for p in processes:
        s = 's'
        if p.num_bursts == 1:
            s = ''
        print('Process', p.name, '[NEW] (arrival time', p.arrival, 'ms)', p.num_bursts, 'CPU burst{}'.format(s))

########################## Variable Initialization #############################

    # clock for counting time
    clock = 0 

    # queue of FCFS, could be changed to accommodate priority queue
    queue = Queue()

    # List of processes before arrival
    pre_arrival = [] 

    # List of processes currently doing IO. Note that this list must be sorted
    # at all times
    ios = []

    # Current bursting process. If the CPU is idle, this variable is set to None
    bursting = None

    # Indicates whether the CPU is doing the first half of the context switch
    switch_in = False

    # Indicates whether the CPU is doing the second half of the context switch
    switch_out = False

    # Preparation counter for context switch. If preparation == 0, context
    # switch is done
    preparation = tcs

    # The process that's going to IO. After a process ends its CPU burst, it's
    # "going" to IO, but it only actually goes to IO after the context switch
    # is done
    to_io = None

    # List of burst times to calculate the metrics
    burst_time = []

################################## Overhead ####################################

    print('time 0ms: Simulator started for FCFS', queue)

    # Put all processes to either the queue (if arrival time is 0) or the
    # pre_arrival list
    for p in processes:
        if p.arrival == 0:
            queue.push(p)
            print('time {}ms: Process {} arrived; placed on ready queue'.format(clock, p.name), queue)
        else:
            pre_arrival.append(p)

    # Select a process to burst if the queue is not empty
    if len(queue) != 0:
        bursting = queue.pop()
        p.wait.append(0)
        switch_in = True
        preparation = tcs - 1

################################# Simulation ###################################

    while (True):
        """
        The workflow:
        1. taking out a process from bursting
        2. add a new process to burst
        3. check for any completed IO
        4. check for any process arrival
        For ties in any of the above events, break with names in alphabetical
        order, i.e. Process A is should finish IO ahead of Process B
        """
        
        # Increment time first
        clock += 1

        # Do a CPU burst
        if bursting != None and (not switch_in):
            bursting.timelist[0] -= 1
            burst_time[-1] += 1
            
            # If a process finished bursting, check if the process is
            # terminating. If not, put it to IO. Also turns on context switches.
            if bursting.timelist[0] == 0:
                bursting.timelist.pop(0)
                bursting.num_bursts -= 1
                if bursting.num_bursts == 0:
                    print('time {}ms: Process {} terminated'.format(clock, bursting.name), queue)
                else:
                    s = 's'
                    if bursting.num_bursts == 1:
                        s = ''
                    if clock < 1000 or not __debug__:
                        print('time {}ms: Process {} completed a CPU burst; {} burst{} to go'.format(clock, bursting.name, bursting.num_bursts, s), queue)
                        print('time {}ms: Process {} switching out of CPU; will block on I/O until time {}ms'.format(clock, bursting.name, clock + bursting.timelist[0] + tcs), queue)
                    to_io = bursting
                switch_out = True
                preparation = tcs + 1
                bursting = None

        # Doing context switch and if context switch done, put a process into
        # bursting
        if switch_in:
            if preparation != 0:
                preparation -= 1
            else:
                switch_in = False
                burst_time.append(0)
                if clock < 1000 or not __debug__:
                    print('time {}ms: Process {} started using the CPU for {}ms burst'.format(clock, bursting.name, bursting.timelist[0]), queue)
        
        # Do IO for each process and check if any process completed IO. Note
        # that the IO list must always be in alphabetical order
        remove = []
        for p in ios:
            p.timelist[0] -= 1
            if p.timelist[0] == 0:
                p.timelist.pop(0)
                queue.push(p)
                p.wait.append(0)
                remove.append(p)
                if clock < 1000 or not __debug__:
                    print('time {}ms: Process {} completed I/O; placed on ready queue'.format(clock, p.name), queue)
        for p in remove:
            ios.remove(p)
        ios.sort()

        # Decrement arrival time and check if any process arrives
        remove.clear()
        for p in pre_arrival:
            p.arrival -= 1
            if p.arrival == 0:
                queue.push(p)
                p.wait.append(0)
                remove.append(p)
                if clock < 1000 or not __debug__:
                    print('time {}ms: Process {} arrived; placed on ready queue'.format(clock, p.name), queue)
        for p in remove:
            pre_arrival.remove(p)

        # Doing switch out. If done, put a process into IO.
        if switch_out:
            preparation -= 1
            if preparation == 0:
                switch_out = False
                if to_io != None:
                    ios.append(to_io)
                    ios.sort()
                to_io = None

        # If the CPU is idle and the queue is not empty, pop the queue and start
        # switching in
        if bursting == None and len(queue) != 0 and (not switch_out) and (not switch_in):
            bursting = queue.pop()
            switch_in = True
            preparation = tcs - 1

        # For each process that's still in the queue, increment its wait time
        # for metrics calculation
        for p in queue:
            p.wait[-1] += 1

        # If there isn't a process anywhere, break the simulation, and directly
        # add tcs to the clock to account for the final context switch
        if len(pre_arrival) == 0 and len(ios) == 0 and bursting == None and len(queue) == 0 and to_io == None:
            print('time {}ms: Simulator ended for FCFS'.format(clock + tcs), queue,'\n')
            break

############################# metrics calculation ##############################

    # Calculate average burst time
    avg_burst = sum(burst_time) / len(burst_time)

    # Calculate average wait time by appending all wait times from all processes
    # together, then get the average
    avg_wait = []
    for p in processes:
        avg_wait += p.wait
    avg_wait = sum(avg_wait) / len(avg_wait)

    # Create the metrics data. 
    # Note that avg_turnaround = avg_burst + avg_wait + tcs * 2
    # Here FCFS doesn't have preemptions.
    data = 'Algorithm FCFS\n' + \
           '-- average CPU burst time: {:.3f} ms\n'.format(avg_burst) + \
           '-- average wait time: {:.3f} ms\n'.format(avg_wait) + \
           '-- average turnaround time: {:.3f} ms\n'.format(avg_burst + avg_wait + tcs * 2) + \
           '-- total number of context switches: {}\n'.format(len(burst_time)) + \
           '-- total number of preemptions: 0\n' + \
           '-- CPU utilization: {:.3f}%\n'.format(sum(burst_time) / (clock + tcs) * 100)
    simout.write(data)
def tau_function(process,alpha):
    tau=math.ceil((1-alpha)*process.tau+alpha*process.cpu_time)
    return int(tau)
def SJF(processes, tcs, simout,lamb,alpha):
    """
    The SJF algorithm
    @param processes: list of processes to be scheduled
    @param tcs: time required to perform **HALF** context switches, i.e. time
    needed to for either switching in or switching out
    @param simout: the out file object
    """

    # print all processes
    for p in processes:
        s = 's'
        if p.num_bursts == 1:
            s = ''
        print('Process', p.name, '[NEW] (arrival time', p.arrival, 'ms)', p.num_bursts, 'CPU burst{} (tau {}ms)'.format(s,int(1/lamb)))

########################## Variable Initialization #############################

    # clock for counting time
    clock = 0 

    # queue of FCFS, could be changed to accommodate priority queue
    queue = Queue('pq')

    # List of processes before arrival
    pre_arrival = [] 

    # List of processes currently doing IO. Note that this list must be sorted
    # at all times
    ios = []

    # Current bursting process. If the CPU is idle, this variable is set to None
    bursting = None

    # Indicates whether the CPU is doing the first half of the context switch
    switch_in = False

    # Indicates whether the CPU is doing the second half of the context switch
    switch_out = False

    # Preparation counter for context switch. If preparation == 0, context
    # switch is done
    preparation = tcs

    # The process that's going to IO. After a process ends its CPU burst, it's
    # "going" to IO, but it only actually goes to IO after the context switch
    # is done
    to_io = None

    # List of burst times to calculate the metrics
    burst_time = []

################################## Overhead ####################################

    print('time 0ms: Simulator started for SJF', queue)

    # Put all processes to either the queue (if arrival time is 0) or the
    # pre_arrival list
    for p in processes:
        if p.arrival == 0:
            p.tau=int(1/lamb)
            queue.push((p.tau,p))
            print('time {}ms: Process {} (tau {}ms) arrived; placed on ready queue'.format(clock, p.name,p.tau), queue)
        else:
            pre_arrival.append(p)

    # Select a process to burst if the queue is not empty
    if len(queue) != 0:
        bursting = queue.pop()[1]
        p.wait.append(0)
        switch_in = True
        preparation = tcs - 1

################################# Simulation ###################################

    while (True):
        """
        The workflow:
        1. taking out a process from bursting
        2. add a new process to burst
        3. check for any completed IO
        4. check for any process arrival

        For ties in any of the above events, break with names in alphabetical
        order, i.e. Process A is should finish IO ahead of Process B
        """
        
        # Increment time first
        clock += 1

        # Do a CPU burst
        if bursting != None and (not switch_in):
            bursting.timelist[0] -= 1
            bursting.cpu_time += 1
            burst_time[-1] += 1
            
            # If a process finished bursting, check if the process is
            # terminating. If not, put it to IO. Also turns on context switches.
            if bursting.timelist[0] == 0:
                bursting.timelist.pop(0)
                bursting.num_bursts -= 1
                if bursting.num_bursts == 0:
                    print('time {}ms: Process {} terminated'.format(clock, bursting.name), queue)
                else:
                    s = 's'
                    if bursting.num_bursts == 1:
                        s = ''
                    new_tau = tau_function(bursting,alpha)
                    if clock < 1000 or not __debug__:
                        print('time {}ms: Process {} (tau {}ms) completed a CPU burst; {} burst{} to go'.format(clock, bursting.name, bursting.tau,bursting.num_bursts, s), queue)
                        print('time {}ms: Recalculated tau ({}ms) for process {}'.format(clock,new_tau,bursting.name),queue)
                        print('time {}ms: Process {} switching out of CPU; will block on I/O until time {}ms'.format(clock, bursting.name, clock + bursting.timelist[0] + tcs), queue)
                    bursting.tau=new_tau
                    to_io = bursting
                switch_out = True
                bursting.cpu_time = 0
                preparation = tcs + 1
                bursting = None

        # Doing context switch and if context switch done, put a process into
        # bursting
        if switch_in:
            if preparation != 0:
                preparation -= 1
            else:
                switch_in = False
                burst_time.append(0)
                if clock < 1000 or not __debug__:
                    print('time {}ms: Process {} (tau {}ms) started using the CPU for {}ms burst'.format(clock,bursting.name,bursting.tau, bursting.timelist[0]), queue)
        
        # Do IO for each process and check if any process completed IO. Note
        # that the IO list must always be in alphabetical order
        remove = []
        for p in ios:
            p.timelist[0] -= 1
            if p.timelist[0] == 0:
                p.timelist.pop(0)
                queue.push((p.tau,p))
                p.wait.append(0)
                remove.append(p)
                if clock < 1000 or not __debug__:
                    print('time {}ms: Process {} (tau {}ms) completed I/O; placed on ready queue'.format(clock, p.name,p.tau), queue)
        for p in remove:
            ios.remove(p)
        ios.sort()

        # Decrement arrival time and check if any process arrives
        remove.clear()
        for p in pre_arrival:
            p.arrival -= 1
            if p.arrival == 0:
                p.tau=int(1/lamb)
                queue.push((p.tau,p))
                p.wait.append(0)
                remove.append(p)
                if clock < 1000 or not __debug__:
                    print('time {}ms: Process {} (tau {}ms) arrived; placed on ready queue'.format(clock, p.name,p.tau), queue)
        for p in remove:
            pre_arrival.remove(p)

        # Doing switch out. If done, put a process into IO.
        if switch_out:
            preparation -= 1
            if preparation == 0:
                switch_out = False
                if to_io != None:
                    ios.append(to_io)
                    ios.sort()
                to_io = None

        # If the CPU is idle and the queue is not empty, pop the queue and start
        # switching in
        if bursting == None and len(queue) != 0 and (not switch_out) and (not switch_in):
            bursting = queue.pop()[1]
            switch_in = True
            preparation = tcs - 1

        # For each process that's still in the queue, increment its wait time
        # for metrics calculation
        for p in queue:
            p[1].wait[-1] += 1

        # If there isn't a process anywhere, break the simulation, and directly
        # add tcs to the clock to account for the final context switch
        if len(pre_arrival) == 0 and len(ios) == 0 and bursting == None and len(queue) == 0 and to_io == None:
            print('time {}ms: Simulator ended for SJF'.format(clock + tcs), queue,'\n')
            break

############################# metrics calculation ##############################

    # Calculate average burst time
    avg_burst = sum(burst_time) / len(burst_time)

    # Calculate average wait time by appending all wait times from all processes
    # together, then get the average
    avg_wait = []
    for p in processes:
        avg_wait += p.wait
    avg_wait = sum(avg_wait) / len(avg_wait)

    # Create the metrics data. 
    # Note that avg_turnaround = avg_burst + avg_wait + tcs * 2
    # Here FCFS doesn't have preemptions.
    data = 'Algorithm SJF\n' + \
           '-- average CPU burst time: {:.3f} ms\n'.format(avg_burst) + \
           '-- average wait time: {:.3f} ms\n'.format(avg_wait) + \
           '-- average turnaround time: {:.3f} ms\n'.format(avg_burst + avg_wait + tcs * 2) + \
           '-- total number of context switches: {}\n'.format(len(burst_time)) + \
           '-- total number of preemptions: 0\n' + \
           '-- CPU utilization: {:.3f}%\n'.format(sum(burst_time) / (clock + tcs) * 100)
    simout.write(data)

def SRT(processes, tcs, simout,lamb,alpha):
    """
    The SRT algorithm
    @param processes: list of processes to be scheduled
    @param tcs: time required to perform **HALF** context switches, i.e. time
    needed to for either switching in or switching out
    @param simout: the out file object
    """

    # print all processes
    for p in processes:
        s = 's'
        if p.num_bursts == 1:
            s = ''
        print('Process', p.name, '[NEW] (arrival time', p.arrival, 'ms)', p.num_bursts, 'CPU burst{} (tau {}ms)'.format(s,int(1/lamb)))

########################## Variable Initialization #############################

    # clock for counting time
    clock = 0 

    # queue of FCFS, could be changed to accommodate priority queue
    queue = Queue('pq')

    # List of processes before arrival
    pre_arrival = [] 

    # List of processes currently doing IO. Note that this list must be sorted
    # at all times
    ios = []

    # Current bursting process. If the CPU is idle, this variable is set to None
    bursting = None

    # Indicates whether the CPU is doing the first half of the context switch
    switch_in = False

    # Indicates whether the CPU is doing the second half of the context switch
    switch_out = False

    # Preparation counter for context switch. If preparation == 0, context
    # switch is done
    preparation = tcs

    # The process that's going to IO. After a process ends its CPU burst, it's
    # "going" to IO, but it only actually goes to IO after the context switch
    # is done
    to_io = None

    # List of burst times to calculate the metrics
    burst_time = []
    
    burst_number = 0
################################## Overhead ####################################

    print('time 0ms: Simulator started for SRT', queue)

    # Put all processes to either the queue (if arrival time is 0) or the
    # pre_arrival list
    for p in processes:
        if p.arrival == 0:
            p.tau=int(1/lamb)
            queue.push((p.tau,p))
            print('time {}ms: Process {} (tau {}ms) arrived; placed on ready queue'.format(clock, p.name,p.tau), queue)
        else:
            pre_arrival.append(p)
    # Find the burst number in total
    for p in processes:
        burst_number += p.num_bursts
    # Select a process to burst if the queue is not empty
    if len(queue) != 0:
        bursting = queue.pop()[1]
        p.wait.append(0)
        switch_in = True
        preparation = tcs - 1

################################# Simulation ###################################
    preemption = 0

    preempt_flag = False

    finished_io = None
    while (True):
        """
        The workflow:
        1. taking out a process from bursting
        2. add a new process to burst
        3. check for any completed IO
        4. check for any process arrival

        For ties in any of the above events, break with names in alphabetical
        order, i.e. Process A is should finish IO ahead of Process B
        """
        
        # Increment time first
        clock += 1
        # Do a CPU burst
        if bursting != None and (not switch_in):
            bursting.timelist[0] -= 1
            bursting.cpu_time += 1
            burst_time[-1] += 1
            
            # If a process finished bursting, check if the process is
            # terminating. If not, put it to IO. Also turns on context switches.
            if bursting.timelist[0] == 0:
                bursting.timelist.pop(0)
                bursting.num_bursts -= 1
                if bursting.num_bursts == 0:
                    print('time {}ms: Process {} terminated'.format(clock, bursting.name), queue)
                else:
                    s = 's'
                    if bursting.num_bursts == 1:
                        s = ''
                    new_tau=tau_function(bursting,alpha)
                    if clock < 1000 or not __debug__:
                        print('time {}ms: Process {} (tau {}ms) completed a CPU burst; {} burst{} to go'.format(clock, bursting.name, bursting.tau,bursting.num_bursts, s), queue)
                        print('time {}ms: Recalculated tau ({}ms) for process {}'.format(clock,new_tau,bursting.name),queue)
                        print('time {}ms: Process {} switching out of CPU; will block on I/O until time {}ms'.format(clock, bursting.name, clock + bursting.timelist[0] + tcs), queue)
                    bursting.tau = new_tau
                    to_io = bursting
                switch_out = True
                bursting.cpu_time=0
                preparation = tcs + 1
                bursting = None

        # Doing context switch and if context switch done, put a process into
        # bursting
        if switch_in:
            if preparation != 0:
                preparation -= 1
            else:
                switch_in = False
                burst_time.append(0)
                if clock < 1000 or not __debug__:
                    print('time {}ms: Process {} (tau {}ms) started using the CPU with {}ms burst remaining'.format(clock,bursting.name,bursting.tau, bursting.timelist[0]), queue)
                if (finished_io):
                    if (bursting.tau-bursting.cpu_time>finished_io.tau):
                        if clock<1000 or not __debug__:
                            print('time {}ms: Process {} (tau {}ms) will preempt {}'.format(clock,finished_io.name,finished_io.tau,bursting.name),queue)
                        preemption +=1
                        switch_out = True
                        preparation = tcs + 1
                        to_io=bursting
                        preempt_flag = True
                        bursting = None
                finished_io = None
        
        #push the preempt process in
        if switch_out:
            if ((preparation-1)==0 and (preempt_flag)):
                switch_out=False
                preempt_flag=False
                queue.push((to_io.tau-to_io.cpu_time,to_io))
                to_io=None

        # Do IO for each process and check if any process completed IO. Note
        # that the IO list must always be in alphabetical order
        remove = []
        for p in ios:
            p.timelist[0] -= 1
            if p.timelist[0] == 0:
                p.timelist.pop(0)
                queue.push((p.tau,p))
                p.wait.append(0)
                remove.append(p)
                if (not(bursting==None) and not switch_in):
                    if (bursting.tau-bursting.cpu_time>p.tau):
                        if clock<1000 or not __debug__:
                            print('time {}ms: Process {} (tau {}ms) completed I/O; preempting {}'.format(clock,p.name,p.tau,bursting.name),queue)
                        preemption +=1
                        switch_out = True
                        preparation = tcs + 1
                        to_io=bursting
                        preempt_flag = True
                        bursting = None
                    else:
                        if clock < 1000 or not __debug__:
                            print('time {}ms: Process {} (tau {}ms) completed I/O; placed on ready queue'.format(clock, p.name,p.tau), queue)
                else:
                    if (switch_in):
                        finished_io = p
                    if clock < 1000 or not __debug__:
                        print('time {}ms: Process {} (tau {}ms) completed I/O; placed on ready queue'.format(clock, p.name,p.tau), queue)
        for p in remove:
            ios.remove(p)
        ios.sort()

        # Decrement arrival time and check if any process arrives
        remove.clear()
        for p in pre_arrival:
            p.arrival -= 1
            if p.arrival == 0:
                p.tau=int(1/lamb)
                queue.push((p.tau,p))
                p.wait.append(0)
                remove.append(p)
                if clock < 1000 or not __debug__:
                    print('time {}ms: Process {} (tau {}ms) arrived; placed on ready queue'.format(clock, p.name,p.tau), queue)
        for p in remove:
            pre_arrival.remove(p)

        # Doing switch out. If done, put a process into IO.
        if switch_out:
            preparation -= 1
            if preparation == 0:
                switch_out = False
                if to_io != None:
                    ios.append(to_io)
                    ios.sort()
                to_io = None

        # If the CPU is idle and the queue is not empty, pop the queue and start
        # switching in
        if bursting == None and len(queue) != 0 and (not switch_out) and (not switch_in):
            bursting = queue.pop()[1]
            switch_in = True
            preparation = tcs - 1

        # For each process that's still in the queue, increment its wait time
        # for metrics calculation
        for p in queue:
            p[1].wait[-1] += 1

        # If there isn't a process anywhere, break the simulation, and directly
        # add tcs to the clock to account for the final context switch
        if len(pre_arrival) == 0 and len(ios) == 0 and bursting == None and len(queue) == 0 and to_io == None:
            print('time {}ms: Simulator ended for SRT'.format(clock + tcs), queue,'\n')
            break

############################# metrics calculation ##############################

    # Calculate average burst time
    avg_burst = sum(burst_time) / burst_number

    # Calculate average wait time by appending all wait times from all processes
    # together, then get the average
    avg_wait = []
    for p in processes:
        avg_wait += p.wait
    avg_wait = sum(avg_wait) / len(avg_wait)

    # Create the metrics data. 
    # Note that avg_turnaround = avg_burst + avg_wait + tcs * 2
    # Here FCFS doesn't have preemptions.
    data = 'Algorithm SRT\n' + \
           '-- average CPU burst time: {:.3f} ms\n'.format(avg_burst) + \
           '-- average wait time: {:.3f} ms\n'.format(avg_wait) + \
           '-- average turnaround time: {:.3f} ms\n'.format(avg_burst + avg_wait + (len(burst_time))*tcs * 2/(burst_number)) + \
           '-- total number of context switches: {}\n'.format(len(burst_time)) + \
           '-- total number of preemptions: {}\n'.format(preemption) + \
           '-- CPU utilization: {:.3f}%\n'.format(sum(burst_time) / (clock + tcs) * 100)
    simout.write(data)


def RR(processes, tcs, simout,tslice,rradd):
    """
    The RR algorithm
    @param processes: list of processes to be scheduled
    @param tcs: time required to perform **HALF** context switches, i.e. time
    needed to for either switching in or switching out
    @param simout: the out file object
    """

    # print all processes
    for p in processes:
        s = 's'
        if p.num_bursts == 1:
            s = ''
        print('Process', p.name, '[NEW] (arrival time', p.arrival, 'ms)', p.num_bursts, 'CPU burst{}'.format(s))

########################## Variable Initialization #############################

    # clock for counting time
    clock = 0 

    # queue of RR, could be changed to accommodate priority queue
    if (rradd==Precedence.END): queue = Queue()
    else: queue=Queue('stack')

    # List of processes before arrival
    pre_arrival = [] 

    # List of processes currently doing IO. Note that this list must be sorted
    # at all times
    ios = []

    # Current bursting process. If the CPU is idle, this variable is set to None
    bursting = None

    # Indicates whether the CPU is doing the first half of the context switch
    switch_in = False

    # Indicates whether the CPU is doing the second half of the context switch
    switch_out = False

    # Preparation counter for context switch. If preparation == 0, context
    # switch is done
    preparation = tcs

    # The process that's going to IO. After a process ends its CPU burst, it's
    # "going" to IO, but it only actually goes to IO after the context switch
    # is done
    to_io = None

    # List of burst times to calculate the metrics
    burst_time = []

    #number of preemption
    preemption=0

    #flag to determine whether exit normally or preempted

    preempt_flag=False


    burst_number=0

    preced='END' if rradd==Precedence.END else 'BEGINNING'

################################## Overhead ####################################

    print('time 0ms: Simulator started for RR with time slice {}ms and rr_add to {}'.format(int(tslice),preced),queue)

    # Put all processes to either the queue (if arrival time is 0) or the
    # pre_arrival list
    for p in processes:
        if p.arrival == 0:
            queue.push(p)
            print('time {}ms: Process {} arrived; placed on ready queue'.format(clock, p.name), queue)
        else:
            pre_arrival.append(p)
    # Find the burst number in total
    for p in processes:
        burst_number += p.num_bursts
    # Select a process to burst if the queue is not empty
    if len(queue) != 0:
        bursting = queue.pop()
        p.wait.append(0)
        switch_in = True
        preparation = tcs - 1

################################# Simulation ###################################
    #ts is use to keep track of tslice
    ts=tslice

    while (True):
        """
        The workflow:
        1. taking out a process from bursting
        2. add a new process to burst
        3. check for any completed IO
        4. check for any process arrival
        For ties in any of the above events, break with names in alphabetical
        order, i.e. Process A is should finish IO ahead of Process B
        """
        
        # Increment time first
        clock += 1
        # Do a CPU burst
        if bursting != None and (not switch_in):
            bursting.timelist[0] -= 1
            bursting.cpu_time += 1
            burst_time[-1] += 1
            ts-=1
            # If a process finished bursting, check if the process is
            # terminating. If not, put it to IO. Also turns on context switches.
            if bursting.timelist[0] == 0:
                bursting.timelist.pop(0)
                bursting.num_bursts -= 1
                if bursting.num_bursts == 0:
                    print('time {}ms: Process {} terminated'.format(clock, bursting.name), queue)
                else:
                    s = 's'
                    if bursting.num_bursts == 1:
                        s = ''
                    if clock < 1000 or not __debug__:
                        print('time {}ms: Process {} completed a CPU burst; {} burst{} to go'.format(clock, bursting.name, bursting.num_bursts, s), queue)
                        print('time {}ms: Process {} switching out of CPU; will block on I/O until time {}ms'.format(clock, bursting.name, clock + bursting.timelist[0] + tcs), queue)
                    to_io = bursting
                switch_out = True
                bursting.cpu_time = 0
                preparation = tcs + 1
                bursting = None
            elif ts==0 and len(queue):
                if clock < 1000 or not __debug__:
                    print('time {}ms: Time slice expired; process {} preempted with {}ms to go'.format(clock,bursting.name,bursting.timelist[0]),queue)
                switch_out=True
                preparation = tcs + 1
                to_io=bursting
                bursting=None
                preemption += 1
                preempt_flag=True
            elif ts==0 and len(queue)==0:
                ts=tslice

        # Doing context switch and if context switch done, put a process into
        # bursting
        if switch_in:
            if preparation != 0:
                preparation -= 1
            else:
                switch_in = False
                burst_time.append(0)
                if clock < 1000 or not __debug__:
                    if (bursting.cpu_time == 0):
                        print('time {}ms: Process {} started using the CPU for {}ms burst'.format(clock, bursting.name, bursting.timelist[0]), queue)
                    else:
                        print('time {}ms: Process {} started using the CPU with {}ms burst remaining'.format(clock,bursting.name,bursting.timelist[0]),queue)
        
        #push the preempt process in
        if switch_out:
            if ((preparation-1)==0 and (preempt_flag)):
                switch_out=False
                preempt_flag=False
                queue.push(to_io)
                to_io=None
                ts=tslice

        # Do IO for each process and check if any process completed IO. Note
        # that the IO list must always be in alphabetical order
        remove = []
        for p in ios:
            p.timelist[0] -= 1
            if p.timelist[0] == 0:
                p.timelist.pop(0)
                queue.push(p)
                p.wait.append(0)
                remove.append(p)
                if clock < 1000 or not __debug__:
                    print('time {}ms: Process {} completed I/O; placed on ready queue'.format(clock, p.name), queue)
        for p in remove:
            ios.remove(p)
        ios.sort()

        # Decrement arrival time and check if any process arrives
        remove.clear()
        for p in pre_arrival:
            p.arrival -= 1
            if p.arrival == 0:
                queue.push(p)
                p.wait.append(0)
                remove.append(p)
                if clock < 1000 or not __debug__:
                    print('time {}ms: Process {} arrived; placed on ready queue'.format(clock, p.name), queue)
        for p in remove:
            pre_arrival.remove(p)

        # Doing switch out. If done, put a process into IO.
        if switch_out:
            preparation -= 1
            if preparation == 0:
                switch_out = False
                if to_io != None:
                    ios.append(to_io)
                    ios.sort()
                to_io = None
                ts=tslice

        # If the CPU is idle and the queue is not empty, pop the queue and start
        # switching in
        if bursting == None and len(queue) != 0 and (not switch_out) and (not switch_in):
            bursting = queue.pop()
            switch_in = True
            preparation = tcs - 1

        # For each process that's still in the queue, increment its wait time
        # for metrics calculation
        for p in queue:
            p.wait[-1] += 1

        # If there isn't a process anywhere, break the simulation, and directly
        # add tcs to the clock to account for the final context switch
        if len(pre_arrival) == 0 and len(ios) == 0 and bursting == None and len(queue) == 0 and to_io == None:
            print('time {}ms: Simulator ended for RR'.format(clock + tcs), queue,'\n')
            break

############################# metrics calculation ##############################

    # Calculate average burst time

    avg_burst = sum(burst_time) / burst_number

    # Calculate average wait time by appending all wait times from all processes
    # together, then get the average
    avg_wait = []
    for p in processes:
        avg_wait += p.wait
    avg_wait = sum(avg_wait) / len(avg_wait)

    # Create the metrics data. 
    # Note that avg_turnaround = avg_burst + avg_wait + tcs * 2
    # Here FCFS doesn't have preemptions.
    data = 'Algorithm RR\n' + \
           '-- average CPU burst time: {:.3f} ms\n'.format(avg_burst) + \
           '-- average wait time: {:.3f} ms\n'.format(avg_wait) + \
           '-- average turnaround time: {:.3f} ms\n'.format(avg_burst + avg_wait + (len(burst_time))*tcs * 2/(burst_number)) + \
           '-- total number of context switches: {}\n'.format(len(burst_time)) + \
           '-- total number of preemptions: {}\n'.format(preemption) + \
           '-- CPU utilization: {:.3f}%\n'.format(sum(burst_time) / (clock + tcs) * 100)
    simout.write(data)

def main(args):
    
    # 48-bit random number generator
    rand = Rand48(args.seed, args.Lambda, args.max)

    # Processes created using the random number generator
    processes = create_processes(rand, args.n,1/args.Lambda)

    # metrics out file
    simout = open('simout.txt', 'w')

    # Note that we use a copy of the processes generated, so we don't need to
    # generate the processes again. We divide tcs by 2 to indicate half of the 
    # context switch time
    FCFS(copy.deepcopy(processes), args.tcs // 2, simout)
    SJF(copy.deepcopy(processes), args.tcs // 2, simout,args.Lambda,args.alpha)
    SRT(copy.deepcopy(processes),args.tcs // 2, simout, args.Lambda,args.alpha)
    RR(copy.deepcopy(processes),args.tcs // 2, simout, args.tslice,args.rradd)

if __name__ == '__main__':
    main(parsing())