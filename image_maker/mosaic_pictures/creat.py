l=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]
i=8
j=0
while True:
    if i< len(l):
        l2=l[j:i]
        print(l2)
    else:
        print(l[j:])    
        break
    i+=8
    j+=8
   