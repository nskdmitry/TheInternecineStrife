def toothIndex(old, junior, n):
    def f(val):
        return sum(range(0, val))
    if old == 0: return junior
    return (junior - old) + f(old) + (n - old) * old