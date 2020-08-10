import pygame
import sys
from timeit import default_timer as timer
import os

os.environ['SDL_VIDEO_CENTERED'] = '1'

pygame.init()

# screen

SCREEN_HEIGHT = 600
WIDTH = 500
HEIGHT = 500
screen = pygame.display.set_mode((WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("MazeGame")

# colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (128, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 247, 0)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)

# mouse
mouse_pos_x = 0
mouse_pos_y = 0
BL = True  # Left button pressed
BR = True  # Right button pressed

# Game
solve_the_maze = True
boxsize = 20
size = 25
vertices_num = size * size
run = True
fps = pygame.time.Clock()
Font = pygame.font.SysFont("Cambria", 30, False)
textSolveWithDij = Font.render("Solve with ", 1, BLACK)
textDijstra = Font.render("Dijstra", 1, BLACK)
textSolveWithA = Font.render("Solve with", 1, BLACK)
textAstar = Font.render("A*", 1, BLACK)
useDijstra = True


# Getting the position of the mouse and whether right or left button has been clicked
def mouseAction(mouse_pos_x, mouse_pos_y, BL, BR):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        (mouse_pos_x, mouse_pos_y) = pygame.mouse.get_pos()
        (BL, BM, BR) = pygame.mouse.get_pressed()
    return (mouse_pos_x, mouse_pos_y, BL, BR)


# Detection if mouse has clicked on some of the blocks or on the "Solve the maze" button
# Left click adds obstacles and destroys edges between vertices and right click does the opposite
def clickDetection(solve_the_maze):
    global useDijstra
    if BL:
        if mouse_pos_y <= 500:
            xpos = mouse_pos_x // boxsize
            ypos = mouse_pos_y // boxsize
            maze.deleteEdges(xpos, ypos)
        else:
            if (mouse_pos_x < 250):
                useDijstra = True
            else:
                useDijstra = False
            solve_the_maze = True

    if BR and mouse_pos_y <= 500:
        xpos2 = mouse_pos_x // boxsize
        ypos2 = mouse_pos_y // boxsize
        maze.addEdges(xpos2, ypos2)

    return solve_the_maze


class Cube(object):
    def __init__(self, xpos, ypos):
        self.color = BLACK
        self.xpos = xpos
        self.ypos = ypos

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.ypos * boxsize, self.xpos * boxsize, boxsize, boxsize))


class Maze(object):
    def __init__(self):
        self.maze = [[Cube(i, j) for j in range(size)] for i in range(size)]
        self.verticalEdges = [[True for _ in range(size)] for _ in range(size - 1)]
        self.horizontalEdges = [[True for _ in range(size - 1)] for _ in range(size)]
        self.enterX = 5
        self.enterY = 8
        self.exitX = 19
        self.exitY = 23

    def draw(self):
        pygame.draw.rect(screen, GREY, (0, 500, 500, 100))
        screen.blit(textSolveWithDij, (50, 515))
        screen.blit(textDijstra, (70, 545))
        screen.blit(textSolveWithA, (300, 515))
        screen.blit(textAstar, (360, 545))
        pygame.draw.line(screen, BLACK, (250, 500), (250, 600))
        for cubes in self.maze:
            for cube in cubes:
                cube.draw()
        for i in range(size):
            pygame.draw.line(screen, WHITE, (boxsize * i, 0), (boxsize * i, HEIGHT))
        for i in range(size):
            pygame.draw.line(screen, WHITE, (0, boxsize * i), (WIDTH, boxsize * i))

    def neighborExists(self, index, i):
        xpos = index % size
        ypos = index // size
        if i == 0:  # checking left neighbor
            if (xpos == 0):
                return False
            return self.horizontalEdges[ypos][xpos - 1]

        if i == 1:  # checking right neighbor
            if (xpos == size - 1):
                return False
            return self.horizontalEdges[ypos][xpos]

        if i == 2:  # checking up neighbor
            if (ypos == 0):
                return False
            return self.verticalEdges[ypos - 1][xpos]

        if i == 3:  # checking down neighbor
            if (ypos == size - 1):
                return False
            return self.verticalEdges[ypos][xpos]

    # When we delete the edge from node A to node B we also have to delete Edge from node B to node A
    # Since we cannot reach a node with deleted edges all we have to do is delete t
    def deleteEdges(self, xpos, ypos):
        # xpos and ypos from cube
        self.maze[ypos][xpos].color = WHITE
        if xpos > 0:
            self.horizontalEdges[ypos][xpos - 1] = False
        if xpos < size - 1:
            self.horizontalEdges[ypos][xpos] = False
        if ypos > 0:
            self.verticalEdges[ypos - 1][xpos] = False
        if ypos < size - 1:
            self.verticalEdges[ypos][xpos] = False

    # Also when we add edge from vertex A to vertex B we also need to add an edge from B to A
    def addEdges(self, xpos, ypos):
        self.maze[ypos][xpos].color = BLACK
        if xpos > 0:
            self.horizontalEdges[ypos][xpos - 1] = True
        if xpos < size - 1:
            self.horizontalEdges[ypos][xpos] = True
        if ypos > 0:
            self.verticalEdges[ypos - 1][xpos] = True
        if ypos < size - 1:
            self.verticalEdges[ypos][xpos] = True

    def h(self, index):
        hxpos = index % size
        hypos = index // size
        return abs(self.exitY - hypos) + abs(self.exitX - hxpos)

    # Solving the maze using Dijstra's algorithm
    def solveMaze(self):
        start = timer()
        SDFE = []  # shortest distance from entry
        PV = []  # previous vertex
        visited = []
        unvisited_num = vertices_num

        # We reset the path every time we solve the maze
        for cubes in maze.maze:
            for cube in cubes:
                if cube.color != WHITE and cube.color != BLUE:
                    cube.color = BLACK

        maze.maze[maze.enterY][maze.enterX].color = BLUE
        maze.maze[maze.exitY][maze.exitX].color = BLUE

        # Making distances between all nodes and starting node ~infinity
        for i in range(vertices_num):
            SDFE.append(1000000)
            visited.append(0)
            PV.append(0)

        # We start from first node thus we give it distance 0 (from itself) and mark it with -1
        # which helps us in retrieving the path
        if not useDijstra:
            SDFE[self.enterY * size + self.enterX] = self.h(self.enterX + size * self.enterY)
        else:
            SDFE[self.enterY * size + self.enterX] = 0

        PV[self.enterY * size + self.enterX] = -1

        path_found = False
        numOfIterations = 0

        while unvisited_num:
            numOfIterations += 1
            # Finding the vertex with min distance from the starting one
            min = 1000100
            min_index = 0

            if useDijstra:
                for i in range(vertices_num):
                    if (SDFE[i] < min and not visited[i]):
                        min = SDFE[i]
                        min_index = i

            else:
                for i in range(vertices_num):
                    if (SDFE[i] + self.h(i) < min and not visited[i]):
                        min = SDFE[i] + self.h(i)
                        min_index = i

            for i in range(4):
                if self.neighborExists(min_index, i):
                    shift = -(not i) + (i == 1) - size * (i == 2) + size * (i == 3)
                    adjacentNode = min_index + shift
                    if not visited[adjacentNode]:
                        self.maze[adjacentNode // size][adjacentNode % size].color = YELLOW
                        if not useDijstra:
                            if SDFE[adjacentNode] + self.h(adjacentNode) > SDFE[min_index] + 1 + self.h(min_index):
                                SDFE[adjacentNode] = SDFE[min_index] + 1
                                PV[adjacentNode] = min_index
                                if adjacentNode == self.exitY * size + self.exitX:
                                    path_found = True

                        else:  # use Dijstra
                            if SDFE[adjacentNode] > SDFE[min_index] + 1:
                                SDFE[adjacentNode] = SDFE[min_index] + 1  # Regular Dijstra
                                PV[adjacentNode] = min_index
                                if adjacentNode == self.exitY * size + self.exitX:
                                    path_found = True
            visited[min_index] = True
            self.maze[min_index // size][min_index % size].color = RED
            unvisited_num -= 1
            if path_found:
                break

        # If path is found we go iterate back from the exit node to the first node and make a path
        distance = 0
        if not path_found:
            print("No path found")
        else:
            current = PV[self.exitX + self.exitY * size]
            while current != -1:
                j = current // size
                i = current % size
                if (not (j == self.enterY and i == self.enterX)):
                    self.maze[j][i].color = GREEN
                    distance += 1
                current = PV[current]

        maze.maze[maze.enterY][maze.enterX].color = BLUE
        maze.maze[maze.exitY][maze.exitX].color = BLUE

        end = timer()
        if useDijstra:
            print('Time elapsed using Dijstra: ', (end - start) * 1000)
        else:
            print('Time elapsed using A*: ', (end - start) * 1000)
        print(numOfIterations)
        print(distance)
        print()


maze = Maze()


coordinates_given = False
solve_the_maze = False



while run:
    mouse_pos_x, mouse_pos_y, BL, BR = mouseAction(mouse_pos_x, mouse_pos_y, BL, BR)
    solve_the_maze = clickDetection(solve_the_maze)
    maze.draw()
    pygame.display.update()
    screen.fill(BLACK)
    fps.tick(60)
    if solve_the_maze:
      maze.solveMaze()
      solve_the_maze = False
    if not coordinates_given   :
       maze.enterX = int(input("Enter the X coordinate of starting position "))
       maze.enterY = int(input("Enter the Y coordinate of starting position "))
       maze.exitX =  int(input("Enter the X coordinate of exit position "))
       maze.exitY = int(input("Enter the Y coordinate of exit position "))
       maze.maze[maze.enterY][maze.enterX].color = BLUE
       maze.maze[maze.exitY][maze.exitX].color = BLUE
       coordinates_given = True
