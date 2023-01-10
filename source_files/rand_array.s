.rand_array
// Create an array of n random numbers in core mem.
// List start expected in R1, list length in R2.
// R6 - scratch reg.

BRZ .rand_arr_end R2
LOD R6 %RNG
PSTR R1 R6
INC R1 R1
DEC R2 R2
JMP .rand_array

.rand_arr_end
RET
