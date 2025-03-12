c = 0
def f():
    global c
    print(c)
    if c == 6:
        return
    c += 1

for i in range(10):
    f()






quit(0)

COUNT = 0
RECORDS = {}
def gcd(x: int, y: int) -> int:
    #  print([x, y])
    global COUNT
    COUNT += 1
    if y == 0:
        return x
    else:
        return(gcd( y, x%y))

#  print(gcd(144, 233))
#  quit()
for x in range(256):
    for y in range(256):
        gcd(x, y)
        RECORDS[COUNT] = [x, y]
        COUNT = 0
        #  input()
print(RECORDS)















quit()

x = int(input())

while x != 1:
    if x%2 == 0: # is even
        x = x >> 1
    else:
        x = 3*x +1
    print(x)

