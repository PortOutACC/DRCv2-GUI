@INCLUDE rand_array.s


// make array of random numbers.
IMM R1 #0
IMM R2 5
CAL .rand_array

// R3 - doesNeedToBeSortedAgain? (bool)
IMM R3 1 // initially - yes.

// R5, R6 - pointers
.mainloop
BRZ .end R3
IMM R5 #0
IMM R6 0

.loop






.end
HLT
