import numpy as np
import scipy.ndimage


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

def find_and_fill_black_holes(arr):
    rows, cols = arr.shape

    # Fill border-connected regions with a temporary value (2)
    for r in range(rows):
        if arr[r, 0] == 0:
            flood_fill(arr, r, 0, 2)
        if arr[r, cols-1] == 0:
            flood_fill(arr, r, cols-1, 2)
    for c in range(cols):
        if arr[0, c] == 0:
            flood_fill(arr, 0, c, 2)
        if arr[rows-1, c] == 0:
            flood_fill(arr, rows-1, c, 2)

    # Set remaining black regions (0) to white (1)
    arr[arr == 0] = 1

    # Restore border-connected regions back to black (0)
    arr[arr == 2] = 0

    return arr

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


def get_orthog_polygon():
  grid_size = 20
  grid = np.zeros((grid_size, grid_size))

  probability = 0.60
  grid = np.random.choice([0, 1], size=(grid_size, grid_size), p=[1-probability, probability])

  labeled_grid, num_features = scipy.ndimage.label(grid)
  component_sizes = np.bincount(labeled_grid.ravel())
  component_sizes[0] = 0
  largest_component_label = component_sizes.argmax()
  largest_component_mask = (labeled_grid == largest_component_label)

  arr = largest_component_mask.astype('int')
  #print('ok0')
  modified_arr = find_and_fill_black_holes(arr)
  #print('ok1')
  arr = expand_ones(arr)
  arr = expand_ones(arr)
  #arr = expand_ones(arr)
  #print('ok2')
  boundary = find_outer_boundary(arr)
  #print('ok3')
  s_bound = sort_ortho_poly(boundary)
  #print('ok4')

  non_col = remove_collinear_vertices(s_bound)
  #print('ok5')
  
  new_non_col = []
  
  x_min = non_col[0][0]
  y_min = non_col[0][1]
  for k, v in non_col:
      x_min = min(x_min, k)
      y_min = min(y_min, v)
      
      
  print(non_col)
  
  for k, v in non_col:
      new_non_col.append(((k - x_min) * 20 + 50, (v - y_min) * 20 + 50))
      
  print(new_non_col)

  return new_non_col