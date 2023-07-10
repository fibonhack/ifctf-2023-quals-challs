import numpy as np
from typing import List

sample_rate = 2e6
symbol_period = 200e-6
samples_per_symbol = int(sample_rate * symbol_period)
bytes_per_packet = 5
bits_per_packet = 8*bytes_per_packet

print(f"Sample rate: {sample_rate}")
print(f"Symbol period: {symbol_period}")
print(f"Samples per symbol: {samples_per_symbol}")

with open("output.bin", "rb") as f:
    raw_data = f.read()

data = np.array([x for x in raw_data])

print("Extracting bits")
symbols : List[int] = []
i = 0
while i < len(data):
    if data[i] == 0:
        i += 1
    else:
        slice = data[i : i + samples_per_symbol*5]
        avg = np.average(slice)
        symbols.append(1 if avg > 0.75 else 0)
        i += samples_per_symbol*5

bits = symbols

def pack(p):
    p = p[::-1]
    p = ''.join([str(x) for x in p])
    p = int(p, 2)
    return p

packets = [bits[i * bits_per_packet : (i+1) * bits_per_packet] for i in range(len(bits) // bits_per_packet)]

msg = ''
for p in packets:
    if p[:8] == [1, 0, 1, 0, 1, 0, 1, 0]:
        print('Valid packet:', end='')
        preamble = pack(p[:8])

        content = pack(p[8:16])

        zero = pack(p[16:24])

        src_l = pack(p[24:32])
        src_h = pack(p[32:40])

        print(f"{preamble:x} - {content:c} - {zero:x} from {src_h:x}{src_l:x}")

        msg += chr(content)
    else:
        print('Invalid packet')
    
print(msg)