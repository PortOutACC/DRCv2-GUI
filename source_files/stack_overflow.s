// create an array of 10 random numbers in core mem.

// list start:
IMM R6 #0
// list size:
IMM R3 100

.loop
BRZ .end R3
LOD R1 %RNG
PSTR R6 R1
DEC R3 R3
INC R6 R6
JMP .loop


.end
IMM R1 200

.rec
BRZ .ret_x R1
DEC R1 R1

CAL .rec

.ret_x
STR %NUMB R1

HLT
