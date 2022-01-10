import math
def mul_sum(a,b):
    sum_a_b = 0
    for i in range(len(a)):
        sum_a_b += a[i] * b[i]
    return sum_a_b
def sum_sqr(a):
    total = 0
    for i in range(len(a)):
        total += a[i]**2
    return total

def karlpearson_coff(a, b):
    n = len(a)
    Ex = sum(a)
    Ey = sum(b)
    Exy = mul_sum(a,b)
    ExEy = sum(a)*sum(b)
    Ex2 = sum_sqr(a)
    Ey2 = sum_sqr(b)

    r = ((n*Exy) - ExEy)/((math.sqrt(n*Ex2 -Ex**2))*math.sqrt(n*Ey2 - Ey**2))
    
    return r

    
a = [120, 118, 130, 140, 140, 128, 140, 140, 120, 128, 124, 135]
b = [60, 60, 68, 69, 80, 75, 94, 80, 60, 80, 70, 85]


# print(len(a))
# print(sum(a))
# print(sum(b))
print(karlpearson_coff(a, b))
# print(sum_sqr(a), sum_sqr(b))
