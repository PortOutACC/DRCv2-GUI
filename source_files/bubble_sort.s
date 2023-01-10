@INCLUDE rand_array.s


// make array of 5 random numbers.
IMM R1 #6
IMM R2 16

// store list start point and decremented size in memory
STR #0 R1
DEC R6 R2
STR #1 R6

CAL .rand_array

// R4 - list length

// R3 - doesNeedToBeSortedAgain? (bool)
IMM R3 1 // initially - yes.

// R5, R6 - pointers
.mainloop
BRZ .end R3
IMM R3 0 // sorted = false

LOD R5 #0
LOD R4 #1

.loop
// if R4 == 0, goto .mainloop
BRZ .mainloop R4
INC R6 R5   // R6 is always onee step further than R5
PLOD R1 R5
PLOD R2 R6

// if R2 >= R1. goto .inc
BGE .inc R2 R1
// else:
PSTR R5 R2
PSTR R6 R1
IMM R3 1

.inc
INC R5 R5
DEC R4 R4
JMP .loop


.end
HLT
