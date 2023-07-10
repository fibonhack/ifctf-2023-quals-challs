from z3 import *
from itertools import count
from time import time
import logging

# author marcog

logger = logging.getLogger()


SYMBOLIC_COUNTER = count()

# find the reduced length of the seed (if any)
def min_len_seed(blocks):
    for i in range(1, 311):
        found = False
        for j in range(624//i):
            if blocks[i-1]-(i*j) != blocks[i*(j+1)-1]:
                found = True
        if not found:
            return i
    return None

# recover seed from MT19937 (only if int)
# maybe extend with bytes of given length?
class RecoverSeed:
    def __init__(self, blocks = 2, solver=None, last_known = None):
        name = next(SYMBOLIC_COUNTER)
        if solver is None:
            self.solver = Solver()
        else:
            self.solver = solver
        self.seed = [BitVec(f'seed_{name}_{i}', 32) for i in range(blocks)]
        if last_known is not None:
            for i in range(len(last_known)):
                self.solver.add(self.seed[-i] == last_known[-i])
        self.symbolic_seed(self.seed)

    def submit(self, state, n = 624):
        for i in range(n):
            self.solver.add(state[i] == self.MT[i])
        
        logger.debug('Solving...')
        start = time()
        logger.debug(self.solver.check())
        model = self.solver.model()
        end = time()
        logger.debug(f'Solved! (in {round(end-start,3)}s)')
        return [model[seed].as_long() for seed in self.seed]

    def submit_class(self, random, n = 624):
        return self.submit(random.getstate()[1][:n])

    def symbolic_seed(self, As, w=32):
        name = next(SYMBOLIC_COUNTER)
        bits = w

        keyused = len(As)
        # TODO: split a for generic bit length
        # split seed (a) in multiple 32 bit blocks ()
        init_key = [a for a in As]
       
        self.init_by_array(init_key)

    def init_genrand(self, num, n = 624, f = 1812433253, w = 32):
        """initialize the generator from a seed"""
        self.MT = []
        self.MT.append(num)
        for i in range(1, n):
            temp = f * (self.MT[i-1] ^ (self.MT[i-1] >> (w-2))) + i
            self.MT.append(temp & 0xffffffff)
        self.index = i+1

    def init_by_array(self, init_key, n = 624, g = 19650218, h = 1664525, u = 1566083941, w = 32, upper_mask=0x80000000):
        name = next(SYMBOLIC_COUNTER)
        self.state = []
    
        self.init_genrand(g)

        for i in range(n):
            gg = BitVec(f'MT_{i}_{name}', 32)
            self.solver.add(self.MT[i] == gg)
            self.MT[i] = gg

        k = max(n, len(init_key))
        i=1
        j=0
        for _ in range(k,0,-1):
            temp = (self.MT[i] ^ ((self.MT[i-1] ^ LShR(self.MT[i-1],(w-2))) * h)) + init_key[j] + j
            self.MT[i] = temp & 0xffffffff
            i+=1
            j+=1
            if i >= n:
                self.MT[0] = self.MT[n-1]
                i=1
            if j >= len(init_key):
                j=0
        for _ in range(n-1, 0, -1):
            temp = (self.MT[i] ^ ((self.MT[i-1] ^ LShR(self.MT[i-1],(w-2))) * u)) - i
            self.MT[i] = temp & 0xffffffff
            i+=1
            if i >= n:
                self.MT[0] = self.MT[n-1]
                i=1
        self.MT[0] = upper_mask