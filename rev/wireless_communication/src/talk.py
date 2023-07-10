import serial
import time
from tqdm import tqdm

with open("text.txt", "rb") as f:
    data = f.read()

sent = ''
with serial.Serial('/dev/ttyACM0', 115200) as s:
    time.sleep(3)
    for i in tqdm(range(len(data))):
        c = bytes([data[i]])
        s.write(c)

        x = s.readline().decode()
        x = x.split(' ')
        x = int(x[0])
        sent += chr(x)

print(f"Correctly sent: {sent}")
