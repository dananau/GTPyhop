"""
The blocks_goal_splitting domain illustrates how to achieve blocks-world
multigoals using GTPyhop's built-in m_split_multigoal method, which splits a
multigoal into a list of unigoals and tries to achieve them sequentially.
Due to deleted-condition interactions (in which achieving a later unigoal
undoes a previously-achieved unigoal), this usually won't produce a state in
which the entire multigoal has been achieved. If repeated sufficiently many
times, it will eventually produce such a state, but it may take several
tries, thus producing solution plans that are much longer than optimal.

This would work much better if GTPyhop had an intelligent way to choose an
order in which to achieve the unigoals. To accomplish that, we would need
either to write a domain-specific multigoal method and use it instead of
m_split_multigoals (as in the blocks_gtn, blocks_htn, and blocks_hgn
domains), or to modify m_split_multigoals to use a heuristic function to
reorder its list of unigoals.

-- Dana Nau <nau@umd.edu>, July 14, 2021
"""

# kludge to make gtpyhop available regardless of whether the current directory
# is the Examples directory or its parent (where gtpyhop.py is located)
#
import sys
sys.path.append('../')
import gtpyhop

from .examples import *
