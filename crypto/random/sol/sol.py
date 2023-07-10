#!/usr/bin/env python3
from pwn import process, remote, args, logging
from mersenne_partial_input import Untwister
from RecoverSeed import min_len_seed
from pathlib import Path
import signal
import string
import subprocess


def signal_handler(signum, frame):
    raise EOFError()


def do_pow(io):
    io.recvuntil(b"proof of work: ")
    data = io.recvline().split(b" -s ")[-1].decode()[:-1]
    # check that data is letter.base64.base64
    assert len(data.split(".")) == 3
    assert data.split(".")[0] in string.ascii_letters
    base64letters = string.ascii_letters + string.digits + "+/="
    assert all(d in base64letters for d in data.split(".")[1])
    assert all(d in base64letters for d in data.split(".")[2])
    # get pow by running "curl -sSfL https://pwn.red/pow | sh -s <data>"

    pow_file = Path(__file__).parent / "pow.sh"
    pow = subprocess.check_output(f"{pow_file} {data}", shell=True).strip()
    io.sendlineafter(b"solution: ", pow)


def start():
    if args['REMOTE']:
        io = remote(args["HOST"], args["PORT"])
        do_pow(io)
    else:
        scriptname = Path(__file__).parent.parent / "dist" / "chall.py"
        io = process(["python3", str(scriptname)])
    return io


def internal():
    import time
    # sTime = time.time()
    io = start()

    ut = Untwister()
    ut.submit("?"*32)
    for i in range(2000):
        bits = io.recvline()[:-1].decode()
        ut.submit(bits)

    seed = None
    m = 624
    
    try:
        signal.alarm(60)
        state, state_o = ut.get_state()
        seed_t = ut.get_seed_from_state(state_o, 624)
        m = min_len_seed(seed_t)
        signal.alarm(0)
        # print(f"m = {mm}")
        if m is not None:
            seed = ut.get_seed_from_state_reduced(state_o, m, seed_t)
            # print("seed found")
        else:
            return io
    except:
        return io
    
    if m >= 624//2 or seed is None:
        return io

    check = ut.get_random_from_state(state_o).getrandbits(32)
    io.sendlineafter(b"Enter first 32 bits generated", str(check).encode())
    io.recvline()
    assert io.recvline() == b"Correct\n"

    seed = sum([a*2**(32*i) for i, a in enumerate(seed)])
    io.sendlineafter(b"Enter the seed", hex(seed)[2:].encode())
    io.recvline()
    line = io.recvline()
    # print(line.decode())
    # endTime = time.time()
    # print(f"Time: {endTime-sTime}")
    if "You got it" in line.decode():
        line = io.recvline()
        if b"ifctf{" not in line:
            print("ERR - flag not found")
            exit(1)
        print("OK - found")
        exit(0)
    return io


def main():
    logging.disable()
    signal.signal(signal.SIGALRM, signal_handler)
    for _ in range(100):
        internal().close()
        print("retry")
    else:
        print("ERR - not found, too many tries")
        exit(1)


if __name__ == "__main__":
    main()
