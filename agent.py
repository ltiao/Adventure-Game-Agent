#!/usr/bin/python

import socket, sys, optparse, json, heapq

# TODO:
# 1. Make State immutable
#   a. global_map to be encapsulated by another class, states to have reference to that class
# 2. Finish implementing action_is_effective()
# 3. Generate child states from current state with action_is_effective()
# 4. Implement A*/Uniform cost search
#   a. Implement manhattan distance (?) heuristic + number of tools
# 5. Search priority:
#   a. If have gold, move to start position
#   b. If not, look for gold
#   c. If not, look for tools
#   d. Else, look for nearest '?'

# Constants
GLOBAL_MAX_WIDTH = 20
GLOBAL_MAX_LENGTH = 20
GLOBAL_DIM = GLOBAL_MAX_WIDTH * GLOBAL_MAX_LENGTH

MAX_WIDTH = 5
MAX_LENGTH = 5
MAX_DIM = MAX_WIDTH * MAX_LENGTH

UNKNOWN_SYMBOL = '?'

# Make shift enums
NORTH, EAST, SOUTH, WEST = range(4)

agent_symbols = ['^', '>', 'v', '<']

actions = []
#with open('actions.json', 'r') as infile:
#	actions = json.load(infile)

# class Map:
#     def __init__(self, file_object, length, width):
#         self.length, self.width = length, width
#         self.map = [[UNKNOWN_SYMBOL for j in range(width)] for i in range(length)]
#         self.file = file_object
#         
#     def __str__(self):
#         return '\n'.join([''.join(row) for row in self.map])
        
class State:
    def __init__(self, file_object, start_position=(GLOBAL_MAX_LENGTH, GLOBAL_MAX_WIDTH)):
        self.start_position = start_position
        self.file = file_object
        self.map = {}#[[UNKNOWN_SYMBOL for j in range(2*GLOBAL_MAX_WIDTH)] for i in range(2*GLOBAL_MAX_LENGTH)]
        self.row, self.col = start_position
        self.orientation = NORTH
        self.tools = {
            'a': 0,
            'k': 0,
            'd': 0,
            'g': 0,
        }
        self.lost = self.won = False
        self.update_map()

    def is_over(self):
        return (self.lost or self.won)
    
    def update(self, action):
        self.update_map()
        if self.apply(action):
            self.file.write(action)
        
    def apply(self, action):
        # No action is valid when the game is over
        if self.is_over():
            return False
        # Normalize input
        action = action.lower()
        if action == 'l':
            self.orientation = (self.orientation - 1) % 4
            return True
        elif action == 'r':
            self.orientation = (self.orientation + 1) % 4
            return True
        else:
            new_row, new_col = self.position_ahead()
            cell_ahead = self.get(new_row, new_col)

            if action == 'f':
                if cell_ahead in ['*', 'T', '-']:
                    return False
                self.row, self.col = new_row, new_col

                if cell_ahead in self.tools.keys():
                    self.tools[cell_ahead] += 1

                self.lost = (cell_ahead == '~')
                start_row, start_col = self.start_position
                self.won = (self.tools['g'] and self.row == start_row and self.col == start_col)
                
                return True
            elif action == 'c':
                if cell_ahead == 'T' and self.tools['a']:
                    return True
            elif action == 'o':
                if cell_ahead == '_' and self.tools['k']:
                    return True
            elif action == 'b':
                if cell_ahead in ['*', 'T', '-'] and self.tools['d']:
                    self.tools['d'] -= 1
                    return True
        
    def get(self, i, j, default=None):
        try: 
            return self.map[i][j]
        except IndexError: 
            return default

    def update_map(self):
        r = c = 0
        for i in range(-2, 3):
            for j in range(-2, 3):
                if self.orientation == NORTH:
                    r, c = self.row+i, self.col+j
                elif self.orientation == EAST:
                    r, c = self.row+j, self.col-i
                elif self.orientation == SOUTH:
                    r, c = self.row-i, self.col-j
                elif self.orientation == WEST:
                    r, c = self.row-j, self.col+i

                if (i == 0 and j == 0):
                    ch = agent_symbols[self.orientation]
                else:
                    ch = self.file.read(1)

                if not self.map[r]:
                    self.map[r] = {}
                self.map[r][c] = str(ch)

    def known_cells(self):
        """
        Return number of cells that are known, i.e. have been explored, not UNKNOWN_SYMBOL
        """
        pass
                
    def __str__(self):
        result = []
        result.append('\n'.join([''.join(row) for row in self.map]))
        result.append('Position: {pos}'.format(pos=(self.row, self.col)))
        result.append('Orientation: {orient}'.format(orient=('N', 'E', 'S', 'W')[self.orientation]))
        result.append('Aresenal: {{Axe: {a}, Key: {k}, Gold: {g}, Dynamite: {d}}}'.format(**self.tools))
        return '\n'.join(result)

    def __key(self):
        attr = [self.row, self.col, self.orientation]
        attr.extend(self.tools.items())
        return tuple(attr)
        
    def position(self):
        return (self.row, self.col)

    def orientation(self):
        return self.orientation

    def tools(self):
        return self.tools
        
    def position_ahead(self):
        d_row = d_col = 0     
        if self.orientation == NORTH:   d_row -= 1
        elif self.orientation == EAST:  d_col += 1
        elif self.orientation == SOUTH: d_row += 1
        elif self.orientation == WEST:  d_col -= 1
        return self.row+d_row, self.col+d_col
    
    def action_effective(self, action):
        """
        If performing action will actually bring about change in the state.
        (N. B. By this token, walking into water and subsequently drowning is considered an effective action.)
        """
        # Normalize input
        action = action.lower()
        if action == 'l' or action == 'r':
            return True
        else:
            new_row, new_col = self.ahead()
            cell_ahead = self.map.get(new_row, new_col)
            tools = state.tools()
            if action == 'f':
                if cell_ahead in ['*', 'T', '-']:
                    return False
                return True    
            elif action == 'c':
                if cell_ahead == 'T' and tools['a']:
                    return True
            elif action == 'o':
                if cell_ahead == '-' and tools['k']:
                    return True
            elif action == 'b':
                if cell_ahead in ['*', 'T', '-'] and tools['d']:
                    return True
            return False
         
    def __eq__(self, other):
        return type(self) == type(other) and self.__key() == other__key()
        
    def __hash__(self):
        return hash(self.__key())

def main():
    # Get and process command line arguments. 
    parser = optparse.OptionParser(usage='usage: %prog [options]', version='%prog version 0.1')
    parser.add_option('-p', '--port', action="store", type="int", dest="port", help='server port number to bind to (between 1025 and 65535)')
    options, args = parser.parse_args()

    # Make port a "required option"
    if not options.port:
        parser.print_help()
        return 1
    
    # Create a TCP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(('localhost', options.port))
    except socket.error:
        print 'Could not bind to port: {0}'.format(options.port)
        return 1

    action_string = ''
    f = s.makefile('r', MAX_DIM)
    state = State(f)
    while not state.is_over():                
        print state
        try:
            action_string = actions.pop(0)
        except IndexError:
            action_string = raw_input('Enter Action(s): ')
        if state.apply(action_string):
            s.sendall(action_string)
            state.update_map()

    s.close()
    return 0

if __name__ == '__main__':
    sys.exit(main())
