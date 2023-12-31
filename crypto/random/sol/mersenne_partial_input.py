from z3 import Solver, BitVec, LShR, If, Extract
from random import Random
from itertools import count
from time import time
import logging
import RecoverSeed


logger = logging.getLogger()


SYMBOLIC_COUNTER = count()

# modified Untwister from https://cor.team/posts/zh3r0-ctf-v2-twist_and_shout/
# to include seed recovery and other stuff
class Untwister:
    def __init__(self):
        name = next(SYMBOLIC_COUNTER)
        self.solver = Solver()
        self.MT = [BitVec(f'MT_{i}_{name}', 32) for i in range(624)]

        self.Original = self.MT
        self.index = 624

    # This particular method was adapted from https://www.schutzwerk.com/en/43/posts/attacking_a_random_number_generator/
    def symbolic_untamper(self, solver, y):
        name = next(SYMBOLIC_COUNTER)

        y1 = BitVec(f'y1_{name}', 32)
        y2 = BitVec(f'y2_{name}', 32)
        y3 = BitVec(f'y3_{name}', 32)
        y4 = BitVec(f'y4_{name}', 32)

        equations = [
            y2 == y1 ^ (LShR(y1, 11)),
            y3 == y2 ^ ((y2 << 7) & 0x9D2C5680),
            y4 == y3 ^ ((y3 << 15) & 0xEFC60000),
            y == y4 ^ (LShR(y4, 18))
        ]

        solver.add(equations)
        return y1

    def symbolic_twist(self, MT, n=624, upper_mask=0x80000000, lower_mask=0x7FFFFFFF, a=0x9908B0DF, m=397):
        '''
            This method models MT19937 function as a Z3 program
        '''
        MT = [i for i in MT]  # Just a shallow copy of the state

        for i in range(n):
            x = (MT[i] & upper_mask) + (MT[(i+1) % n] & lower_mask)
            xA = LShR(x, 1)
            # Possible Z3 optimization here by declaring auxiliary symbolic variables
            xB = If(x & 1 == 0, xA, xA ^ a)
            MT[i] = MT[(i + m) % n] ^ xB

        return MT

    def get_symbolic(self, guess):
        name = next(SYMBOLIC_COUNTER)
        ERROR = 'Must pass a string like "?1100???1001000??0?100?10??10010" where ? represents an unknown bit'

        assert type(guess) == str, ERROR
        assert all(map(lambda x: x in '01?', guess)), ERROR
        assert len(guess) <= 32, "One 32-bit number at a time please"
        guess = guess.zfill(32)

        self.symbolic_guess = BitVec(f'symbolic_guess_{name}', 32)
        guess = guess[::-1]

        for i, bit in enumerate(guess):
            if bit != '?':
                self.solver.add(Extract(i, i, self.symbolic_guess) == int(bit))

        return self.symbolic_guess

    def submit(self, guess):
        '''
            You need 624 numbers to completely clone the state.
                You can input less than that though and this will give you the best guess for the state
        '''
        if self.index >= 624:
            name = next(SYMBOLIC_COUNTER)
            next_mt = self.symbolic_twist(self.MT)
            self.MT = [BitVec(f'MT_{i}_{name}', 32) for i in range(624)]
            for i in range(624):
                self.solver.add(self.MT[i] == next_mt[i])
            self.index = 0

        symbolic_guess = self.get_symbolic(guess)
        symbolic_guess = self.symbolic_untamper(self.solver, symbolic_guess)
        self.solver.add(self.MT[self.index] == symbolic_guess)
        self.index += 1

    def get_seed(self, blocks, n=624):
        self.recover = RecoverSeed.RecoverSeed(blocks, self.solver)
        for i in range(n):
            self.solver.add(self.Original[i] == self.recover.MT[i])
        logger.debug('Solving...')
        start = time()
        logger.debug(self.solver.check())
        model = self.solver.model()
        end = time()
        logger.debug(f'Solved! (in {round(end-start,3)}s)')
        return [model[seed].as_long() for seed in self.recover.seed]

    def get_seed_from_state(self, state, blocks, n=624):
        recover = RecoverSeed.RecoverSeed(blocks)
        return recover.submit(state)

    def get_seed_from_state_reduced(self, state, blocks, seed_total, n=624):
        diff = seed_total[2]-seed_total[blocks+2]
        return [seed_total[blocks]+diff, seed_total[blocks+1]+diff] + seed_total[2:blocks]

    def get_state(self):

        logger.debug('Solving...')
        start = time()
        logger.debug(self.solver.check())
        model = self.solver.model()
        end = time()
        logger.debug(f'Solved! (in {round(end-start,3)}s)')

        state = list(map(lambda x: model[x].as_long(), self.MT))
        state_o = list(map(lambda x: model[x].as_long(), self.Original))
        return state, state_o

    def get_random(self):
        '''
            This will give you a random.Random() instance with the cloned state.
            And one with the original initial state.
        '''
        state, state_o = self.get_state()

        result_state = (3, tuple(state+[self.index]), None)
        r = Random()
        r.setstate(result_state)

        result_state_o = (3, tuple(state_o+[624]), None)
        r_o = Random()
        r_o.setstate(result_state_o)

        return r, r_o

    def get_random_from_state(self, state):
        '''
            This will give you a random.Random() instance with the cloned state.
            And one with the original initial state.
        '''

        result_state = (3, tuple(state+[624]), None)
        r = Random()
        r.setstate(result_state)

        return r
