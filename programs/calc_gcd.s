@INCLUDE modulo.s
@INCLUDE gcd.s

IMM R1 144
IMM R2 233
CAL .gcd
STR %NUMB R1

HLT



