"""
The following code runs GTPyhop on all but one of the example domains, to
see whether they run without error and return correct answers. The
2nd-to-last line imports simple_htn_acting_error but doesn't run it,
because running it is *supposed* to cause an error.

-- Dana Nau <nau@umd.edu>, July 20, 2021
"""

# The argument False tells the test harness not to stop for user input
import simple_htn; simple_htn.main(False)
import simple_hgn; simple_hgn.main(False)
import backtracking_htn; backtracking_htn.main(False)
import logistics_hgn; logistics_hgn.main(False)
import blocks_gtn; blocks_gtn.main(False)
import blocks_goal_splitting; blocks_goal_splitting.main(False)
import blocks_hgn; blocks_hgn.main(False)
import blocks_htn; blocks_htn.main(False)
import pyhop_simple_travel_example
import simple_htn_acting_error
print('\nFinished without error.')
