import time
import random
import threading
from graphviz import Digraph

class Task:
    def __init__(self, name, reads=None, writes=None, run=None):
        if reads is None:
            reads = []
        if writes is None:
            writes = []
        
        self.name = name
        self.reads = set(reads)
        self.writes = set(writes)
        self.run = run
        
    def execute(self):
        if self.run:
            self.run()

class TaskSystem:
    def __init__(self, tasks, precedence):
        self.tasks = {task.name: task for task in tasks}
        self.precedence = precedence
        self.validate()

        for i in range(len(tasks)):
            task_i = tasks[i].name
            for j in range(i + 1, len(tasks)):
                task_j = tasks[j].name
                if not self.can_run_in_parallel(task_i, task_j):
                    raise ValueError(f"Les tâches {task_i} et {task_j} violent les conditions de Bernstein.")
    
    def validate(self):
        defined_tasks = set(self.tasks.keys())
        for task, deps in self.precedence.items():
            if task not in defined_tasks:
                raise ValueError(f"Tâche inconnue dans la précédence: {task}")
            for dep in deps:
                if dep not in defined_tasks:
                    raise ValueError(f"Tâche dépendante inexistante: {dep}")
        
        if self.has_cycle():
            raise ValueError("Le graphe de dépendances contient une boucle.")
    
    def has_cycle(self):
        visited = set()
        rec_stack = set()
        
        def visit(task):
            if task in rec_stack:
                return True  # Cycle détecté
            if task in visited:
                return False
            visited.add(task)
            rec_stack.add(task)
            for dep in self.precedence.get(task, []):
                if visit(dep):
                    return True
            rec_stack.remove(task)
            return False
        
        for task in self.tasks:
            if visit(task):
                return True
        return False
    

    
    def can_run_in_parallel(self, task1, task2):
        t1_reads = self.tasks[task1].reads
        t1_writes = self.tasks[task1].writes
        t2_reads = self.tasks[task2].reads
        t2_writes = self.tasks[task2].writes

        if (t1_writes & t2_reads or t1_reads & t2_writes or t1_writes & t2_writes) and (task1 not in self.precedence.get(task2, []) and task2 not in self.precedence.get(task1, [])):
            return False
        return True

    def runSeq(self):
        """ Exécution séquentielle des tâches en respectant les dépendances """
        executed = set()
        start = time.time()
        # On exécute les tâches en respectant l'ordre topologique
        while len(executed) < len(self.tasks):
            for task in self.tasks:
                if task not in executed and all(dep in executed for dep in self.precedence.get(task, [])):
                    self.tasks[task].execute()
                    executed.add(task)
        print(f"Temps d'exécution séquentielle: {time.time() - start:.6f}s")

        
    def run(self):
        """ Exécution parallèle des tâches en respectant les dépendances et les conditions de Bernstein """
        start = time.time()
        executed = set()
        precedence = {task: set(deps) for task, deps in self.precedence.items()}

        while len(executed) < len(self.tasks):
            ready_tasks = [t for t in self.tasks if t not in executed and not precedence.get(t, set())]
            
            threads = []

            for task in ready_tasks:
                if task not in executed and all(dep in executed for dep in self.precedence.get(task, [])):
                    thread = threading.Thread(target=self.tasks[task].execute)
                    thread.start()
                    threads.append((task, thread))

            for task, thread in threads:
                thread.join()
                executed.add(task)
                for deps in precedence.values():
                    deps.discard(task)
        print(f"Temps d'exécution parallèle: {time.time() - start:.6f}s")
 
    def detTestRnd(self, globals_):
        """ Teste si le système est déterministe en exécutant plusieurs fois """
        results = []
        for _ in range(5):
            for var in globals_:
                if var.isupper():
                    globals_[var] = random.randint(1, 100)
            self.run()
            results.append({var: globals_[var] for var in globals_ if var.isupper()})
        
        if len(set(map(str, results))) > 1:
            print("Le système de tâches n'est PAS déterministe.")
        else:
            print("Le système de tâches est déterministe.")
    
    def parCost(self, runs=5):
        """ Calcule le coût du parallélisme par rapport à l'exécution séquentielle """
        seq_times = []
        par_times = []
        
        for _ in range(runs):
            start = time.time()
            self.runSeq()
            seq_times.append(time.time() - start)
            
            start = time.time()
            self.run()
            par_times.append(time.time() - start)
        
        print(f"Temps moyen séquentiel: {sum(seq_times)/runs:.6f}s")
        print(f"Temps moyen parallèle: {sum(par_times)/runs:.6f}s")

    def draw(self):
        """ Dessine le graphe des dépendances avec Graphviz """
        dot = Digraph(comment='Dépendances des tâches')
        for task in self.tasks:
            dot.node(task)
        for task, deps in self.precedence.items():
            for dep in deps:
                dot.edge(dep, task)
        dot.render('task_dependencies', format='png', view=True)