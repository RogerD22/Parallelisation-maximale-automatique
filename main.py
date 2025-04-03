from Projet import Task, TaskSystem
import time 

def run1():
    global X
    X = 1
    print("Execution de la tache 1")

def run2():
    global Y, X
    Y = X + X
    print("Execution de la tache 2")

def run3():
    global Z
    Z = 1
    print("Execution de la tache 3")

def run4():
    global Y, Z
    Z = Z + Y
    print("Execution de la tache 4 %d" % Z)

t1 = Task(name="T1", reads=[], writes=["X"], run=run1)
t2 = Task(name="T2", reads=["X"], writes=["Y"], run=run2)
t3 = Task(name="T3", reads=[], writes=["Z"], run=run3)
t4 = Task(name="T4", reads=["Z", "Y"], writes=["Z"], run=run4)

task_system = TaskSystem(
    tasks=[t1, t2, t3, t4],
    precedence={"T1": [],"T2": ["T1"],"T3": [],"T4": ["T2", "T3"]
    }
)

task_system.draw()

print("\n--- Exécution séquentielle ---")
start = time.time()
task_system.runSeq()

print("\n--- Exécution parallèle ---")
start = time.time()
task_system.run()

print("\n--- Test de déterminisme ---")
task_system.detTestRnd(globals())

print("\n--- Test de parallélisme ---")
task_system.parCost()