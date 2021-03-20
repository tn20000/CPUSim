import heapq

class Queue():
    """
    A Queue class that has a mode for different types of queue. Overrides 
    multiple methods for easier use. Note that if you're using a priority queue,
    push a tuple instead of just the Process, i.e., push((priority, Process))
    instead of push(Process).
    """

    def __init__(self, mode='queue'):
        """
        @param mode: 'queue' for FIFO queue, 'pq' for priority queue, 'stack'
        for LIFO queue (used in RR when rradd is Precedence.BEGINNING)
        """
        self.mode = mode
        self.container = []

    def push(self, obj):
        """
        A push method to push an object into the queue. Note that when using
        priority queue you should push a tuple of (priority, object) instead of
        just the object
        @param obj: the object to be pushed into the queue
        """
        if self.mode == 'queue' or self.mode == 'stack':
            self.container.append(obj)
        elif self.mode == 'pq':
            heapq.heappush(self.container, obj)
    
    def pop(self):
        """
        A pop method to return the appropriate element according to the type of
        the queue.
        @return obj: object that is popped from the queue
        """
        if self.mode == 'queue':
            return self.container.pop(0)
        if self.mode == 'pq':
            return heapq.heappop(self.container)
        if self.mode == 'stack':
            return self.container.pop()

    def __str__(self):
        """
        Method to print the queue
        @return str: the string representation of the queue
        """
        if len(self) == 0:
            return '[Q <empty>]'
        s = '[Q'
        for x in self:
            if self.mode == 'queue' or self.mode == 'stack':
                s += ' ' + str(x)
            elif self.mode == 'pq':
                s += ' ' + str(x[1])
        return s + ']'

    def __len__(self):
        """
        Method to get the length of the queue
        @return len: length of the queue
        """
        return len(self.container)

    def __iter__(self):
        """
        Method to enable iteration of the queue
        @return iter: an iterator of the queue.
        """
        return iter(self.container)
