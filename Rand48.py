import math

class Rand48:
    """
    Random number generator mimicking the 48-bit linear congruential algorithm
    in C
    """

    def __init__(self, seed, lam, tail):
        self.seed = seed
        self.X = (self.seed << 16) + 0x330E
        self.lam = lam
        self.tail = tail
    
    def drand48(self):
        self.X = (0x5DEECE66D * self.X + 0xB) % 2 ** 48
        return self.X / 2 ** 48
    
    def next_exp(self):
        while (True):
            rt = -math.log(self.drand48()) / self.lam
            if rt <= self.tail:
                break
        return rt