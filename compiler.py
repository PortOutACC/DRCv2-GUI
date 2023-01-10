""" DRCv2 compiler main script. """
from sys import argv
from libcompiler import *

# Directory to be searched for code libraries.
LIB_DIR = ""

HEAP_START = 64
DEVICES = {
    "%RNG": 40,
    "%NUMB": 2
}

FILENAME = "programs/bubble_sort.s"  # Default source file.

try:
    FILENAME = argv[1]
except Exception:
    print(f"No filename given. Defaulting to {FILENAME}")

CODE = load_file(FILENAME)
CODE = include_includes(CODE, LIB_DIR)

# Print raw code.
for line in CODE:
    print(line)

print("==================================")

CODE = remove_unneeded_stuff(CODE)
CODE = translate_to_asm(CODE)
CODE, LABELS = parse_labels(CODE)
CODE = replace_labels(CODE, LABELS)
CODE = replace_addresses(CODE, DEVICES, HEAP_START)

# Print assembler code.
for i in range(len(CODE)):
    print(i, CODE[i])
print("==================================")

# Save assembly.
try:
    FILENAME = argv[2]
    if input("Save assembly? Y/n\n") != "n":
        save_file(FILENAME, CODE)
        print("Saving assembly...")
except Exception:
    print("Save failed.")
    quit(1)

quit(0)
