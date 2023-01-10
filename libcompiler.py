""" Code library for DRC v.2 compiler. """


def load_file(filename: str) -> str:
    """ Load source code from file. """
    code_out = []
    try:
        with open(filename, "r") as f:
            for line in f:
                code_out.append(line.strip())

    except FileNotFoundError:
        print(f"File {filename} not found!")
        quit(1)

    return code_out


def remove_unneeded_stuff(code_in):
    code_out = []
    for line in code_in:
        if line and line[:2] != "//" and line[:1] != ";" and line != "":
            line = line.split("//")[0]
            line = line.split(";")[0]
            line = line.split()

            code_out.append(line)

    code_in = code_out
    code_out = []

    for line in code_in:
        if line:
            code_out.append(" ".join(line))
    return code_out


def translate_to_asm(code_in: str) -> str:
    """ Translate instructions to be directly supported by a target. """
    lbl = 343234
    code_out = []
    for line in code_in:
        line = line.split()
        if line[0][0] == ".":
            code_out.append(line[0])
        elif line[0] == "ADD":
            # add reg reg reg 0 0
            code_out.append(f"ADD {line[1]} {line[2]} {line[3]} 0 0")

        elif line[0] == "ADDI":
            #  add reg reg 0 imm 0
            code_out.append(f"ADD {line[1]} {line[2]} 0 {line[3]} 0")

        elif line[0] == "SUB":
            # sub reg reg reg 0 0
            code_out.append(f"SUB {line[1]} {line[2]} {line[3]} 0 0")

        elif line[0] == "SUBI":
            #  sub reg reg 0 imm 0
            code_out.append(f"SUB {line[1]} {line[2]} 0 {line[3]} 0")

        elif line[0] == "NOR":
            # nor reg reg reg 0 0
            code_out.append(f"NOR {line[1]} {line[2]} {line[3]} 0 0")

        elif line[0] == "NORI":
            #  nor reg reg 0 imm 0
            code_out.append(f"NOR {line[1]} {line[2]} 0 {line[3]} 0")

        elif line[0] == "AND":
            # and reg reg reg 0 0
            code_out.append(f"AND {line[1]} {line[2]} {line[3]} 0 0")

        elif line[0] == "ANDI":
            #  and reg reg 0 imm 0
            code_out.append(f"AND {line[1]} {line[2]} 0 {line[3]} 0")

        elif line[0] == "RSH":
            # rsh reg reg 0 0 0
            code_out.append(f"RSH {line[1]} {line[2]} 0 0 0")

        elif line[0] == "INC":
            # add reg reg 0 1 0
            code_out.append(f"ADD {line[1]} {line[2]} 0 1 0")

        elif line[0] == "DEC":
            # sub reg reg 0 1 0
            code_out.append(f"SUB {line[1]} {line[2]} 0 1 0")

        elif line[0] == "PLOD":
            # lod reg 0 poi 0 0
            code_out.append(f"LOD {line[1]} 0 {line[2]} 0 0")

        elif line[0] == "LOD":
            # lod reg 0 0 imm 0
            code_out.append(f"LOD {line[1]} 0 0 {line[2]} 0")

        elif line[0] == "IMM":
            # imm reg 0 0 imm 0
            code_out.append(f"IMM {line[1]}  0 0 {line[2]} 0")

        elif line[0] == "STR":
            # note: in source code STR imm src
            # str 0 reg 0 imm 0
            code_out.append(f"STR 0 {line[2]} 0 {line[1]} 0")

        elif line[0] == "PSTR":
            # str 0 reg poi 0 0
            code_out.append(f"STR 0 {line[2]} {line[1]} 0 0")

        elif line[0] == "PSH":
            # sub 7 7 0 1 0 (dec)
            # str 0 reg 7 0 0 (pstr)
            code_out.append("SUB 7 7 0 1 0")
            code_out.append(f"STR 0 {line[1]} 7 0 0")

        elif line[0] == "POP":
            # lod reg 0 7 0 0 (plod)
            # add 7 7 0 1 0 (addi/inc)
            code_out.append(f"LOD {line[1]} 0 7 0 0")
            code_out.append("ADD 7 7 0 1 0")

        elif line[0] == "MOV":
            # add reg reg 0 0 0
            code_out.append(f"ADD {line[1]} {line[2]} 0 0 0")

        elif line[0] == "OR":
            # in: OR dest a b
            # nor dest a b 0 0
            # nor dest dest 0 0 0 (not)
            code_out.append(f"NOR {line[1]} {line[2]} {line[3]} 0 0")
            code_out.append(f"NOR {line[1]} {line[1]} 0 0 0")

        #  LSH = add a a a

        #  NEG = sub a r0 a

        #  NOT = nor 0 a

        #  elif line[0] == "PBGE": # (branch to pointer)
            # sub 0 a b 0 0
            # brnch 0 0 poi 0 c

    #  BGE - sub(a,b) c
        elif line[0] == "BGE":
            # sub 0 B C 0 0
            # brnch 0 0 0 A c
            code_out.append(f"SUB 0 {line[2]} {line[3]} 0 0")
            code_out.append(f"BRNCH 0 0 0 {line[1]} c")

    #  BRL = sub a b, nc and nz
        elif line[0] == "BRL":
            # sub 0 A B 0 0
            # brnch 0 0 0 A nc&nz
            code_out.append(f"SUB 0 {line[2]} {line[3]} 0 0")
            code_out.append(f"BRNCH 0 0 0 {line[1]} nc&nz")

            #  BRG - sub(a,b) c and nz
        elif line[0] == "":
            #
            code_out.append("")
            code_out.append("")

    #  BRE - sub(a,b) c and z
        elif line[0] == "":
            #
            code_out.append("")
            code_out.append("")

#  BNE - sub(a,b) nz
        elif line[0] == "":
            #
            code_out.append("")
            code_out.append("")

    #  BLE = BGE a c b
        elif line[0] == "":
            #
            code_out.append("")

    #  JMP = bge p 0 0
        elif line[0] == "JMP":
            # add 0 0 0 0 0  - set zero flag
            # brnch 0 0 0 imm z
            code_out.append("ADD 0 0 0 0 0")
            code_out.append(f"BRNCH 0 0 0 {line[1]} z")


#  BRC - add(a,b) c
        elif line[0] == "":
            #
            code_out.append("")
            code_out.append("")

#  BNC - add(a,b) nc
        elif line[0] == "":
            #
            code_out.append("")
            code_out.append("")

#  BRZ - add a 0, z
        elif line[0] == "BRZ":
            # add 0 B 0 0 0
            # brnch 0 0 0 A z
            code_out.append(f"ADD 0 {line[2]} 0 0 0")
            code_out.append(f"BRNCH 0 0 0 {line[1]} z")

#  BNZ - add a 0, nz
        elif line[0] == "":
            #
            code_out.append(f"")
            code_out.append(f"")

#  BRN - add a a, c
        elif line[0] == "":
            #
            code_out.append(f"")
            code_out.append(f"")

#  BRP - add a a, nc
        elif line[0] == "":
            #
            code_out.append(f"")
            code_out.append(f"")

#  BOD - rsh a, nc
        elif line[0] == "":
            #
            code_out.append(f"")
            code_out.append(f"")

#  BEV - rsh a, c
        elif line[0] == "":
            #
            code_out.append(f"")
            code_out.append(f"")
    #  NOP = add 0 0 0
    #  CAL = push ~+2, jump
        elif line[0] == "CAL":
            # imm 6 0 0 .ret_addr 0
            # sub 7 7 0 1 0
            # str 0 6 7 0 0
            # brnch 0 0 0 A nz - zero flag is unset after sub instr.
            # .ret_addr
            lbl += 123
            code_out.append(f"IMM 6 0 0 .return_addr_{lbl} 0")
            code_out.append(f"SUB 7 7 0 1 0")
            code_out.append(f"STR 0 6 7 0 0")
            code_out.append(f"BRNCH 0 0 0 {line[1]} nz")
            code_out.append(f".return_addr_{lbl}")

    #  RET = pop temp, jump temp
        elif line[0] == "RET":
            # lod 6 0 7 0 0
            # add 7 7 0 1 0
            # add 0 0 0 0 0
            # brnch 0 0 6 0 z
            code_out.append("LOD 6 0 7 0 0")
            code_out.append("ADD 7 7 0 1 0")
            code_out.append(f"ADD 0 0 0 0 0")
            code_out.append(f"BRNCH 0 0 6 0 z")

#  HLT = msc set halt bit
        elif line[0] == "HLT":
            # msc 0 0 0 0 1
            code_out.append("MSC 0 0 0 0 1")
    #  CPY = lod, str
        else:
            print(f"not supported instruction!\n{line[0]}")
            quit(1)
#  MSC - set status bits - halt bit, ignore wait bit?, interrupt mask bit
#  BRNCH - 7 conditions: z, nz, c, nc, nc&nz, c&z, c&nz,
    return code_out


def parse_labels(code_in: str):
    idx = 0
    code_out = []
    labels = {}
    for line in code_in:
        #  tmp.append(f"{idx} {line}")
        if line[0][0] != ".":
            idx += 1
            code_out.append(line)
        else:
            labels[line] = idx
    return code_out, labels


def replace_labels(code_in, labels_dict):
    code_out = []
    for line in code_in:
        line = line.split()
        nline = ""
        for word in line:
            if word[0] == ".":
                nline += str(labels_dict[word])
                nline += " "
            elif word[0] != ".":
                nline += word
                nline += " "
        code_out.append(nline)

    return code_out


def replace_addresses(code_in, dev_dict, heap_start):
    code_out = []
    for line in code_in:
        line = line.split()
        nline = ""
        for word in line:
            if word[0] == "%":
                nline += str(dev_dict[word])
                nline += " "
            elif word[0] == "#":
                nline += str(int(word[1:]) + heap_start)
                nline += " "
            elif word[0] == "R":
                nline += str(int(word[1:]))
                nline += " "
            else:
                nline += word
                nline += " "
        code_out.append(nline)

    return code_out


def save_file(filename, code):
    with open(filename, "w") as f:
        for line in code:
            f.write(line + "\n")


def include_includes(code_in, libdir):
    lib_code = []
    code_out = []
    for line in code_in:

        if line and line.split()[0] == "@INCLUDE":
            libname = libdir + line.split()[1]
            try:
                with open(libname, "r") as lib:
                    for lib_line in lib:
                        lib_code.append(lib_line.strip())
            except FileNotFoundError:
                print(f"File {libname} not found!")
                quit(1)
        else:
            code_out.append(line)

    code_out.append("////begin library code////")
    code_out += lib_code
    code_out.append("////end library code////")

    return code_out
