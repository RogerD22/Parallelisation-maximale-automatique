import networkx as nx
import matplotlib.pyplot as plt

class Task:
    def __init__(self, name, reads, writes, run):
        self.name = name
        self.reads = reads
        self.writes = writes
        self.run = run


