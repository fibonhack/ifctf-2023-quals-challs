#!/usr/bin/env python3
import os
import pickle
import sys
from pwn import remote, xor, args


class Client(remote):

    def register(self) -> "tuple[bytes, list[str]]":
        self.sendlineafter(b"do? [1,2,3]: ", b"1")
        answers = [os.urandom(8).hex() for _ in range(8)]
        for i in range(8):
            self.sendlineafter(b"? ", answers[i].encode())
        self.recvuntil(b"Here is your login token: ")
        return bytes.fromhex(self.recvline().strip().decode()), answers

    def login(self, token: bytes) -> bytes:
        self.sendlineafter(b"do? [1,2,3]: ", b"2")
        self.sendlineafter(b"token: ", token.hex().encode())
        resp = self.recvline()
        return resp


def main(host: str, port: int):

    c = Client(host, port, level="critical")
    token, answers = c.register()

    iv, b0, *bs = [token[i: i + 16] for i in range(0, len(token), 16)]

    payload = pickle.dumps(
        (None, None, None, None, None, None, None, None, 1), 0)
    assert len(payload) == 17

    b0_plaintext = pickle.dumps((*answers, False))

    new_iv = xor(iv, b0_plaintext, payload, cut="min")

    while True:
        new_token = new_iv + b0 + os.urandom(16)
        resp = c.login(new_token)
        if b"flag" in resp:
            print("OK - flag found")
            exit(0)

    print("ERR - flag not found")
    exit(1)


if __name__ == "__main__":
    main(args["HOST"], int(args["PORT"]))
