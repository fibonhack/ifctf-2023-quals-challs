#!/usr/bin/env python3
from pwn import remote, args, logging
from Crypto.Util.number import bytes_to_long, long_to_bytes
from math import prod
import sys


def main():
    logging.disable()
    pyscript = b"\nprint(*open('flag.txt'))#1337"
    assert len(pyscript) == 30
    n = bytes_to_long(pyscript)
    e = 5
    factors = [
        47,
        7105738723,
        619270185563,
        348370083718991636917731952656327698359955621449,
    ]
    assert prod(factors) == n

    # useful links:
    # - https://github.com/wiml/derlite
    data = []
    data.append(0x30)  # magic number (TAG for constructed sequence)
    data.extend(b"#")  # total length (after this) = 35

    data.append(0x02)  # integer N, remaining lenght 34
    data.append(30)  # length of integer = 30, remaining length 33
    data.extend(pyscript)  # payload, remaining length 3

    data.append(0x02)  # integer E, remaining lenght 2
    data.append(0x01)  # length of integer = 1, remaining length 1
    data.append(e)  # value of integer

    assert len(data) == 35 + 2
    payload = bytes(data)

    r = remote(args["HOST"], int(args["PORT"]))
    r.sendlineafter(b"Send me your script: ", payload.hex().encode())
    r.sendlineafter(b"Send me your public key: ", b"00")
    r.recvuntil(b"Here is your encrypted output: \n")
    res = bytes.fromhex(r.recvline(keepends=False).decode())

    c = bytes_to_long(res)
    phi = prod([p - 1 for p in factors])
    d = pow(e, -1, phi)
    m = pow(c, d, n)
    if "ifctf" in long_to_bytes(m).decode():
        print("OK - flag found")
        exit(0)
    print("ERR - flag not found")
    exit(1)


if __name__ == "__main__":
    main()
