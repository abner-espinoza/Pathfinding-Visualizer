import pygame
import math
from queue import PriorityQueue

WIDTH = 700
WINDOW = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Pathfinding Algorithms Visualizer")

WHITE = (255, 255, 255) # Used for unaltered squares
YELLOW = (254, 254, 106) # Used for path
LIGHT_BLUE = (209, 243, 251) # Used for open squares
PAPER_BLUE = (209,232,251) # Used for lines
TURQUOISE = (138, 227, 215) # Used for closed squares
TEAL = (59, 178, 226) # Used for starting square
OCEAN_BLUE = (65, 132, 164) # Used for ending square
DARK_BLUE = (11, 54, 71) # Used for barriers

class Square:
	def __init__(self, row, col, width, total_rows):
		self.row = row
		self.col = col
		self.x = row * width
		self.y = col * width
		self.color = WHITE
		self.neighbors = []
		self.width = width
		self.total_rows = total_rows
	
	def is_open(self):
		return self.color == LIGHT_BLUE
	
	def is_closed(self):
		return self.color == TURQUOISE
		
	def get_pos(self):
		return self.row, self.col
    
	def is_barrier(self):
		return self.color == DARK_BLUE
    
	def is_start(self):
		return self.color == TEAL
        
	def is_end(self):
		return self.color == OCEAN_BLUE
	
	def is_path(self):
		return self.color == YELLOW
    
	def reset(self):
		self.color = WHITE
        
	def make_start(self):
		self.color = TEAL
    
	def make_closed(self):
		self.color = TURQUOISE
    
	def make_open(self):
		self.color = LIGHT_BLUE
    
	def make_barrier(self):
		self.color = DARK_BLUE
    
	def make_end(self):
		self.color = OCEAN_BLUE
    
	def make_path(self):
		self.color = YELLOW
        
	def draw(self, window):
		pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.width))

	def update_neighbors(self, grid):
		self.neighbors = []
		if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): # DOWN
			self.neighbors.append(grid[self.row + 1][self.col])
        
		if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # UP
			self.neighbors.append(grid[self.row - 1][self.col])
        
		if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # RIGHT
			self.neighbors.append(grid[self.row][self.col + 1])
        
		if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # LEFT
			self.neighbors.append(grid[self.row][self.col - 1])
    
	def __lt__(self, other):
		return False


def h(p1, p2):
	x1, y1 = p1
	x2, y2 = p2
	return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current, draw):
	stack = []
	while current in came_from:
		current = came_from[current]
		stack.append(current)
	
	for i in range(len(stack)):
		current = stack.pop()
		if i == 0:
			current.make_start()
		else:
			current.make_path()
		draw()


def algorithm(draw, grid, start, end):
	count = 0
	open_set = PriorityQueue()
	open_set.put((0, count, start))
	came_from = {}
	g_score = {square: float("inf") for row in grid for square in row}
	g_score[start] = 0
	f_score = {square: float("inf") for row in grid for square in row}
	f_score[start] = h(start.get_pos(), end.get_pos())
    
	open_set_hash = {start}
    
	while not open_set.empty():
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
    
		current = open_set.get()[2]
		open_set_hash.remove(current)
    
		if current == end:
			reconstruct_path(came_from, end, draw)
			end.make_end()
			return True
    
		for neighbor in current.neighbors:
			temp_g_score = g_score[current] + 1
    
			if temp_g_score < g_score[neighbor]:
				came_from[neighbor] = current
				g_score[neighbor] = temp_g_score
				f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
				if neighbor not in open_set_hash:
						count += 1
						open_set.put((f_score[neighbor], count, neighbor))
						open_set_hash.add(neighbor)
						neighbor.make_open()
						
		draw()

		if current != start:
			current.make_closed()
            
	return False


def clear_nonessential_squares(grid):
	for row in grid:
		for square in row:
			if square.is_open() or square.is_closed() or square.is_path():
				square.reset()

	return grid
	
	
def make_grid(rows, width):
	grid = []
	gap = width // rows
	for i in range(rows):
		grid.append([])
		for j in range(rows):
			square = Square(i, j, gap, rows)
			grid[i].append(square)
    
	return grid
    
    
def draw_grid(window, rows, width):
	gap = width // rows
	for i in range(rows):
		pygame.draw.line(window, PAPER_BLUE, (0, i * gap), (width, i * gap))
		for j in range(rows):
			pygame.draw.line(window, PAPER_BLUE, (j * gap, 0), (j * gap, width))


def draw(window, grid, rows, width):
	window.fill(WHITE)
    
	for row in grid:
		for square in row:
			square.draw(window)
    
	draw_grid(window, rows, width)
	pygame.display.update()
    

def get_clicked_pos(pos, rows, width):
	gap = width // rows
	y, x = pos
    
	row = y // gap
	col = x // gap
    
	return row, col
    
    
def main(window, width):
	ROWS = 50
	grid = make_grid(ROWS, width)
    
	start = None
	end = None
    
	run = True
	
	algo_counter = 0 # keeps track of whether an algorithm method has been called
	while run:
		draw(window, grid, ROWS, width)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
    
			if pygame.mouse.get_pressed()[0]:
				if algo_counter == 1:
					grid = clear_nonessential_squares(grid)
					algo_counter -= 1
					
				pos = pygame.mouse.get_pos()
				row, col = get_clicked_pos(pos, ROWS, width)
				square = grid[row][col]
				if not start and square != end:
					start = square
					start.make_start()
					
				elif not end and square != start:
					end = square
					end.make_end()
					
				elif square.is_start():
					square.reset()
					start = None
					
				elif square.is_end():
					square.reset()
					end = None
					
				else:
					if square.is_barrier():
						square.reset()
					else:
						square.make_barrier()
        
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE and start and end:
					if algo_counter == 1:
						grid = clear_nonessential_squares(grid)
						algo_counter -= 1
						
					for row in grid:
						for square in row:
							square.update_neighbors(grid)
					
					algorithm(lambda: draw(window, grid, ROWS, width), grid, start, end)
					algo_counter += 1
        
				if event.key == pygame.K_c:
					start = None
					end = None
					grid = make_grid(ROWS, width)
				if event.key == pygame.K_x:
					run = False
				if event.key == pygame.K_UP:
					grid_size_up = 0 # keeps track of grid size when pressing 'UP' key
					if ROWS == 50:
						ROWS += 20
						grid_size_up += 1
					elif ROWS == 20:
						ROWS += 30
						grid_size_up += 1
					elif ROWS == 10:
						ROWS += 10
						grid_size_up += 1
					if grid_size_up == 1:
						grid = make_grid(ROWS, width)
						start = None
						end = None
				if event.key == pygame.K_DOWN:
					grid_size_down = 0 # keeps track of grid size when pressing 'DOWN' key
					if ROWS == 70:
						ROWS -= 20
						grid_size_down += 1
					elif ROWS == 50:
						ROWS -= 30
						grid_size_down += 1
					elif ROWS == 20:
						ROWS -= 10
						grid_size_down += 1
					if grid_size_down == 1:
						grid = make_grid(ROWS, width)
						start = None
						end = None
	pygame.quit()
    
main(WINDOW, WIDTH)
