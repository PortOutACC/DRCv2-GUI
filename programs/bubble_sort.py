from random import randint
from os import system
from time import sleep

l = []
for i in range(10):
    l.append(randint(0,255))

for i in l:
    print(i)

c = True
while c == True:
    p1 = 0
    c = False
    while p1 < 9:
        p2 = p1 + 1

        a = l[p1]
        b = l[p2]

        if b < a:
            c = True
            l[p1] = b
            l[p2] = a
        p1 += 1




        sleep(0.1)
        system("clear")
        # print(c)
        for i in l:
            print(i)

