import os
import sys
import argparse

def console():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--players', default=10, type=int, help='Count of players without zero-player')
    parser.add_argument('-j', '--junior', default=10, type=int, help='Player with biggest ID')
    parser.add_argument('-o', '--older', default=2200, type=int, help='Player with litte ID')
    return parser

def generateRelations(n):
    table = []
    table.append([tuple((i, 0, i, 0)) for i in range(0, n+1)])
    table[0][0] = tuple((0, 0, 0, -1))
    no = n - 1
    for i in range(1, n):
        table.append([tuple((no + j, i, j, 0)) for j in range(i+1, n+1)])
        no = no + n - i - 1
    return table

def key(n, o, j):
    if o == 0:
        return j
    def trapecy(w, h):
        return (w - h) * h + (h*h + h)/2
    prev = trapecy(n, o)
    return prev + j - o

def listmerge(lstlst):
    all=[]
    for lst in lstlst:
      all.extend(lst)
    return all

if __name__ == '__main__':
    parser = console()
    args = parser.parse_args()
    count = max([3, args.players])
    junior = args.junior
    older = args.older
    if junior < 0:
        junior = -junior
    if older < 0:
        older = -older
    (junior, older) = (junior, older) if junior > older else (older, junior)

    relations = generateRelations(count)
    print("Relations of lord's index table")
    rowNo = 0
    for row in relations:
        try:
            sys.stdout.write(str(row[0][1]) + "\t")
            sys.stdout.flush()
            line = "\t".join([" " for _ in range(-1, count - len(row))] + ["{00:d}".format(item[0]) for item in row])
            print(line)
            rowNo = rowNo + 1
        except:
            print("Error in ", rowNo, row, len(relations), relations[rowNo-1])

    print("")

    relations = listmerge(relations)
    print("Relations between players {} & {}".format(older, junior))
    try:
        if junior > count:
            index = '??'
            relation = None
        elif older < junior:
            index = key(count, older, junior)
            relation = relations[index][3] if len(relations) < index else None
        elif older == 0:
            index = key(count, older, junior)
            relation = relations[index][3]
        else:
            index = "??"
            relation = None
    except:
        print("Index Error", index)
        relation = None

    if relation is not None:
        relation = "Pease" if relation == 0  else ("Union" if relation > 0 else "War")
    else:
        relation = "O, realy?"
    print("Index of relation is {}/{}, status: '{}'".format(index, len(relations) - 1, relation))
    if index != '??' and index < len(relations):
        print(relations[index])
