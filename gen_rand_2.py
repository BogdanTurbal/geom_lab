import numpy as np
import scipy.ndimage
from copy import deepcopy

def find_outer_boundary(arr):
    rows, cols = arr.shape
    visited = np.zeros_like(arr)
    boundary = []

    def is_boundary(r, c):
        if arr[r, c] == 0:
            return False
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
            nr, nc = r + dr, c + dc
            if nr < 0 or nc < 0 or nr >= rows or nc >= cols or (0 <= nr < rows and 0 <= nc < cols and arr[nr, nc] == 0):
                return True
        return False

    def dfs(r, c):
        stack = [(r, c)]
        while stack:
            cr, cc = stack.pop()
            if visited[cr, cc]:
                continue
            visited[cr, cc] = 1
            if is_boundary(cr, cc):
                boundary.append((cr, cc))
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = cr + dr, cc + dc
                if 0 <= nr < rows and 0 <= nc < cols and not visited[nr, nc] and arr[nr, nc] == 1:
                    stack.append((nr, nc))

    for r in range(rows):
        for c in range(cols):
            if arr[r, c] == 1 and not visited[r, c]:
                dfs(r, c)

    return boundary


def flood_fill(arr, start_r, start_c, new_value):
    original_value = arr[start_r, start_c]
    rows, cols = arr.shape
    stack = [(start_r, start_c)]

    while stack:
        r, c = stack.pop()
        if arr[r, c] == original_value:
            arr[r, c] = new_value
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and arr[nr, nc] == original_value:
                    stack.append((nr, nc))



def find_outer_boundary(arr):
    rows, cols = arr.shape
    visited = np.zeros_like(arr)
    boundary = []

    def is_boundary(r, c):
        if arr[r, c] == 0:
            return False
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
            nr, nc = r + dr, c + dc
            if nr < 0 or nc < 0 or nr >= rows or nc >= cols or (0 <= nr < rows and 0 <= nc < cols and arr[nr, nc] == 0):
                return True
        return False

    def dfs(r, c):
        stack = [(r, c)]
        while stack:
            cr, cc = stack.pop()
            if visited[cr, cc]:
                continue
            visited[cr, cc] = 1
            if is_boundary(cr, cc):
                boundary.append((cr, cc))
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = cr + dr, cc + dc
                if 0 <= nr < rows and 0 <= nc < cols and not visited[nr, nc] and arr[nr, nc] == 1:
                    stack.append((nr, nc))

    for r in range(rows):
        for c in range(cols):
            if arr[r, c] == 1 and not visited[r, c]:
                dfs(r, c)

    return boundary


def expand_ones(array):
    rows, cols = array.shape
    new_array = array.copy()
    
    for i in range(rows):
        for j in range(cols):
            if array[i, j] == 1:
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if 0 <= i + dx < rows and 0 <= j + dy < cols:
                            new_array[i + dx, j + dy] = 1
    return new_array


def sort_ortho_poly(boundary):
    def explore(curr, set_b, sb):
        for x, y in [[0, 1], [1, 0], [-1, 0], [0, -1]]:
            nxt = (curr[0] + x, curr[1] + y)
            if nxt in set_b:
                sb.append(nxt)
                set_b.remove(nxt)
                explore(nxt, set_b, sb)
        return sb

    set_b = set(boundary)
    curr = boundary[0]
    set_b.remove(curr)
    sb = [curr]

    return explore(curr, set_b, sb)


def remove_collinear_vertices(vertices):
    """
    Remove vertices that lie on the same edge in a sorted clockwise boundary of an orthogonal polygon.
    
    :param vertices: List of vertices in sorted clockwise boundary (list of tuples)
    :return: List of vertices with collinear vertices removed
    """
    # Initialize a new list to store the result vertices
    result = []
    
    # Iterate over the vertices
    for i in range(len(vertices)):
        prev_vertex = vertices[i - 1]
        curr_vertex = vertices[i]
        next_vertex = vertices[(i + 1) % len(vertices)]
        
        # Check if the current vertex is collinear with previous and next vertices
        if (prev_vertex[0] == curr_vertex[0] == next_vertex[0]) or (prev_vertex[1] == curr_vertex[1] == next_vertex[1]):
            continue  # Skip the current vertex
        else:
            result.append(curr_vertex)
    
    return result

import random
import numpy as np
import matplotlib.pyplot as plt

def get_random_minus_one_or_one():
    return random.choice([-1, 1])

class OrthogonalPolygon:
    def __init__(self, grid_size):
        self.grid_size = grid_size
        self.grid = np.zeros((grid_size, grid_size), dtype=int)
        # Start with a unit square
        self.black_cells = set()
        for i in range(1, 4):
            for j in range(1, 4):
                self.grid[i, j] = 1
                self.black_cells.add((i, j))

    def inflate(self, p, q):
        #print('inflating')
        # Shift rows down
        for i in range(self.grid_size - 1, p, -1):
            self.grid[i, :] = self.grid[i - 1, :]
        
        # Shift columns right
        for j in range(self.grid_size - 1, q, -1):
            self.grid[:, j] = self.grid[:, j - 1]

        self.balck_cells = set()
        for i in range(len(self.grid)):
          for j in range(len(self.grid)):
            self.black_cells.add((i, j))

    def is_vertix(self, x, y):
        dir = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for d in range(4):
          is_ax = True
          for i in range(2):
            dm = (d + i) % 4
            if self.grid[x + dir[dm][0], y + dir[dm][1]] != 1:
              is_ax = False

          diag = (dir[d][0] + dir[(d + 1) % 4][0], dir[d][1] + dir[(d + 1) % 4][1])
          if self.grid[x + diag[0] , y + diag[1]] != 0:
              is_ax = False
          if is_ax:
            return 1

        for d in range(4):
          is_ax = True
          for i in range(2):
            dm = (d + i) % 4
            if self.grid[x + dir[dm][0], y + dir[dm][1]] != 0:
              is_ax = False

          diag = (dir[d][0] + dir[(d + 1) % 4][0], dir[d][1] + dir[(d + 1) % 4][1])
          if self.grid[x + diag[0] , y + diag[1]] != 0:
              is_ax = False

          if is_ax:
            return 2
        return 0

    def cut(self, p, q):
        #self.display_grid()
        vc = (p + 1, q + 1)
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        random.shuffle(directions)
        #print(vc)

        for dx, dy in directions:
            #print('()'*20)
            x, y = vc
            while 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                if self.grid[x, y] == 0:
                    x -= dx
                    y -= dy
                    break
                x += dx
                y += dy
            #print(x, y)
            
            fnd = False
            dnf = get_random_minus_one_or_one()
            #print(dnf)
            xn = x
            yn = y
            #print(dx, dy)

            t_rem = -1
            if (dx, dy) in [(0, 1), (0, -1)]:
              #print('--0--')
              while True:
                #print(x, yn)
                vr = self.is_vertix(xn, y)
                if vr == 1:
                  t_rem = 1
                  xn += -dnf
                  fnd = True 
                  break
                elif vr == 2:
                  
                  fnd = True
                  break
                xn += dnf
            

            if (dx, dy) in [(1, 0), (-1, 0)]:
              #print('--1--')
              while True:
                #print(x, yn)
                vr = self.is_vertix(x, yn)
                if vr == 1:
                  t_rem = 2
                  #yn += -dnf
                  fnd = True 
                  break
                elif vr == 2:
                  fnd = True
                  break
                else:
                  pass
                  #print(x, yn)
                  #print('fuck')
                  #break
                yn += dnf

            #print(xn, yn)
            
            block_x_min = min(xn, p + 1)
            block_x_max = max(xn, p + 1)

            block_y_min = min(yn, q + 1)
            block_y_max = max(yn, q + 1)

            #print(block_x_min, block_x_max, block_y_min, block_y_max)

            is_vrtx_cnt = 0
            for i in range(block_x_min, block_x_max + 1):
              for j in range(block_y_min, block_y_max + 1):
                vr = self.is_vertix(i, j)
                if vr > 0:
                  is_vrtx_cnt += 1
                if is_vrtx_cnt >= 2:
                  break
              if is_vrtx_cnt >= 2:
                  break

            #print(is_vrtx_cnt)
            #print('nooo'*10)

            if is_vrtx_cnt <= 1:
              #print(dx, dy)
              #print(t_rem)
              #print(block_x_min, block_x_max, block_y_min, block_y_max)
              #print(dnf)

              if t_rem == 1:
                xn -= dnf
                block_x_min = min(xn, p + 1)
                block_x_max = max(xn, p + 1)

                block_y_min = min(yn, q + 1)
                block_y_max = max(yn, q + 1)
              elif t_rem == 2:
                yn -= dnf
                block_x_min = min(xn, p + 1)
                block_x_max = max(xn, p + 1)

                block_y_min = min(yn, q + 1)
                block_y_max = max(yn, q + 1)
                #print(xn, yn)

              for i in range(block_x_min, block_x_max + 1):
                for j in range(block_y_min, block_y_max + 1):
                  #print(i, j)
                  self.grid[i][j] = 0
                  self.black_cells.remove((i, j))
              return True
            else:
              return False

    def check_interior(self, p, q):
      dir = [(0, 1), (1, 0), (0, -1), (-1, 0)]
      for d in dir:
        if self.grid[p + d[0], q + d[1]] != 1:
          return False
      return True

    def generate(self, n):
        r = n // 2 - 2
        kl = 0
        while r > 0:
            inter_clock = 0
            while True:
                p, q = random.choice(list(self.black_cells))#p, q = random.randint(1, self.grid_size - 3), random.randint(1, self.grid_size - 3)
                inter_clock += 1
                if inter_clock >= 4:
                  self.inflate(p, q)
                  inter_clock = 0
                if self.grid[p, q] == 1 and self.check_interior(p, q):
                    #self.display_grid()
                    self.inflate(p, q)

                    cdrf = deepcopy(self.grid)
                    
                    if self.cut(p, q):
                        #self.display_grid(cdrf)
                        #self.display_grid(self.grid)
                        break
                    else:
                      pass
                        #self.display_grid(cdrf)
                    
                    #print('=' * 200)
                    kl += 1
                    if kl > 5:
                        break
                if kl > 5:
                    break
            r -= 1

    def display_grid(self, grid):
        plt.imshow(grid, cmap='Greys', interpolation='nearest')
        plt.grid(True, which='both', color='black', linestyle='-', linewidth=0.5)
        plt.xticks(np.arange(-.5, len(grid), 1), [])
        plt.yticks(np.arange(-.5, len(grid), 1), [])
        plt.show()

# def main():
#     n = 15  # Desired number of vertices (must be even and ≥ 4)
#     grid_size = 50 # Create a grid that can accommodate the polygon
#     polygon = OrthogonalPolygon(grid_size)
#     polygon.generate(n)
#     ##polygon.display_grid(polygon.grid)

def find_outer_boundary_opt(grid):
    boundary = []
    directs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    for i in range(len(grid)):
        for j in range(len(grid)):
            if grid[i, j] != 1:
                continue
            
            for l, d in enumerate(directs):
                if grid[i + d[0], j + d[1]] != 1:
                    if l == 0:
                        boundary.append((i + 1, j + 1))
                        boundary.append((i, j + 1))
                    elif l == 1:
                        boundary.append((i + 1, j + 1))
                        boundary.append((i + 1, j))
                    elif l == 2:
                        boundary.append((i + 1, j))
                        boundary.append((i, j))
                    elif l == 3:
                        boundary.append((i, j + 1))
                        boundary.append((i, j))
                        
    return boundary
            
            
        

def get_orthog_polygon_n(n=15):
  #grid_size = 20
  #grid = np.zeros((grid_size, grid_size))

  #print('ok2')
  #n = 15  # Desired number of vertices (must be even and ≥ 4)
  grid_size = 150 # Create a grid that can accommodate the polygon
  polygon = OrthogonalPolygon(grid_size)
  polygon.generate(n)
  #print(polygon.grid)
    
  boundary = find_outer_boundary_opt(polygon.grid)
  print('ok3')
  #print(boundary)
  #boundary = expand_ones(boundary)
  s_bound = sort_ortho_poly(boundary)
  
  print('ok4')

  non_col = remove_collinear_vertices(s_bound)
  print('ok5')
  
  new_non_col = []
  
  x_min = non_col[0][0]
  y_min = non_col[0][1]
  for k, v in non_col:
      x_min = min(x_min, k)
      y_min = min(y_min, v)
      
      
  print(non_col)
  
  for k, v in non_col:
      new_non_col.append(((k - x_min) * 10 + 50, (v - y_min) * 10 + 50))
      
  print(new_non_col)

  return new_non_col