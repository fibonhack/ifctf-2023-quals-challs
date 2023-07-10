#!/usr/bin/env python3
from pwn import args, process, connect, context, logging
from pathlib import Path
from os import environ


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


def start(io=None):
    if io is not None:
        io.close()

    if args['REMOTE']:
        io = connect(args["HOST"], args["PORT"])
        do_pow(io)
    else:
        scriptname = Path(__file__).parent.parent / "dist" / "chall.py"
        io = process(["python3", str(scriptname)])
    return io


def change(vals, plain: str, target: str, pos=-1):
    ret = []
    if pos not in range(16):
        for v, o, r in zip(vals, plain, target):
            a = v ^ ord(o) ^ ord(r)
            ret.append(a)
    else:
        for i in range(16):
            if i == pos:
                a = vals[i] ^ ord(plain) ^ ord(target)
                ret.append(a)
            else:
                ret.append(vals[i])
    return bytes(ret)


def change2(vals, plain, target, pos=-1):
    ret = []
    if pos not in range(16):
        for v, o, r in zip(vals, plain, target):
            a = v ^ o ^ r
            ret.append(a)
    else:
        for i in range(16):
            if i == pos:
                a = vals[i] ^ plain ^ target
                ret.append(a)
            else:
                ret.append(vals[i])
    return bytes(ret)


def encrypt(io, name: bytes):
    io.recvuntil(b"cmd: ")
    io.sendline(b"encrypt")
    io.recvuntil(b"name: ")
    io.sendline(name)
    _ = io.recvuntil(b"tag: ")
    tag = bytes.fromhex(io.recvuntil(b"\n", drop=True).decode())
    return tag


def check(io, tag: bytes, iv: bytes):
    io.recvuntil(b"cmd: ")
    io.sendline(b"check")
    io.recvuntil(b"tag: ")
    io.sendline(tag.hex().encode())
    io.recvuntil(b"iv: ")
    io.sendline(iv.hex().encode())
    p = io.recvuntil((b"tag: ", b"encrypt or check"))
    if b"encrypt or check" in p:
        return None
    # print(p)
    tag = bytes.fromhex(io.recvuntil(b"\n", drop=True).decode())
    return tag


def test_check(io, tag, iv):
    try:
        tag = check(io, tag, iv)
        return tag
    except KeyboardInterrupt:
        exit(2)
    except Exception:
        io.close()
        io = start(io)
        tag = check(io, tag, iv)
        return tag


def oracle_read_single(io, tag, iv, pos, seq=""):
    new_possible = []
    for a in "0123456789":
        iv2 = change(iv, a, " ", pos)
        tag2 = test_check(io, tag, iv2)
        if tag2 is not None:
            new_possible.append((iv2, tag2, seq+a))
    return new_possible


def oracle_read(io, tag, iv, start=0):
    # find next space
    last_possible = [(iv, tag, "")]
    second = False
    while True:
        iv = last_possible[0][0]
        tag = last_possible[0][1]
        seq = last_possible[0][2]
        # if seq != "":
        #     print(print("".join([chr(int(b)) for b in seq.split(",")])))
        first = 0
        space = False
        for i in range(second*3, 5):
            # print(i)
            num = 0
            for j, a in enumerate("0123456789"):
                iv2 = change(iv, a, " ", i)
                if test_check(io, tag, iv2):
                    num += 1
            # print(num)
            if num == 0:
                if first == 0:
                    first = i
            if num == 10:
                space = True
                break
            # else:
            #     print("comma or digit")

        if space:
            pass
            # print("found space at", i)
        else:
            i = first
            # print("starting padding in pos", i)

        pos = i
        if space:
            pos = i-1  # skip comma
        # pos is a space
        # pos-1 is a comma
        # 0-(pos-2) are digits
        seq2 = seq if seq == "" else seq+", "
        last_possible = [(iv, tag, seq2)]
        new_possible = []
        for i in range(pos):
            # print("try:", i)
            for iv2, tag2, seq in last_possible:
                if space and (i == pos-1):
                    # print("last digit")
                    iv2 = change(iv2, ",", " ", i+1)

                new_possible = oracle_read_single(io, tag, iv2, i, seq)
                if new_possible != []:
                    # print("success")
                    # print(new_possible)
                    break
                else:
                    continue
            last_possible = new_possible
        # print(last_possible)
        second = True
        if last_possible == []:
            # last character is lost (is recoverable but it does not matter)
            return seq

# pos should point to a space
# seq should be a list of numbers


def pump(io, tag, iv, pos, seq):
    for s in seq[::-1]:
        # insert future comma
        iv = change(iv, " ", "1", pos)
        tag = check(io, tag, iv)

        # insert future digit
        iv = change(iv, " ", "1", pos)
        tag = check(io, tag, iv)

        # insert comma
        iv = change(iv, "1", ",", pos+2)
        tag = check(io, tag, iv)

        for i in range(len(str(s))-1):
            # insert future digit
            iv = change(iv, " ", "1", pos)
            tag = check(io, tag, iv)

        # insert digits
        for i, a in enumerate(str(s)):
            iv = change(iv, "1", a, pos+i+1)
            tag = check(io, tag, iv)

    return tag, iv


def main():
    environ['PWNLIB_NOTERM'] = 'True'
    logging.disable()

    io = start()

    # 110, 97, 109, 10
    # 1, 58, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97

    tag = encrypt(io, b"a")
    # print(len(tag))
    context.log_level = 'ERROR'

    # 0x110000 max

    seq = [ord(a) for a in "name:admin,cmd:getflag,psw:superpassword"[:-1]]
    iv = tag[:16]
    tag = tag[16:]

    # delete first 2 characters "1,"
    iv = change(iv, "1", " ", 0)
    iv = change(iv, ",", " ", 1)
    tag = check(io, tag, iv)
    # delete 3 characters "58,"
    # replace 2 characters "97" with "d"
    iv = change(iv, "5", "1", 0)
    iv = change(iv, "8", ",", 1)
    iv = change(iv, ",", " ", 2)
    iv = change(iv, " ", str(ord("d"))[0], 3)
    iv = change(iv, "9", str(ord("d"))[1], 4)
    iv = change(iv, "7", str(ord("d"))[2], 5)
    tag = check(io, tag, iv)
    tag, iv = pump(io, tag, iv, 2, seq)

    # delete first 2 characters "1,"
    iv = change(iv, "1", " ", 0)
    iv = change(iv, ",", " ", 1)
    tag = check(io, tag, iv)
    pos = (len(tag)-5*(60))//16
    iv = tag[16*(pos-1):16*pos]
    tag = tag[16*(pos):]
    tag = check(io, tag, iv)

    seq = oracle_read(io, tag, iv)
    flag = "".join([chr(int(b)) for b in seq.split(",")])+"}"
    if "ifctf{" not in flag:
        print("ERR - Flag not found")
        exit(1)
    print("OK - flag found")
    exit(0)


if __name__ == "__main__":
    main()
