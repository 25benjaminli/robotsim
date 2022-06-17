def getcomb(a, b):
    numerator = 1
    denom = 1
    print(a, b)

    for i in range(b):
        numerator *= (a - i)
        denom *= (b - i)
        # print(numerator, denom)

    return numerator / denom

s = 0
for i in range(44, 0, -1):
    s += getcomb(i, 4)

print(s)
