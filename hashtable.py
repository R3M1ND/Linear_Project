dict1 = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5}


dict1 = {k:v*v for k,v in dict1.items()}

for i in dict1.keys():
    dict1[i] += 20


print(dict1)



for c in charact