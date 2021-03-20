class Queue(list):
    """
    A Queue class that inherits from list class. Overrides the __str__ method
    for easier printing
    """

    def __str__(self):
        if len(self) == 0:
            return '[Q <empty>]'
        s = '[Q'
        for x in self:
            s += ' ' + str(x)
        return s + ']'