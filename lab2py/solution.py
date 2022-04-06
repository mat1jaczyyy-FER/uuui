#!/usr/bin/env python3
# Dominik Matijaca 0036524568

from sys import argv

def enumerate_from(sequence, start):
    n = 0
    for i in sequence:
        if n >= start:
            yield n, i
        n += 1

def subset(a, b):
    return all(i in b for i in a)

def clause_str(s):
    return ' v '.join(LITERALS[i] for i in sorted(s, key = lambda x: abs(x))) if len(s) else "NIL"

def resolution(clauses, print_on_fail = True):
    target = clauses[-1]
    del clauses[-1]
    
    delete = set()

    for i, x in enumerate(clauses):
        if i in delete: continue
        
        for j, y in enumerate_from(clauses, start = i + 1):
            if j in delete: continue
            
            if subset(y, x):
                delete.add(i)
                break
            
            if subset(x, y):
                delete.add(j)
        
        if any(a == -b for a in x for b in x):
            delete.add(i)

    clauses = [x for i, x in enumerate(clauses) if i not in delete]
    next = len(clauses)

    clauses.extend([{-i} for i in target])
    clauses = [[x, None, None, True] for x in clauses]
    
    def resolve(x, y):
        result = None

        for a in x:
            for b in y:
                if a == -b:
                    if result != None:
                        return None
                    result = a
        
        return result

    def eliminate(r, *s):
        for i in s:
            for j in i:
                if not j[3]: continue
                if subset(j[0], r):
                    return False

        for i in s:
            for j in i:
                if not j[3]: continue
                if subset(r, j[0]):
                    j[3] = False
        
        return True

    def search():
        nonlocal next
        new = []
        while True:
            for i, x in enumerate(clauses):
                if not x[3]: continue

                for j, y in enumerate_from(clauses, start = max(next, i + 1)):
                    if not y[3]: continue
                    
                    literal = resolve(x[0], y[0])
                    if literal == None:
                        continue

                    r = (x[0] | y[0]) - {literal, -literal}

                    if not len(r):
                        clauses.append([r, i, j, True])
                        return True
                    
                    if not eliminate(r, clauses, new):
                        continue

                    new.append([r, i, j, True])
            
            new = [i for i in new if i[0] not in [j[0] for j in clauses]]

            if not len(new):
                return False

            next = len(clauses)
            clauses.extend(new)
    
    result = search()

    if print_on_fail or result:
        def reconstruct(i, s = set()):
            if i == None: return
            
            s.add(i)
            
            reconstruct(clauses[i][1], s)
            reconstruct(clauses[i][2], s)

            return s

        keep = reconstruct(len(clauses) - 1)
        clauses = [x for i, x in enumerate(clauses) if i in keep]

        keep = {x: i for i, x in enumerate(sorted(keep))}
        keep[None] = None

        clauses = [[x[0], keep[x[1]], keep[x[2]], x[3]] for x in clauses]

        sep = False
        for i, x in enumerate(clauses):
            if x[1] == None:
                print(f"{i + 1}: {clause_str(x[0])}")

            else:
                if not result: break

                if not sep:
                    print("===============")
                    sep = True
                
                print(f"{i + 1}: {clause_str(x[0])} ({x[1] + 1}, {x[2] + 1})")

        print("===============")
    
    print(f"[CONCLUSION]: {clause_str(target)} is {'true' if result else 'unknown'}")

def cooking(clauses):
    print("Constructed with knowledge:")
    
    for i in clauses:
        print(clause_str(i))
    
    for clause, action in USER_COMMANDS:
        print()
        s = clause_str(clause)
        print(f"User's command: {s} {action}")

        if action == "?":
            resolution(clauses + [clause], False)
        
        elif action == "+":
            if clause not in clauses:
                clauses.append(clause)
            
            print(f"Added {s}")

        elif action == "-":
            if clause in clauses:
                clauses.remove(clause)

            print(f"Removed {s}")

def file(path):
    with open(path, "r", encoding = "utf8") as f:
        return [i.strip().lower() for i in f.readlines() if not i.startswith("#")]

TASK_NAME = argv[1]

tasks = [resolution, cooking]
TASK = [i.__name__ for i in tasks].index(TASK_NAME)

CLAUSES = [set(i.split(" v ")) for i in file(argv[2])]

LITERALS = {i + 1: x for i, x in enumerate(set(map(lambda x: x.replace("~", ""), set().union(*CLAUSES))))}
LITERALS.update({-i: f"~{x}" for i, x in LITERALS.items()})
LITERALS.update({x: i for i, x in LITERALS.items()})

CLAUSES = [set(map(lambda x: LITERALS[x], i)) for i in CLAUSES]

if len(argv) > 3:
    USER_COMMANDS = [i.rsplit(maxsplit = 1) for i in file(argv[3])]

    for i in USER_COMMANDS:
        i[0] = set(LITERALS[j] for j in i[0].split(" v "))

tasks[TASK](CLAUSES)
