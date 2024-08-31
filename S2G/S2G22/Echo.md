Challenge description
```
Welcome to Echo!
In order to solve the challenge you will be given words,
which you have to echo back to the server.
You will be given 50 words.
You have 1 second to echo each word back.

Are you ready? (y/n) y
Word number 1 is: five
Enter the word: 
```
I already knew this was possible to solve relatively simply with pwntools, having done a couple of tasks like this before. So I got to it, not being very proficient in pwntools. After quite a lot of debugging I was left with the script below, which gave me the flag.


Solution
```
from pwn import *

r = remote("10.212.138.23", 54790)
r.sendlineafter(b"(y/n)",'y')
for i in range(50):
    r.recvuntil(b': ', timeout=1, drop=True)
    w = r.recvline()
    y = w.decode().strip("\n").encode()
    r.sendlineafter(b': ', y)
print(r.recvline())
