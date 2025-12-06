import os
import numpy as np

class Cell(object):
    def __init__(self, i, j):
        self.i = i
        self.j = j


class Node:
    """Stores search information for each cell."""
    def __init__(self):
        self.parent = None
        self.g = float('inf')     # cost so far
        self.h = 0                # heuristic cost
        self.f = float('inf')     # g + h
        self.visited = False


class GridGraph:
    def __init__(self, file_path=None, width=-1, height=-1, origin=(0, 0),
                 meters_per_cell=0, cell_odds=None, collision_radius=0.15, threshold=-100):

        if file_path is not None:
            assert self.load_from_file(file_path)
        else:
            self.width = width
            self.height = height
            self.origin = origin
            self.meters_per_cell = meters_per_cell
            self.cell_odds = cell_odds

        self.threshold = threshold
        self.set_collision_radius(collision_radius)
        self.visited_cells = []

        # Allocate node data grid
        self.nodes = [[Node() for _ in range(self.height)] for _ in range(self.width)]

    def as_string(self):
        map_list = self.cell_odds.astype(str).tolist()
        rows = [' '.join(row) for row in map_list]
        cell_data = ' '.join(rows)
        header_data = f"{self.origin[0]} {self.origin[1]} {self.width} {self.height} {self.meters_per_cell}"
        return ' '.join([header_data, cell_data])

    def load_from_file(self, file_path):
        if not os.path.isfile(file_path):
            print(f'ERROR: loadFromFile: Failed to load from {file_path}')
            return False

        with open(file_path, 'r') as file:
            header = file.readline().split()
            origin_x, origin_y, self.width, self.height, self.meters_per_cell = map(float, header)
            self.origin = (origin_x, origin_y)
            self.width = int(self.width)
            self.height = int(self.height)

            self.cell_odds = np.zeros((self.height, self.width), dtype=np.int8)

            for r in range(self.height):
                row = file.readline().strip().split()
                for c in range(self.width):
                    self.cell_odds[r, c] = np.int8(row[c])
        return True

    def pos_to_cell(self, x, y):
        i = int(np.floor((x - self.origin[0]) / self.meters_per_cell))
        j = int(np.floor((y - self.origin[1]) / self.meters_per_cell))
        return Cell(i, j)

    def cell_to_pos(self, i, j):
        x = (i + 0.5) * self.meters_per_cell + self.origin[0]
        y = (j + 0.5) * self.meters_per_cell + self.origin[1]
        return x, y

    def is_cell_in_bounds(self, i, j):
        return 0 <= i < self.width and 0 <= j < self.height

    def is_cell_occupied(self, i, j):
        return self.cell_odds[j, i] >= self.threshold

    def set_collision_radius(self, r):
        r_cells = int(np.ceil(r / self.meters_per_cell))
        r_indices, c_indices = np.indices((2 * r_cells - 1, 2 * r_cells - 1))
        c = r_cells - 1
        dists = (r_indices - c)**2 + (c_indices - c)**2
        self._coll_ind_j, self._coll_ind_i = np.nonzero(dists <= (r_cells - 1)**2)
        self.collision_radius = r
        self.collision_radius_cells = r_cells

    def check_collision(self, i, j):
        j_inds = self._coll_ind_j + j - (self.collision_radius_cells - 1)
        i_inds = self._coll_ind_i + i - (self.collision_radius_cells - 1)

        in_bounds = np.bitwise_and(
            np.bitwise_and(j_inds >= 0, j_inds < self.height),
            np.bitwise_and(i_inds >= 0, i_inds < self.width)
        )
        return np.any(self.is_cell_occupied(i_inds[in_bounds], j_inds[in_bounds]))

    # ================
    # REQUIRED FUNCTION
    # ================
    def get_parent(self, cell):
        return self.nodes[cell.i][cell.j].parent

    # ================
    # REQUIRED FUNCTION
    # ================
    def init_graph(self):
        self.visited_cells = []
        # Reset all nodes
        self.nodes = [[Node() for _ in range(self.height)] for _ in range(self.width)]

    # ================
    # REQUIRED FUNCTION
    # ================
    def find_neighbors(self, i, j):
        neighbors = []
        dirs = [(1,0), (-1,0), (0,1), (0,-1)]

        for di, dj in dirs:
            ni, nj = i + di, j + dj
            if not self.is_cell_in_bounds(ni, nj):
                continue
            if self.check_collision(ni, nj):
                continue
            neighbors.append(Cell(ni, nj))

        return neighbors
