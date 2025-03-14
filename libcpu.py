""" test libcpu """
from random import randint


class DRCv2System():
    """ doc """
    def __init__(self):
        self.program_counter = 0
        self.word_size = 8
        self.alu = ALU(self.word_size)
        self.program = []
        self.registers = [0]
        self.status_reg = {}
        self.devices = []
        self.initialise_regs()
        self.initialise_devices()
        self.last_written = None
        self.ign_wait = False

    def initialise_devices(self):
        """ doc """
        for i in range(64):
            self.devices.append(Device(f"dev{i}", False, None))

        self.devices[40] = Rng()
        self.devices[2] = Console()

        for i in range(64, 256):
            self.devices.append(Device(f"RAM cell {i-64}", False, None))

    def initialise_regs(self):
        """ doc """
        i = 1
        while i < 8:
            self.registers.append(None)
            i += 1
        self.registers[7] = 0
        self.status_reg = {"halt_bit": False,
                           "carry_flag": None, "zero_flag": None, "wait_bit": False}

    def load_rom(self, filename):
        """ doc """
        try:
            self.program = load_program(self.word_size, filename)
        except FileNotFoundError:
            print(f"File {filename} not found!")

    def get_next_state(self):
        """ doc """
        self.registers[0] = 0
        instruction = self.program[self.program_counter]
        self.last_written = None

        if self.status_reg["wait_bit"] == True:
            return


        opcode = instruction["opcode"]
        dest = int(instruction["dest_reg"])
        src_a = int(instruction["src_a_reg"])
        src_b = int(instruction["src_b_reg"])
        imm = int(instruction["immediate"])
        cnd = instruction["condition"]

        if opcode == "MSC" and cnd == "1":
            self.status_reg["halt_bit"] = True

        elif opcode == "ADD":
            rslt = self.alu.add_(self.registers[src_a], imm | self.registers[src_b])
            self.registers[dest] = rslt[0]
            self.status_reg["carry_flag"] = rslt[1]
            self.status_reg["zero_flag"] = rslt[2]

        elif opcode == "SUB":
            rslt = self.alu.sub_(self.registers[src_a], imm | self.registers[src_b])
            self.registers[dest] = rslt[0]
            self.status_reg["carry_flag"] = rslt[1]
            self.status_reg["zero_flag"] = rslt[2]

        elif opcode == "RSH":
            result = self.alu.rsh_(self.registers[src_a])
            self.registers[dest] = result[0]
            self.status_reg["carry_flag"] = result[1]

        elif opcode == "INC":
            self.registers[dest] = self.alu.add_(self.registers[src_a], 1)[0]

        elif opcode == "DEC":
            self.registers[dest] = self.alu.sub_(self.registers[src_a], 1)[0]

        elif opcode == "NOR":
            self.registers[dest] = \
                self.alu.nor_(self.registers[src_a], imm | self.registers[src_b])

        elif opcode == "AND":
            self.registers[dest] = \
                self.alu.and_(self.registers[src_a], self.registers[src_b])

        elif opcode == "LOD":
            addr = imm | self.registers[src_b]
            if addr == 2 and not self.ign_wait:
                self.status_reg["wait_bit"] = True
                self.ign_wait = True
                return
            self.registers[dest] = \
                self.devices[addr].read()
            self.ign_wait = False



        elif opcode == "STR":
            addr = imm | self.registers[src_b]
            self.devices[addr].write(self.registers[src_a])
            self.last_written = addr

        elif opcode == "IMM":
            self.registers[dest] = imm

        elif opcode == "BRNCH":
            if eval_cond(cnd, self.status_reg):
                self.program_counter = imm | self.registers[src_b]
            else:
                self.program_counter += 1

        if self.status_reg["halt_bit"] is False and opcode != "BRNCH":
            self.program_counter += 1
        self.program_counter = self.program_counter % (2**self.word_size)
        self.registers[0] = 0


    def dump_all(self):
        """ Print debug info to console. """
        print(f"PC: {self.program_counter}")
        print(self.program[self.program_counter])
        print(self.status_reg)
        for reg in self.registers:
            print(reg)
        print()
        for dev in self.devices:
            print(dev)


def load_program(bits=8, filename="test.a"):
    """ d """
    with open(filename, "r") as infile:
        lines = []
        for line in infile:
            lines.append(line.strip())

        program = []
        for i in range(2**bits):
            empty_ins = {
                "opcode": "MSC",
                "dest_reg": 0,
                "src_a_reg": 0,
                "src_b_reg": 0,
                "immediate": 0,
                "condition": 0
            }
            program.append(empty_ins)
        for i in range(len(lines)):
            line = lines[i].split(" ")
            new_ins = {
                "opcode": line[0],
                "dest_reg": line[1],
                "src_a_reg": line[2],
                "src_b_reg": line[3],
                "immediate": line[4],
                "condition": line[5]
            }
            program[i] = new_ins
    return program


class Device():
    """ doc """
    def __init__(self, label="dev", ro=False, val=None):
        self.label = label
        self.readonly = ro
        self.val = val

    def __str__(self):
        return self.label + ", value=" + str(self.val)

    def write(self, new_val):
        """ doc """
        if not self.readonly:
            self.val = new_val

    def read(self):
        """ doc """
        return self.val


def truncate_numbers(data: int, word_length=8) -> int:
    """ doc """
    if data < 0:
        raise ValueError("This emulator does not \
support negative values:", data)
    if data >= 2**word_length:
        return data % (2**word_length)
    return data


class ALU():
    """ doc """
    def __init__(self, bits=8):
        self.bits = bits

    def add_(self, a, b):
        """ doc """
        carry, zero = False, False
        if a+b >= 2**self.bits:
            carry = True
        if a+b == 0:
            zero = True
        result = truncate_numbers(a + b)
        return result, carry, zero

    def sub_(self, a, b):
        """ doc """
        b = 2**self.bits - b
        carry, zero = False, False

        if a + b >= 2**self.bits:
            carry = True
        result = truncate_numbers(a+b, self.bits)
        if result == 0:
            zero = True
        return result, carry, zero

    def and_(self, a, b):
        """ doc """
        return a & b

    def nor_(self, a, b):
        """ doc """
        arg_a = str(bin(a))[2:].zfill(self.bits)
        arg_b = str(bin(b))[2:].zfill(self.bits)
        r = ""
        for i in range(self.bits):
            if arg_a[i] == "0" and arg_b[i] == "0":
                rslt += "1"
            else:
                rslt += "0"
        rslt = int(rslt, base=2)
        return r

    def rsh_(self, a):
        """ doc """
        carry = False
        if a % 2 != 0:
            carry = True

        return a//2, carry


def eval_cond(cnd: str, status_reg) -> bool:
    """ doc """
    zero = status_reg["zero_flag"]
    carry = status_reg["carry_flag"]
    return (cnd == "0")\
        or (cnd == "z" and zero)\
        or (cnd == "nz" and not zero)\
        or (cnd == "c" and carry)\
        or (cnd == "nc" and not carry)\
        or (cnd == "nc&nz" and not carry and not zero)\
        or (cnd == "c&z" and carry and zero)\
        or (cnd == "c&nz" and carry and not zero)


class Rng():
    """ doc """
    def __init__(self, label="RNG", bits=8):
        self.label = label
        self.bits = bits

    def __str__(self):
        return self.label + ", value=random :)"

    def write(self, new_val):
        """ doc """
        pass

    def read(self):
        """ doc """
        return randint(0, 2**self.bits-1)


class Console():
    """ doc """
    def __init__(self, label="Console", bits=8):
        self.buffer = [None]
        self.label = label
        self.bits = bits
        self.is_ready = False

    def __str__(self):
        return self.label + ": " + str(self.buffer[0])

    def read(self):
        """ doc """
        #  prompt = f"{self.label}: Type a number: "
        #  inp = input(prompt)
        #  inp = randint(0, 255) ######### TEMPORARY FIX!!!!!!
        #  from app import App
        #  inp = App.prompt()
        #  inp = int(inp) % 2**self.bits
        #  self.buffer.insert(0, inp)
        return self.buffer[0]

    def write(self, val):
        """ doc """
        self.buffer.insert(0, val)

    #  def dump_all(self):
        #  """ doc """
        #  for line in self.buffer:
            #  print(line)


# def dump_all_info():
    # global devices, pc, registers, status, program
    # print("executed:")
    # print(program[pc])
    # print("status reg:")
    # print(status)
    # print("devices:")
    # for dev in devices:
        # print(dev)
    # print("regs:")
    # for reg in registers:
        # print(reg)


# ADD
# SUB
# RSH
# INC
# DEC
# NOR
# AND
# LOD
# STR
# IMM
# MSC
# BRNCH
