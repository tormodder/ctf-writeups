# Fun Fact

>This challenge should help you to learn more about reverse engineering Python code. But if not, at least you can learn more about sea creatures!!
>Flag format - `byuctf{message}`

**files**: obfuscated.py

## Writeup
Looking at the **obfuscated.py** file it's clearly encoded with base64. Throwing it into Cyberchef and decoding from base64 gives **deobfuscated.py**.

On line 29 in that file, we get the conditional: 
```
if(encrypted == 'g%4c$zc%dz4gg;'):
        print("Success!")
```
Since nothing else hinted at a flag in the code I assumed the `{message}` was a string which, when encrypted, looked like the `encrypted` string. Which is another way to say reversing the encryption on the `encrypted` string would give the flag.

On line 25 we see how the string is encrypted: 
```
encrypted = "".join([chr(ord(x) ^ ord(key)) for x in user_input])
```
We see that the encryption works by joining together a list of characters which correspond to the unicode codes for numbers obtained through the function: `ord(x) ^ ord(key)`. The variable `key` is obtained through a similar encryption process, but this process is irrelevant, because `key` always had the value `'W'` or `87` in unicode.

## Binary XOR operator
The `^` operator is a binary exclusive or (XOR) operator. This holds true if either one or the other of the statement is true, but not both:

|a|b|a ^ b|
--|-|-----|
|1|1|0|
|1|0|1|
|0|1|1|
|0|0|0|

Applied to binary numbers, this means that when two bits in the same position in two different numbers are equal, the bit flips to 0, and when they are unequal it flips to 1.

E.g. `5 ^ 3 = 6`, or in binary `101 ^ 011 = 110`

Understanding how this binary operator at the core of the encryption process worked, it was just a matter of figuring out how to reverse it.

After searching online I found the following on the relationship between three statements and XOR:
```
c = a ^ b
a = c ^ b
b = c ^ a
```
Then it was just a simple matter of doing the same XOR operation on our two known variables to obtain the flag. Which is done in **solution.py**:
`flag = "".join([chr(ord(i) ^ ord(key)) for i in message])`
Giving the flag: `0rc4s-4r3-c00l`
