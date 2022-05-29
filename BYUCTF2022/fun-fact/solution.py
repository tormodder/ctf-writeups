#for each character in flag:
#new character = key ^ flag[i]

key = 'W'
message = 'g%4c$zc%dz4gg;'
flag = "".join([chr(ord(i) ^ ord(key)) for i in message])
print(flag)