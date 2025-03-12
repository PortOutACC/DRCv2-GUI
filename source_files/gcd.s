.gcd
// calculates the greatest common divisor
// of R1 and R2 using the Euclidean Algorithm.
// Depends on: modulo
// gcd(R1, R2) -> R1
// R6 is used as a scratch reg.

BRZ .gcd_ret_x R2
PSH R2
CAL .modulo  // R1 = R1%R2

MOV R2 R1
POP R1
CAL .gcd

.gcd_ret_x
RET

// pseudocode:
// int gcd(x, y)
// {
//     if(y == 0) return x;
//     return gcd(y, x%y);
// }
