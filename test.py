lst = [1,2,3,4,5]
def gen(l):
    for i in l:
        yield i

for i in gen(lst):
    print(i)