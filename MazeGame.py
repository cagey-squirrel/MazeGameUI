import pygame
import sys

pygame.init()

#screen

SCREEN_HEIGHT = 600
WIDTH = 500
HEIGHT = 500
screen = pygame.display.set_mode((WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("MazeGame")

#colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

#mouse
mouse_pos_x = 0
mouse_pos_y = 0
BL = False #Left button pressed
BR = False #Right button pressed


#Game
solve_the_maze = False
boxsize = 20
size = 25
vertices_num = size*size
run = True
fps = pygame.time.Clock()
res = [ [ 0 for i in range(size) ] for j in range(size) ]
Font = pygame.font.SysFont("Cherish Today", 50, False)
text_print = Font.render("Solve the Maze", 1, BLACK)

# Getting the position of the mouse and whether right or left button has been clicked
def mouseAction(mouse_pos_x, mouse_pos_y, BL, BR):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        (mouse_pos_x, mouse_pos_y) = pygame.mouse.get_pos()
        (BL, BM, BR) = pygame.mouse.get_pressed()
    return(mouse_pos_x, mouse_pos_y, BL, BR)

#Drawing vertical and horizontal lines as well as the "Solve the Maze" button
#Drawing white boxes for obstacles, red for path and blue for start and exit point
def draw():
    for i in range(size):
        pygame.draw.line(screen, WHITE,(boxsize*i, 0), (boxsize*i, HEIGHT))
    for i in range(size):
        pygame.draw.line(screen, WHITE,(0, boxsize*i), (WIDTH, boxsize*i))
    pygame.draw.rect(screen, GREEN, (0, 500, 500, 100))
    screen.blit(text_print, (130, 525))
    for i in range(size):
        for j in range(size):
            if res[i][j] == 1:
                pygame.draw.rect(screen, WHITE, (i * boxsize, j * boxsize, boxsize, boxsize))
            if res[i][j] == 3:
                pygame.draw.rect(screen, RED, (i * boxsize, j * boxsize, boxsize, boxsize))
            if res[i][j] == 4:
                pygame.draw.rect(screen, BLUE, (i*boxsize, j * boxsize, boxsize, boxsize))

#Detection if mouse has clicked on some of the blocks or on the "Solve the maze" button
#Left click adds obstacles and destroys edges between vertices and right click does the opposite
def clickDetection(solve_the_maze):
    if BL:
        if mouse_pos_y <= 500:
            xpos = mouse_pos_x // boxsize
            ypos = mouse_pos_y // boxsize
           # if not res[xpos][ypos] == 4:
            res[xpos][ypos] = 1
            maze.deleteEdges(xpos, ypos)
        else:
            solve_the_maze = True

    if BR and mouse_pos_y <= 500:
        xpos2 = mouse_pos_x // boxsize
        ypos2 = mouse_pos_y // boxsize
        maze.addEdges(xpos2, ypos2)
        res[xpos2][ypos2] = 0

    return solve_the_maze

class Maze(object):
    def __init__(self):
        self.maze = []
        for i in range(4*vertices_num):
            self.maze.append(0)
        self.enterX = 0
        self.enterY = 0
        self.exitX = 23
        self.exitY = 23
    
    #In starting position every vertex is connected to its neighbors: left, right, up and down but only if they exist
    #We make room for every vertex to have 4 neighbors and store them as bools
    def makeEdges(self):
        for i in range(vertices_num):
            ypos = i // size
            xpos = i % size
            if xpos > 0:
                self.maze[i*4] = 1
            if xpos < size-1:
                self.maze[i*4+1] = 1
            if ypos > 0:
                self.maze[i*4+2] = 1
            if ypos < size - 1:
                self.maze[i*4+3] = 1
    
    #When we delete the edge from node A to node B we also have to delete Edge from node B to node A
    def deleteEdges(self, xpos, ypos):
        i = ypos*size + xpos #index of the node with given position
        if xpos > 0:
            self.maze[i * 4] = 0
            self.maze[(i-1)*4+1] = 0
        if xpos < size - 1:
            self.maze[i * 4 + 1] = 0
            self.maze[(i+1)*4] = 0
        if ypos > 0:
            self.maze[i * 4 + 2] = 0
            self.maze[(i-size)*4 + 3] = 0
        if ypos < size - 1:
            self.maze[i * 4 + 3] = 0
            self.maze[(i+size)*4 + 2] = 0
    
    #Also when we add edge from vertex A to vertex B we also need to add an edge from B to A
    def addEdges(self, xpos, ypos):
        i = ypos*size + xpos
        if xpos > 0:
            self.maze[i * 4] = 1
            self.maze[(i-1)*4+1] = 1
        if xpos < size - 1:
            self.maze[i * 4 + 1] = 1
            self.maze[(i+1)*4] = 1
        if ypos > 0:
            self.maze[i * 4 + 2] = 1
            self.maze[(i-size)*4 + 3] = 1
        if ypos < size - 1:
            self.maze[i * 4 + 3] = 1
            self.maze[(i+size)*4 + 2] = 1


    #Solving the maze using Dijstra's algorithm
    def solveMaze(self):
        SDFE = [] #shortest distance from entry
        PV = [] #previous vertex
        visited = []
        unvisited_num = vertices_num

        #We reset the path every time we solve the maze
        for i in range(size):
            for j in range(size):
                if res[i][j]==3:
                    res[i][j]=0
        
        #Making distances between all nodes and starting node ~infinity
        for i in range(vertices_num):
            SDFE.append(1000000)
            visited.append(0)
            PV.append(0)
            
        #We start from first node thus we give it distance 0 (from itself) and mark it with -1 
        # which helps us in retrieving the path
        SDFE[self.enterY * size + self.enterX] = 0
        PV[self.enterY * size + self.enterX] = -1

        path_found = False

        while unvisited_num:
            
            #Finding the vertex with min distance from the starting one
            min = 1000100
            min_index = 0
            for i in range(vertices_num):
                if (SDFE[i] < min and not visited[i]):
                    min = SDFE[i]
                    min_index = i

            #For that vertex visit all unvisited neighbors and if the distance to them is shorter than the original
            #update SDFE and PV
            #If we want to update the distance to left neighbor(LN) using the node A, the index of LN is
            #one smaller than index of A (one bigger for right naighboor)
            #For up and down neighbors the difference in indexes is +/- size
            for i in range(4):
                if self.maze[min_index*4 + i]:
                    shift = -(not i) + (i==1) - size*(i==2) + size*(i==3)
                    if not visited[min_index+shift]:
                        if SDFE[min_index+shift] > SDFE[min_index]:
                            SDFE[min_index + shift] = SDFE[min_index] + 1
                            PV[min_index + shift] = min_index

                            if min_index + shift == self.exitY * size + self.exitX:
                                path_found = True
            visited[min_index] = True
            unvisited_num -= 1
            if path_found:
                break

        #If path is found we go iterate back from the exit node to the first node and make a path
        if not path_found:
            print("No path found")
        else:
            current = PV[self.exitX + self.exitY*size]
            while current != -1:
                i = current % size
                j = current // size
                if ( not (j == self.enterY and i == self.enterX)):
                    res[i][j] = 3
                current = PV[current]


maze = Maze()
maze.makeEdges()
coordinates_given = False
while run:
    mouse_pos_x, mouse_pos_y, BL, BR = mouseAction(mouse_pos_x, mouse_pos_y, BL, BR)
    solve_the_maze = clickDetection(solve_the_maze)

    draw()
    pygame.display.update()
    screen.fill(BLACK)
    fps.tick(60)

    if solve_the_maze:
        maze.solveMaze()
        solve_the_maze = False

    if not coordinates_given:
        maze.enterX = int(input("Enter the X coordinate of starting position "))
        maze.enterY = int(input("Enter the Y coordinate of starting position "))
        maze.exitX = int(input("Enter the X coordinate of exit position "))
        maze.exitY = int(input("Enter the Y coordinate of exit position "))
        res[maze.enterX][maze.enterY] = 4
        res[maze.exitX][maze.exitY] = 4
        coordinates_given = True
