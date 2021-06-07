"""
Action definitions file for the blocks_tasks, blocks_goals, and
blocks_goal_splitting examples.
-- Dana Nau <nau@umd.edu>, June 6, 2021
"""

import gtpyhop

"""
Each gtpyhop action is a Python function. The 1st argument is the current
state, and the others are the action's usual arguments. This is analogous to
how methods are defined for Python classes (where the first argument is
always the name of the class instance). For example, the function
pickup(state,b) implements the action for the task ('pickup', b).

The blocks-world actions use three state variables:
- pos[b] = block b's position, which may be 'table', 'hand', or another block.
- clear[b] = False if a block is on b or the hand is holding b, else True.
- holding['hand'] = name of the block being held, or False if the hand is empty.
"""

def pickup(state,b1):
    if state.pos[b1] == 'table' and state.clear[b1] == True and state.holding['hand'] == False:
        state.pos[b1] = 'hand'
        state.clear[b1] = False
        state.holding['hand'] = b1
        return state

def unstack(state,b1,b2):
    if state.pos[b1] == b2 and b2 != 'table' and state.clear[b1] == True and state.holding['hand'] == False:
        state.pos[b1] = 'hand'
        state.clear[b1] = False
        state.holding['hand'] = b1
        state.clear[b2] = True
        return state
    
def putdown(state,b1):
    if state.pos[b1] == 'hand':
        state.pos[b1] = 'table'
        state.clear[b1] = True
        state.holding['hand'] = False
        return state

def stack(state,b1,b2):
    if state.pos[b1] == 'hand' and state.clear[b2] == True:
        state.pos[b1] = b2
        state.clear[b1] = True
        state.holding['hand'] = False
        state.clear[b2] = False
        return state


# Tell Pyhop what the actions are
#
gtpyhop.declare_actions(pickup, unstack, putdown, stack)
