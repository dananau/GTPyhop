"""
blocks_gtn, blocks_htn, and blocks_hgn all are implementations of the
near-optimal blocks-world planning algorithm described in the following
paper:

    N. Gupta and D. S. Nau. On the complexity of blocks-world 
    planning. Artificial Intelligence 56(2-3):223–254, 1992.

The three implementations differ as follows: blocks_gtn uses both tasks
and goals, blocks_htn only uses tasks, and blocks_hgn only uses goals.

-- Dana Nau <nau@umd.edu>, July 14, 2021
"""

# kludge to make gtpyhop available regardless of whether the current directory
# is the Examples directory or its parent (where gtpyhop.py is located)
#
import sys
sys.path.append('../')
import gtpyhop

from .examples import *
