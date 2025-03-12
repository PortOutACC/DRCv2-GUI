// multiply routine.
// For unsigned integers.
// uint16 mul(R1, R2) --> R1, R2 (BE)

.mul

ADD hsum = h1 + h2
ADD lsum = l1 + l2
BNC .skip l1 + l2
INC hsum

.skip


if(R1>R0) goto .label
