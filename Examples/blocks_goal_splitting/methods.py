"""
Method definitions for blocks_goal_splitting.
-- Dana Nau <nau@umd.edu>, July 14, 2021
"""

import gtpyhop


################################################################################
# For multigoals, tell gtpyhop to use its built-in method, m_split_multigoal.


gtpyhop.declare_multigoal_methods(gtpyhop.m_split_multigoal)


################################################################################
# Methods for 'pos' goals. The preconditions have been written to ensure that
# at most one of them will ever be applicable.


def m_move1(state,b1,b2):
    """
    If goal is ('pos',b1,b2) and we're holding nothing, then assert goals to
    get b1 and put it on b2. This method wasn't needed in the blocks_htn,
    blocks_gtn, and blocks_hgn domains.
    """
    if  b2 != 'hand' and not state.holding['hand']:
        if b2 == 'table':
            return [('clear',b1,True), ('pos', b1, 'hand'), ('pos', b1, b2)]
        else:
            return [('clear',b2,True), ('clear',b1,True), \
                    ('pos', b1, 'hand'), ('pos', b1, b2)]

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


################################################################################
# Method for 'clear' goals


def m_make_clear(state,b2,truth):
    """
    if goal is ('clear',b2,True), then remove all of the blocks above b2.
    """
    if truth == True:
        if b2 == 'table' or state.clear[b2]:
            return []
        else:
            # the block above b2
            above_b2 = [b1 for b1 in state.pos if state.pos[b1] == b2][0]
            return [('clear',above_b2,True), ('pos',above_b2,'table')]

gtpyhop.declare_unigoal_methods('clear',m_make_clear)
