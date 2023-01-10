.modulo
// modulo algorithm
// divident is expected to reside in R1
// and divisor in R2
// return address expected on top of the stack.
// remainder is left in R1.

.modulo_loop
BRL .modulo_ret R1 R2
SUB R1 R1 R2
JMP .modulo_loop
.modulo_ret
RET
