"""
Method definitions for blocks_goals.
-- Dana Nau <nau@umd.edu>, June 6, 2021
"""

import gtpyhop

"""
Here are some helper functions that are used in the methods' preconditions.
"""

def is_done(b1,state,goal):
    if b1 == 'table': return True
    if b1 in goal.pos and goal.pos[b1] != state.pos[b1]:
        return False
    if state.pos[b1] == 'table': return True
    return is_done(state.pos[b1],state,goal)

def status(b1,state,goal):
    """
    The status of a block b1 is defined as follows:
    - If b1 and the blocks below it will never need to be moved, it is 'done'.
    - Otherwise, if b1 isn't clear, then its status is 'inaccessible'
    - Otherwise, we examine why b1 needs to be moved:
      - If b1 has no goal position, then there must be a block below b1 that needs
          to be moved, so b1's status is 'move-to-table' to get it out of the way.
      - If b1's goal position is the table, then its status is 'move-to-table'.
      - If b1's goal position is a clear block that's done, then its status
          is 'move-to-block'.
      - Otherwise, we can't move b1 to its goal position until some other
          blocks are moved, so its status is 'waiting'.
    """
    if is_done(b1,state,goal):
        return 'done'
    elif not state.clear[b1]:
        return 'inaccessible'
    elif not (b1 in goal.pos) or goal.pos[b1] == 'table':
        return 'move-to-table'
    elif is_done(goal.pos[b1],state,goal) and state.clear[goal.pos[b1]]:
        return 'move-to-block'
    else:
        return 'waiting'

def all_blocks(state):
    return state.clear.keys()

def all_clear_blocks(state):
    return [x for x in state.clear if state.clear[x] == True]


### methods for "move_blocks"

def m_moveb(state,multigoal):
    """
    This method implements the following block-stacking algorithm: 
    - If there's a clear block b that can be moved to a position where it will
      never need to be moved again, then do so, and invoke the multigoal again.
    - Otherwise, if there's a clear block b that needs to be moved out of the
      way in order to make another block accessible, then move b to the table,
      and invoke the multigoal again.
    - Otherwise, no blocks need to be moved.
    """
    for b1 in all_clear_blocks(state):
        s = status(b1,state,multigoal)
        if s == 'move-to-block':
            b2 = multigoal.pos[b1]
            return [('pos',b1,b2),multigoal]
        elif s == 'move-to-table':
            return [('pos',b1,'table'),multigoal]
        else:
            continue
    #
    # if we get here, no blocks can be moved to their final locations
    for b1 in all_clear_blocks(state):
        if status(b1,state,multigoal) == 'waiting' and not state.pos[b1] == 'table':
            return [('pos',b1,'table'),multigoal]
    #
    # if we get here, there are no blocks that need moving
    return []

"""
Below, we tell gtpyhop that a Multigoal has only one method, m_moveb.
"""
gtpyhop.declare_multigoal_methods(m_moveb)

### methods for 'pos' goals

def m_move1(state,b1,b2):
    """
    If goal is ('pos',b1,b2), b1 is clear, we're holding nothing, and b2 is
    either the table or clear, then assert goals to get b1 and put it on b2.
    """
    if  b2 != 'hand' and state.clear[b1] and state.holding['hand'] == False:
        if b2 == 'table' or state.clear[b2]:
            return [('pos', b1, 'hand'), ('pos', b1, b2)]

def m_get(state,b1,b2):
    """
    If goal is ('pos',b1,'hand') and b1 is clear and we're holding nothing
    then generate either a pickup or an unstack subtask for b1.
    """
    if b2 == 'hand' and state.clear[b1] and state.holding['hand'] == False:
        if state.pos[b1] == 'table':
                return [('pickup',b1)]
        else:
                return [('unstack',b1,state.pos[b1])]
    else:
        return False

def m_put(state,b1,b2):
    """
    If goal is ('pos',b1,b2) and we're holding b1,
    Generate either a putdown or a stack subtask for b1.
    b2 is b1's destination: either the table or another block.
    """
    if b2 != 'hand' and state.pos[b1] == 'hand':
        if b2 == 'table':
                return [('putdown',b1)]
        elif state.clear[b2]:
                return [('stack',b1,b2)]
    else:
        return False

gtpyhop.declare_unigoal_methods('pos',m_move1,m_get,m_put)
