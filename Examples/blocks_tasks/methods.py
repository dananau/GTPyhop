"""
Method definitions for for blocks_tasks.
Author: Dana Nau <nau@umd.edu>
June 3, 2021
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


"""
In each task_method, the first argument is the current state, and the rest
of the arguments must match the arguments of the corresponding task. For
example, the task ('pickup', b1) has a method m_get(state, b1).
"""

### methods for "move_blocks"

def m_moveb(state,goal):
    """
    This method implements the following block-stacking algorithm:
    If there's a block that can be moved to its final position, then
    do so and call move_blocks recursively. Otherwise, if there's a
    block that needs to be moved and can be moved to the table, then 
    do so and call move_blocks recursively. Otherwise, no blocks need
    to be moved.
    """
    for b1 in all_blocks(state):
        s = status(b1,state,goal)
        if s == 'move-to-table':
            return [('move_one',b1,'table'),('move_blocks',goal)]
        elif s == 'move-to-block':
            return [('move_one',b1,goal.pos[b1]), ('move_blocks',goal)]
        else:
            continue
    #
    # if we get here, no blocks can be moved to their final locations
    for b1 in all_blocks(state):
        if status(b1,state,goal) == 'waiting' and not state.pos[b1] == 'table':
            return [('move_one',b1,'table'), ('move_blocks',goal)]
    #
    # if we get here, there are no blocks that need moving
    return []

"""
declare_task_methods must be called once for each taskname. Below, 'declare_task_methods('get',m_get)' tells gtpyhop that 'get' has one method, m_get. Notice that 'get' is a quoted string, and m_get is the actual function.
"""
gtpyhop.declare_task_methods('move_blocks',m_moveb)


### methods for "move_one"

def m_move1(state,b1,dest):
    """
    Generate subtasks to get b1 and put it at dest.
    """
    return [('get', b1), ('put', b1,dest)]

gtpyhop.declare_task_methods('move_one',m_move1)


### methods for "get"

def m_get(state,b1):
    """
    Generate either a pickup or an unstack subtask for b1.
    """
    if state.clear[b1]:
        if state.pos[b1] == 'table':
                return [('pickup',b1)]
        else:
                return [('unstack',b1,state.pos[b1])]
    else:
        return False

gtpyhop.declare_task_methods('get',m_get)


### methods for "put"

def m_put(state,b1,b2):
    """
    Generate either a putdown or a stack subtask for b1.
    b2 is b1's destination: either the table or another block.
    """
    if state.holding['hand'] == b1:
        if b2 == 'table':
                return [('putdown',b1)]
        else:
                return [('stack',b1,b2)]
    else:
        return False

gtpyhop.declare_task_methods('put',m_put)


