import numpy as np

class TrussBar:
    def __init__(self, id, start_node, end_node, E, A):
        self.id = id
        self.start = start_node
        self.end = end_node
        self.E = E  # Módulo de Elasticidade
        self.A = A  # Área da seção transversal
        self.length = self.calc_length()
        self.normal_force = 0

    def calc_length(self):
        dx = self.end.x - self.start.x
        dy = self.end.y - self.start.y
        return np.sqrt(dx * dx + dy * dy)