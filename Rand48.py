import math

class Rand48:
    """
    Random number generator mimicking the 48-bit linear congruential algorithm
    in C
    """

    def __init__(self, seed, lam, tail):
        """
        @param seed: the seed required to initialized the random number
        generator
        @param lam: the lambda parameter for exponential distribution
        @param tail: the long tail parameter to cut off when generating
        exponential distribution
        """
        self.seed = seed
        self.X = (self.seed << 16) + 0x330E
        self.lam = lam
        self.tail = tail
    
    def drand48(self):
        """
        Method to generate uniform distribution between [0, 1)
        @return r: a random number between [0, 1)
        """
        self.X = (0x5DEECE66D * self.X + 0xB) % 2 ** 48
        return self.X / 2 ** 48
    
    def next_exp(self):
        """
        Method to generate an exponential distribution with the given lambda and
        tail parameters by -log(U(0, 1)) / lambda
        @return rt: random number generated from the exponential distribution
        """
        while (True):
            rt = -math.log(self.drand48()) / self.lam
            if rt <= self.tail:
                break
        return rt