import copy
import random
import heapq
import time
import curses
from collections import deque

class PriorityQueue:
    
    def __init__(self):
        self.elements = []
    
    def empty(self):
        return len(self.elements) == 0
    
    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))
    
    def get(self):
        return heapq.heappop(self.elements)[1]    
    
class World:
    '''
    Serves as the maze enviroment. Other Stuff as well.
    '''
    
    #Default Symbol Variables
    gate = 8
    wall = 1
    unex_wall = '|'  
    blank = '.'
    goal = 9
    agent = '@'
    no_pass = [gate, wall, unex_wall]
    
    agent_positions = {}
    
        
    def __init__(self,debug=True):
        self.level = self.generate()
        self.hidden = self.hide()
        self.goalpos = self.init_goal()
        self.time = 0
        self.display_init(debug)

        
    def replace_symbols(self, original, new):
        '''
        Iterates through the level 
        replacing old symbol with new
        '''
        
        for y in range(self.len_y):
            for x in range(self.len_x):
                if self.level[y][x] == original:
                    self.level[y][x] = new
                    self.hidden[y][x] = new
        
    
    def generate(self, default=True):
        '''Generates map in form of 2D array'''
        
        text_file = open('testWorld.txt')
        level = []
        for line in text_file:
            level.append([int(char) for char in line if char != '\n'])
        '''
        level = [[9,0,0,0,0,0,0,0,8,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [1,1,1,1,1,1,1,1,1,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,1,0,1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,1,1,8,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,1,1,1,1,8,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
        '''              
                
        self.len_y = len(level)
        self.len_x = len(level[0])
    
        return level      

    
    def hide(self):
        '''
        Processes map to produce altered map with no_pass elements hidden
        as other symbol such a unex_wall symbol
        '''
    
        level_copy = copy.deepcopy(self.level)
        for y in range(self.len_y):
            for x in range(self.len_x):
                if level_copy[y][x] in self.no_pass:
                    level_copy[y][x] = self.unex_wall
        return level_copy               
    
    
    def init_goal(self):
        '''Assumes one goal'''
        for y in range(self.len_y):
            for x in range(self.len_x):
                if self.level[y][x] == self.goal:
                    return (y,x)
                
    
    def wall_destroy(self, position):
        y = position[0]
        x = position[1]
        if self.level[y][x] == self.gate:
            self.level[y][x] = self.blank
            self.hidden[y][x] = self.blank

    
    def display_init(self, debug=True):
        if not debug:
            self.cursed = True
            self.screen = curses.initscr()
            
        if debug:
            self.cursed = False
    
    
    def display(self, hidden=False):
        if self.cursed:
            level = self.level
            if hidden:
                level = self.hidden
            for y in range(self.len_y):
                for x in range(self.len_x):
                    temp_char = level[y][x]
                    if (y, x) in self.agent_positions.values():
                        temp_char = self.agent
                    self.screen.addstr(y,x*2,(str(temp_char)))
                            
            self.screen.refresh()
            
        
        if not self.cursed:
            level = self.level
            if hidden:
                level = self.hidden
            for y in range(self.len_y):
                for x in range(self.len_x):
                    temp_char = level[y][x]
                    if (y, x) in self.agent_positions.values():
                        temp_char = self.agent
                    print temp_char,
                print 
            print
        
        
    def inc_time(self):
        self.time += 1
    
    
    def time(self):
        return self.time
    
    
    def is_in_level(self, position):
        (y, x) = position
        return not (y < 0 or x < 0 or y >= self.len_y or x >= self.len_x)

    
    
    
class Agent:
    '''
    AI Agent
    '''
    
    radio_queue = None
    busy = False
    
    def __init__(self, world, name=None, position=(0,0)):
        #Upright corner origin. (y, x)
        
        #Implement position error checking
        self.position = position
        if name is None:
            self.name = random.random()
        self.name = name
        self.world = world
        world.agent_positions[name] = position
        self.walk_queue = []
    
    def move(self, new_pos):
        new_y = new_pos[0]
        new_x = new_pos[1]
        
        if 0 > new_y or 0 > new_x or self.world.len_y < new_y or self.world.len_x < new_x:
            #poss change to error
            return
        
        if self.world.level[new_y][new_x] in self.world.no_pass:
            #poss change to error
            return
        
        old_y = self.position[0]
        old_x = self.position[1]
        
        if abs(new_y - old_y) <= 1 and abs(new_x - old_x) <= 1:
            self.position = (new_y, new_x)
            self.world.agent_positions[self.name] = self.position  
        else:
            # poss change to error
            return
    
    
    def goto(self, goal):
        self.walk_queue = self.pathfind(goal)
    
    
    def walk(self):
        if self.walk_queue:
            self.test = not self.test
            if self.walk_queue[0] in self.world.agent_positions:
                self.walk_queue = []
                return
            self.move(self.walk_queue.pop(0))
    
    
    def look(self):
        seen = []
        for i in range(-1,2):
            for j in range(-1,2):
                y = self.position[0] + j
                x = self.position[1] + i 
                if not self.world.is_in_level((y,x)):
                    continue
                elif self.world.level[y][x] == self.world.gate:
                    self.world.hidden[y][x] = self.world.gate
                    seen.append(self.world.gate)
                elif self.world.level[y][x] == self.world.wall:
                    self.world.hidden[y][x] = self.world.wall
                elif self.world.level[y][x] == 5:
                    seen.append(5)
        return seen
        
        
    def check_radio(self):
        if self.radio_queue == 'Clear':
            busy = False
        if self.radio_queue:
            busy = True
            return self.radio_queue
    
    
    def call_radio(self, agents, message):
        for agent in agents:
            agent.radio_queue = message
    
    
    def asssist(self):
        pass
    
    
    def distance(self, a, b):
        (y1, x1) = a
        (y2, x2) = b
        return ((x1 -x2)**2 + (y1 - y2)**2)**.5
    
    
    def pathfind(self, goal):
        '''Uses a*'''
        frontier = PriorityQueue()
        frontier.put(self.position, 0)
        came_from = {}
        cost_so_far = {}
        came_from[self.position] = None
        cost_so_far[self.position] = 0
        hit_goal = False
        
        while not frontier.empty():
            current = frontier.get()
        
            if current == goal:
                hit_goal = True
                break
        
            for suc in self.succesor(current):
                new_cost = cost_so_far[current] + self.distance(current, suc)
                if suc not in cost_so_far or new_cost < cost_so_far[suc]:
                    cost_so_far[suc] = new_cost
                    priority = new_cost + self.distance(goal, suc)
                    frontier.put(suc, priority)
                    came_from[suc] = current
    
        if not hit_goal:
            return None
        current = goal
        path = [current]
        while current != self.position:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

    
    def valid_neighbors(self, position):
        ret_list = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                y = position[0] + i
                x = position[1] + j
                if self.world.is_in_level((y, x)):
                    ret_list.append((y,x))
        return ret_list
                
    
    def bfs_feature_find(self, level, feature):
        start = self.position
        parent = {}
        parent[start] = None
        queue = deque()
        queue.append(start)
        found_it = False
        
        while queue:
            current = queue.popleft()
            for n in self.succesor(current):           
                if n not in parent:
                    parent[n] = current
                    for neigh in self.valid_neighbors(n):
                        (y, x) = neigh
                        if level[y][x] == feature:
                            found_it = True
                            queue.append(n)
                            break
                    if found_it:
                        break
                    queue.append(n)
            if found_it:
                break
        if not found_it:
            return None
            
        current = n
        path = [current]
        while current != start:
            current = parent[current]
            path.append(current)
        path.reverse()
        return path 
        
        
    
    def succesor(self, position):
        rtn = []
        cur_y = position[0]
        cur_x = position[1]
        for i in range(-1, 2):
            for j in range(-1, 2):
                new_y = cur_y + i
                new_x = cur_x + j
                
                if i == 0 and j == 0:
                    continue
                if 0 > new_y or 0 > new_x:
                    continue
                if self.world.len_y < new_y or self.world.len_x < new_x:
                    continue
                try:
                    if self.world.level[new_y][new_x] in self.world.no_pass:
                        continue
                except:
                    continue
                else:
                    rtn.append((new_y, new_x))
        return rtn
                        
    def destroy(self):
        for (y,x) in self.valid_neighbors(self.position):
            if self.world.level[y][x] == self.world.gate:
                self.world.level[y][x] = self.world.blank
                self.world.hidden[y][x] = self.world.blank
    
    def seek_goal(self):
        self.pathfind(self.world.goalpos)

def main(delay=.1):
    
    try:
        hidden = True
        debug = False
        world = World(debug)
        Agent.test = False
        bob = Agent(world, name='Bob', position=(7,7))
        chuck = Agent(world, name='Chuck', position=(7,0))
        dave = Agent(world,name='Dave', position=(7,1))

        world.replace_symbols(0, '.')
    
        agents = [bob, chuck, dave]
        #for agent in agents:
        #    agent.goto(world.goalpos)
        flag = True
        while True:
            for agent in agents:
            
                agent.walk()
                
                if agent.radio_queue and not agent.busy:
                    agent.busy = True
                    agent.goto(agent.radio_queue)
            
                if not agent.walk_queue:
                    for thing in [world.goal, world.unex_wall]:
                        path = agent.bfs_feature_find(world.hidden, thing)
                        agent.walk_queue = path
                        if path:
                            break
                        
                seen = agent.look()
                if 5 in seen and flag:
                    flag = False
                    agent.call_radio(agents, agent.position)
            
                agent.destroy()

            world.display(hidden=True)
            world.inc_time()

            time.sleep(delay)
            
    except:
        
        if not debug:
            curses.nocbreak()
            world.screen.keypad(0)
            curses.echo()
            curses.endwin()
        raise
        
if __name__ == '__main__':
    main(delay=0.1)



    
    