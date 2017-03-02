#!/usr/bin/python
# -*- coding: utf-8 -*-
import bottle
import json
import heapq
import random
import copy
import os

# taunts madafaka

taunts = ['I am the one', 'Hisssssss', 'Eaat all the appppllles', 'My dad gave me a small loan of a million dollars']

tauntsLength = len(taunts) - 1

false = False
true = True
null = None

######

snakeName = 'nebuchadnezzar'
snakeId = '98835e3e-c861-41c0-88aa-98d58fce2fef'
directions = {
    (-1, 0): 'left',
    (1, 0): 'right',
    (0, -1): 'up',
    (0, 1): 'down',
    }

trapSamples = 20
idlePathSamples = 20


# priority queue class and its functions

class PriorityQueue:

    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def enqueue(self, element, priority):
        heapq.heappush(self.elements, (priority, element))

    def dequeue(self):
        return heapq.heappop(self.elements)[1]


# define previous position i.e. path snake came from
# this also reverses the path given by A star algorithm

def pathCameFrom(cameFrom, goal):
    goTo = {goal: None}
    start = goal
    while cameFrom[start]:
        goTo[cameFrom[start]] = start
        start = cameFrom[start]
    return Path(goTo, start)


class Path:

    def __init__(self, goTo, start):
        self.goTo = goTo
        self.start = start

    def direction(self):
        nxt = self.goTo[self.start]
        return (nxt[0] - self.start[0], nxt[1] - self.start[1])


## grid below is used to avoid obstructions

class Grid:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cells = [[0 for y in range(height)] for x in range(width)]

    # Finds a random, unobstructed cell on the grid

    def random(self):
        cell = None
        while cell == None or self.obstructed(cell):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            cell = (x, y)
        return cell

    # Checks if the grid contains a cell

    def contains(self, cell):
        return cell[0] >= 0 and cell[1] >= 0 and cell[0] < self.width \
            and cell[1] < self.height

    # Obstructs a cell on the grid

    def obstruct(self, cell):
        if self.contains(cell):
            self.cells[cell[0]][cell[1]] = 1

    # Checks if a cell on the grid is obstructed

    def obstructed(self, cell):
        return self.cells[cell[0]][cell[1]] == 1

    # Heuristic for pathfinding, not currently used for anything
    # most likely use it to represent risk

    def heuristic(self, cell):
        return self.cells[cell[0]][cell[1]]

    # Finds neighbours to a cell on the grid

    def neighbours(self, cell):
        neighbours = []
        for direction in directions:
            neighbour = (cell[0] + direction[0], cell[1] + direction[1])

            # Check if on grid, and not obstructed

            if self.contains(neighbour) \
                and not self.obstructed(neighbour):
                neighbours.append(neighbour)

        return neighbours


### function needed for the snake are defined below

## calculate manhattan distance

def manDist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# A* search, uses grid's heuristic

def aStar(grid, start, goal):
    frontier = PriorityQueue()
    frontier.enqueue(start, 0)
    cameFrom = {start: None}
    costSoFar = {start: 0}

    while not frontier.empty():
        current = frontier.dequeue()
        if current == goal:
            return pathCameFrom(cameFrom, goal)

        for neighbour in grid.neighbours(current):
            cost = costSoFar[current] + grid.heuristic(neighbour)

            if neighbour not in costSoFar or cost \
                < costSoFar[neighbour]:
                costSoFar[neighbour] = cost
                priority = cost + manDist(neighbour, goal)
                frontier.enqueue(neighbour, priority)
                cameFrom[neighbour] = current
    return False


# function to find whether our snake's position is better than the competing snakes

def isPositionBetter(
    grid,
    snake,
    current,
    pathTo,
    to,
    ):

    # Passes

    currentPasses = 0
    toPasses = 0

    # New grid

    toGrid = copy.deepcopy(grid)

    # Loop over path and count

    curr = current
    count = 0
    while pathTo.goTo[curr]:  #
        curr = pathTo.goTo[curr]
        count += 1

    x = len(snake['coords']) - count
    while x > 0:
        toGrid.obstruct(snake['coords'][x - 1])
        x -= 1

    if len(snake['coords']) >= count:
        curr = current
        curr = pathTo.goTo[curr]
        while curr:
            toGrid.obstruct(curr)
            curr = pathTo.goTo[curr]
    else:
        curr = current
        curr = pathTo.goTo[curr]
        index = 0
        while curr:
            if index >= count - len(snake['coords']):
                toGrid.obstruct(curr)
            curr = pathTo.goTo[curr]
            index += 1

    for _ in range(trapSamples):
        goal = grid.random()
        if aStar(grid, current, goal):
            currentPasses += 1
        if aStar(toGrid, to, goal):
            toPasses += 1
    return toPasses < currentPasses


###### server shit down here

@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


# code to give link for pictures and shit

@bottle.get('/')
def index():
    head_url = '%s://%s/static/head.jpg' \
        % (bottle.request.urlparts.scheme,
           bottle.request.urlparts.netloc)

    return {'color': '#00ff00', 'head': head_url}


@bottle.post('/start')
def start():
    
    # TODO: Do things with data
    return {
        'taunt':'Hissssssssssss'
    }


@bottle.post('/move')
def move():
    data = bottle.request.json

    #data = data['data'];

    # TODO: Do things with data

    move = None
    ourSnake = None

     # Find our snake

    for snake in data['snakes']:
        if snake['id'] == snakeId:
            ourSnake = snake
            break

    print(ourSnake);

    grid = Grid(data['width'], data['height'])  # makes base grid
    for snake in data['snakes']:  # sorts through snakes
        for coord in snake['coords']:  # get all snake coords
            grid.obstruct(tuple(coord))  # make obstructions
        if snake['id'] != snakeId:  # if snake is not our snake
            for direction in directions:  # make all snake heads a obstruction
                if len(snake['coords']) >= len(ourSnake['coords']):  # if other snake larger, then obstruct where it can move to
                    head = snake['coords'][0]  #
                    movement = (head[0] + direction[0], head[1]
                                + direction[1])  #
                    grid.obstruct(movement)  #

    # -------GET FOODS

    possibleFoods = []
    for food in data['food']:
        dist = manDist(tuple(ourSnake['coords'][0]), tuple(food))
        skip = False
        for snake in data['snakes']:
            if snake['id'] != snakeId \
                and manDist(tuple(snake['coords'][0]), tuple(food)) \
                <= dist:
                skip = True
                break
        if not skip:
            possibleFoods.append(tuple(food))

    # -------GET CLOSEST FOOD

    closestFoodDist = 0
    closestFood = None
    for food in possibleFoods:
        d = manDist(tuple(ourSnake['coords'][0]), food)
        if d < closestFoodDist or closestFood == None:
            closestFood = food
            closestFoodDist = d
    idle = False

    if closestFood != None:
        path = aStar(grid, tuple(ourSnake['coords'][0]), closestFood)
        if path != False and not isPositionBetter(grid, ourSnake,
                tuple(ourSnake['coords'][0]), path, closestFood):
            move = directions[path.direction()]
        else:
            idle = True
    else:
        idle = True

    # ------IDLE MOVEMENTS

    simpleMovements = False
    if idle:
        path = False
        ind = 0
        while not path and ind < idlePathSamples:
            goal = grid.random()
            tmpPath = aStar(grid, tuple(ourSnake['coords'][0]), goal)
            if tmpPath != False and not isPositionBetter(grid,
                    ourSnake, tuple(ourSnake['coords'][0]), tmpPath,
                    goal):
                path = tmpPath
            ind += 1
        if path:
            move = directions[path.direction()]
        else:
            simpleMovements = True

    if simpleMovements:
        bGrid = Grid(data['width'], data['height'])  # makes base grid
        for snake in data['snakes']:  # sorts through snakes
            for coord in snake['coords']:  # get all snake coords
                bGrid.obstruct(tuple(coord))  # make obstructions
            bbb = snake['coords'][-1]
            bGrid.cells[bbb[0]][bbb[1]] = 0

        path = False
        ind = 0
        while not path and ind < idlePathSamples:
            goal = bGrid.random()
            tmpPath = aStar(bGrid, tuple(ourSnake['coords'][0]), goal)
            if tmpPath != False:
                path = tmpPath
        if path:
            move = directions[path.direction()]

    # ------DIRECTION CHECK ***FAILSAFE***

    if move == None:
        move = 'west'

    curdir = None
    for direction in directions:
        if move == directions[direction]:
            curdir = direction
            break

    curpos = tuple(ourSnake['coords'][0])
    transpos = (curpos[0] + curdir[0], curpos[1] + curdir[1])

    if not grid.contains(transpos) or grid.obstructed(transpos):

        cGrid = Grid(data['width'], data['height'])  # makes base grid
        for snake in data['snakes']:  # sorts through snakes
            for coord in snake['coords']:  # get all snake coords
                cGrid.obstruct(tuple(coord))  # make obstructions
            bbb = snake['coords'][-1]
            cGrid.cells[bbb[0]][bbb[1]] = 0

        for direction in directions:
            if direction == curdir:
                continue
            newpos = (curpos[0] + direction[0], curpos[1]
                      + direction[1])

            if cGrid.contains(newpos) and not cGrid.obstructed(newpos):
                move = directions[direction]
                break

    return {'move': move, 'taunt': taunts[random.randint(0, tauntsLength)]}


@bottle.post('/end')
def end():
    return {
        'taunt':'Balle Balle Ho gyi'
    }

# Expose WSGI app (so gunicorn can find it)

application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'),
               port=os.getenv('PORT', '8080'))
