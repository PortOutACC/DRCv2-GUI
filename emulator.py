""" libcpu test """
from time import sleep
from libcpu import DRCv2System

sys0 = DRCv2System()

sys0.load_rom("programs/mod_calc.a")
#  sys0.load_rom("programs/test.a")

with open("programs/mod_calc.a", "r") as f:
    PROGRAM = []
    idx = 0
    for line in f:
        PROGRAM.append(f"{idx} " + line.strip())
        idx += 1

from os import system

while True:

    system("clear")

    sys0.dump_all()

    sys0.get_next_state()
    #  input()
    sleep(0.1)

    if sys0.status_reg["halt_bit"] == True:
        quit()


# Program printing
for line in PROGRAM:
    if int(line.split()[0]) == sys0.program_counter:
        print(line + "    <--")
    else:
        print(line)

# show console
print(sys0.devices[2].buffer[0])

# print registers
for i in range(len(sys0.registers)):
    print(f"register {i}: {sys0.registers[i]}")

# pritn core memory
for i in range(64, 96):
    print(sys0.devices[i].val)
