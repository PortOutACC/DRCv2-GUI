""" DRCv2 compiler main script. """

from libcompiler import *


LIB_DIR = "programs/"
HEAP_START = 64
#  STACK_START = 16
DEVICES = {
    "%RNG": 40,
    "%NUMB": 2
}
FILENAME = "bubble_sort"

code = load_file(f"programs/{FILENAME}.s")
code = include_includes(code, LIB_DIR)

for line in code:
    print(line)
print("==================================")

code = remove_unneeded_stuff(code)
code = translate_to_asm(code)
code, labels = parse_labels(code)
code = replace_labels(code, labels)
code = replace_addresses(code, DEVICES, HEAP_START)

for i in range(len(code)):
    print(i, code[i])
print("==================================")


if input("Save assembly? Y/n\n") != "n":
    save_file(f"programs/{FILENAME}.a", code)
    print("Saving assembly...")

quit(0)
