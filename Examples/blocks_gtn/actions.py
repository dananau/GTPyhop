"""
Action definitions for the blocks_gtn, blocks_htn, blocks_hgn, and
blocks_goal_splitting examples.
-- Dana Nau <nau@umd.edu>, July 14, 2021
"""

import gtpyhop

"""
Each gtpyhop action is a Python function. The 1st argument is the current
state, and the others are the action's usual arguments. This is analogous to
how methods are defined for Python classes (where the first argument is
always the name of the class instance). For example, the function
pickup(s,b) implements the action ('pickup', b).

The blocks-world actions use three state variables:
- pos[b] = block b's position, which may be 'table', 'hand', or another block.
- clear[b] = False if a block is on b or the hand is holding b, else True.
- holding['hand'] = name of the block being held, or False if 'hand' is empty.
"""

def pickup(s,x):
    if s.pos[x] == 'table' and s.clear[x] == True and s.holding['hand'] == False:
        s.pos[x] = 'hand'
        s.clear[x] = False
        s.holding['hand'] = x
        return s

def unstack(s,b1,b2):
    if s.pos[b1] == b2 and b2 != 'table' and s.clear[b1] == True and s.holding['hand'] == False:
        s.pos[b1] = 'hand'
        s.clear[b1] = False
        s.holding['hand'] = b1
        s.clear[b2] = True
        return s
    
def putdown(s,b1):
    if s.pos[b1] == 'hand':
        s.pos[b1] = 'table'
        s.clear[b1] = True
        s.holding['hand'] = False
        return s

def stack(s,b1,b2):
    if s.pos[b1] == 'hand' and s.clear[b2] == True:
        s.pos[b1] = b2
        s.clear[b1] = True
        s.holding['hand'] = False
        s.clear[b2] = False
        return s


# Tell Pyhop what the actions are
#
gtpyhop.declare_actions(pickup, unstack, putdown, stack)
