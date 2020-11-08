import math

def average(collection):
    return (reduce(lambda acc, val: acc + val, collection, 0)/len(collection), len(collection))

def averageClarification(averTuple, newVal):
    n = averTuple[1] + 1
    return (averTuple[0] + (newVal - averTuple[0])/n, n)

def diam(collection):
    return abs(max(collection) - min(collection))

def gradientXY(mapper, dx = 1, power = 3):
    X = mapper.keys()
    X.sort()
    diffs = [{x: mapper[x] for x in X}]
    for i in range(1, power+1, 1):
        diffs.append({x: 0 if x == 0 else (diffs[i-1][x] - diffs[i-1][x-dx])/dx for x in X})
    return diffs

def gradientLinear(collection):
    return [collection[0] if i == 0 else collection[i] - collection[i-1] for i in range(0, len(collection))]

def frequency(collection):
    freqs = {}
    for value in collection:
        freqs[value] = freqs.get(value, 0) + 1
    return freqs

if __name__ == "__main__":
    print("Test")
    three = [1, 2, 3]
    four = [1, 2, 3, 4]
    av1 = average(three)
    av2 = average([1, 2, 3, 4])
    av3 = averageClarification(av1, 4)
    print("average", three, "= %d" % (av1[0]), "?= 2")
    print("average", four, "= %f" % (av2[0]), "?= 2.5")
    print("averageClarification", four, "= %f" % (av3[0]), "?= 2.5")

    k = 20
    d = 20
    c = 100
    collect = [int((i-k)*math.sin((i+k)*math.pi/d)*math.cos((k-i)*math.pi/d)) for i in range(1, c)]
    print(collect)
    aver = average(collect)
    diameter = diam(collect)
    maxi = max(collect)
    mini = min(collect)
    grad = gradientLinear(collect)
    print("Average = %f" % (aver[0]))
    print("Range on ", "[%d, %d]" % (mini, maxi))
    print("Diameter = %d" % (diameter))
    print("Gradient", grad)
    freqs = frequency(collect)
    print("Frequency of numbers", freqs)
