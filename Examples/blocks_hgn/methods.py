"""
Method definitions for blocks_hgn.
-- Dana Nau <nau@umd.edu>, July 14, 2021
"""

import gtpyhop

################################################################################
# Helper functions that are used in the methods' preconditions.


def is_done(b1,state,mgoal):
    if b1 == 'table': return True
    if b1 in mgoal.pos and mgoal.pos[b1] != state.pos[b1]:
        return False
    if state.pos[b1] == 'table': return True
    return is_done(state.pos[b1],state,mgoal)


def status(b1,state,mgoal):
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
    if is_done(b1,state,mgoal):
        return 'done'
    elif not state.clear[b1]:
        return 'inaccessible'
    elif not (b1 in mgoal.pos) or mgoal.pos[b1] == 'table':
        return 'move-to-table'
    elif is_done(mgoal.pos[b1],state,mgoal) and state.clear[mgoal.pos[b1]]:
        return 'move-to-block'
    else:
        return 'waiting'


def all_blocks(state):
    return state.clear.keys()


def all_clear_blocks(state):
    return [x for x in state.clear if state.clear[x] == True]


################################################################################
### method for blocks-world multigoals


def m_moveblocks(s,mgoal):
    """
    This method implements the following block-stacking algorithm [1]: 
    - If there's a clear block x that can be moved to a place where it won't
      need to be moved again, then return a todo list that includes goals to
      move it there, followed by mgoal (to achieve the remaining goals).
    - Otherwise, if there's a clear block x that needs to be moved out of the
      way to make another block movable, then return a todo list that includes
      goals to move x to the table, followed by mgoal.
    - Otherwise, no blocks need to be moved.
    [1] N. Gupta and D. S. Nau. On the complexity of blocks-world 
        planning. Artificial Intelligence 56(2-3):223–254, 1992.
    """

    # look for a clear block that can be moved to its final location
    for x in all_clear_blocks(s):
        xstat = status(x,s,mgoal)
        if xstat == 'move-to-block':
            return [('pos',x,'hand'), ('pos',x,mgoal.pos[x]), mgoal]
        elif xstat == 'move-to-table':
            return [('pos',x,'hand'), ('pos',x,'table'), mgoal]
        else:
            continue

    # if we get here, no blocks can be moved to their final locations
    for x in all_clear_blocks(s):
        if status(x,s,mgoal) == 'waiting' and not s.pos[x] == 'table':
            return [('pos',x,'hand'), ('pos',x,'table'), mgoal]

    # if we get here, there are no blocks that need moving
    return []


gtpyhop.declare_multigoal_methods(m_moveblocks)


################################################################################
# methods for 'pos' goals.
#
# In the blocks_htn and blocks_gtn domains, the m_take and m_put methods
# have simpler preconditions, because the task names 'take' and 'put' tell when
# to use each method.  Here, each method needs some additional preconditions to
# tell what kind of 'pos' task it's for.


def m_take(state,x,h):
    """
    If goal is ('pos',x,'hand') and x is clear and the hand is empty, then
    return a todo list containing either a pickup or an unstack task.
    """
    if h == 'hand' and state.clear[x] and state.holding['hand'] == False:
        if state.pos[x] == 'table':
                return [('pickup',x)]
        else:
                return [('unstack',x,state.pos[x])]
    else:
        return False


def m_put(state,x,y):
    """
    If goal is ('pos',x,y) (where x is a block and y is its destination) and
    we're holding x, return a todo list containing a putdown or a stack task.
    """
    if y != 'hand' and state.pos[x] == 'hand':
        if y == 'table':
                return [('putdown',x)]
        elif state.clear[y]:
                return [('stack',x,y)]
    else:
        return False

gtpyhop.declare_unigoal_methods('pos', m_take, m_put)
