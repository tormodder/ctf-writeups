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

Solution
```
from pwn import *

r = remote("10.212.138.23", 54790)
r.sendlineafter(b"(y/n)",'y')
for i in range(50):
    x = r.recvuntil(b': ', timeout=1, drop=True)
    print(i)
    print("x: ", x)
   # r.recvuntil(b': ', timeout=1, drop=True)
    w = r.recvline()
    y = w.decode().strip("\n").encode()
    print("w: ", w,"y: ", y)
    r.sendlineafter(b': ', y)
print(r.recvline())
