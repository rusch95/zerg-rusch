import copy
import random
import heapq
import time
import curses
from collections import deque
from collections import defaultdict

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
    gate = '8'
    wall = '1'
    unex_wall = '|'  
    blank = '.'
    goal = '9'
    agent = '@'
    no_pass = [gate, wall, unex_wall]
    
    agent_positions = {}
    agent_goals = {}
    
        
    def __init__(self, debug=True):
        self.level = self.generate()
        self.hidden = self.hide()
        self.goalpos = self.init_goal()
        self.time = 0
        self.display_init(debug)

        
    def replace_symbols(self, original, new):
        '''Iterates through the level 
        replacing old symbol with new''' 
        for y in range(self.len_y):
            for x in range(self.len_x):
                if self.level[y][x] == original:
                    self.level[y][x] = new
                    self.hidden[y][x] = new
    
    def dist(self, a, b):
        y1, x1 = a
        y2, x2 = b
        return ((y1 - y2) ** 2 + (x1 - x2) ** 2) ** .5
    
    def mod_dist(self, x2, y2, ignore_agent):        
        total_dist = 0
        no_div_zero = 1
        g_falloff = 1
        g_weight = 100
        p_falloff = 1
        p_weight = 10
        cur = (y2, x2)
        for agent in self.agent_goals:
            if agent != ignore_agent:
                goal = self.agent_goals[agent]
                dist = self.dist(goal, cur)
                total_dist += g_weight / (dist + no_div_zero) ** g_falloff
        for agent in self.agent_positions:
            if agent != ignore_agent:
                pos = self.agent_positions[agent]
                dist = self.dist(pos, cur)
                total_dist += p_weight / (dist + no_div_zero) ** p_falloff
                
            
            
        return total_dist

      
    def agent_conc(self, falloff=-1):
        
        return [[self.mod_dist(i, j) for i in range(self.len_x)] for j in range(self.len_y)]
        
          
    def generate(self, default=True):
        '''Generates map in form of 2D array'''
        
        text_file = open('testWorld.txt')
        level = []
        for line in text_file:
            level.append([char for char in line if char != '\n'])       
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
    
    
    def is_in_level(self, position):
        (y, x) = position
        return not (y < 0 or x < 0 or y >= self.len_y or x >= self.len_x)

    
    
    
class Agent:
    '''
    AI Agent Base Class
    '''
    
    radio_queue = None
    busy = False
    neighbors = 0
    destroy_mode = False
    
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
        self.walk_queue = self.pathfind(self.world.hidden, goal)
    
    
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
                    
                if self.world.level[y][x] == 5:
                    seen.append(5)
                    
                if self.world.level[y][x] == 8:
                    seen.append(8)
                
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
    
    
    def distance(self, a, b):
        (y1, x1) = a
        (y2, x2) = b
        return ((x1 -x2)**2 + (y1 - y2)**2)**.5
    
    
    def pathfind(self, level, goal, isLoc=True, shy=True):
        '''
        Currently explores based on valid moveable area.
        Could be changed to have no level information.
        '''
        frontier = PriorityQueue()
        frontier.put(self.position, 0)
        came_from = {}
        cost_so_far = {}
        came_from[self.position] = None
        cost_so_far[self.position] = 0
        hit_goal = False
        self.world.screen.addstr(28,0, 'Nope')
        
        while not frontier.empty():
            current = frontier.get()
            
            if isLoc:
                if current == goal:
                    hit_goal = True
                    break
            else:
                for suc in self.valid_neighbors(current):
                    (y, x) = suc
                    if level[y][x] == str(goal):                   
                        hit_goal = True
                        goal = current
                        self.world.agent_goals[self.name] = goal
                        break
        
            for suc in self.succesor(current):
                new_cost = cost_so_far[current] + self.distance(current, suc)
                if suc not in cost_so_far or new_cost < cost_so_far[suc]:
                    cost_so_far[suc] = new_cost
                               
                    if True:
                        dist = self.distance(self.world.goalpos, suc)
                    else:
                        dist = 0
                    if shy:
                        shyness = self.world.mod_dist(suc[0],suc[1],self.name)
                    else:
                        shyness = 0
                        
                    priority = new_cost + dist + shyness
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

    
    def valid_neighbors(self, position, inc_self=False):
        ret_list = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0 and not inc_self:
                    continue
                y = position[0] + i
                x = position[1] + j
                if self.world.is_in_level((y, x)):
                    ret_list.append((y,x))
        return ret_list
                  
        
    def succesor(self, position):
        return [x for x in self.valid_neighbors(position) if not self.world.level[x[0]][x[1]] in self.world.no_pass]
         
        
    def destroy(self, needed=3):
        destroyed = False
        for (y,x) in self.valid_neighbors(self.position):
            if self.neighbors >= needed:
                if self.world.level[y][x] == self.world.gate:
                    self.world.level[y][x] = self.world.blank
                    self.world.hidden[y][x] = self.world.blank
                    destroyed = True
        return destroyed
    
    
    def update_neighbors(self):
        fucking_shit = self.valid_neighbors(self.position, inc_self=True)
        total = 0
        for x in self.world.agent_positions.values():
            if x in fucking_shit:
                total += 1
        self.neighbors = total    
            
    
    def seek_goal(self):
        self.pathfind(self.world.goalpos)

        
        
        
def main(delay=0):
    
    try:
        hidden = True
        debug = False
        world = World(debug)
        Agent.test = False
        bob = Agent(world, name='Bob', position=(7,7))
        chuck = Agent(world, name='Chuck', position=(7,0))
        dave = Agent(world,name='Dave', position=(8,4))

        world.replace_symbols(0, '.')
    
        agents = [bob, chuck, dave]

        #for agent in agents:
        #    agent.goto(world.goalpos)
        while True:
            for agent in agents:
                
                world.inc_time()
                agent.update_neighbors()
                agent.walk()            
                
                if agent.radio_queue:
                    
                    if agent.radio_queue == 'Clear':
                        agent.busy = False
                    
                    elif not agent.busy:
                        agent.busy = True
                        agent.goto(agent.radio_queue)
                        agent.radio_queue = []
            
                if not agent.walk_queue and not agent.busy:
                    for thing in [world.goal, world.unex_wall]:
                        path = agent.pathfind(world.hidden, thing, shy=True, isLoc=False)
                        agent.world.screen.addstr(32, 0, '                                                                                                  ')
                        agent.world.screen.addstr(32, 0, str(world.time))
                        agent.world.screen.addstr(30, 0, str(thing))
                        #path = agent.bfs_feature_find(world.hidden, thing)
                        agent.walk_queue = path
                        if path:
                            break
                        
                seen = agent.look()
                
                if '8' in seen and not agent.destroy_mode:
                    agent.destroy_mode = True
                    agent.busy = True
                    agent.call_radio(agents, agent.position)
            
                destroyed = agent.destroy()
                
                if destroyed:
                    agent.call_radio(agents, 'Clear')
                    agent.busy = False
                    agent.destroy_mode = False
                     

            world.display(hidden=True)

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

    



    
    