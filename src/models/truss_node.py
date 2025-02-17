class TrussNode:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.forces = [0, 0]  # Fx, Fy
        self.constraints = [False, False]  # Fixed_x, Fixed_y