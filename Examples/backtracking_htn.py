"""
Some examples that show GTPyhop backtracking through several methods and tasks.
-- Dana Nau <nau@umd.edu>, July 20, 2021
"""

import sys

# kludge to make gtpyhop available regardless of whether the current directory
# is the Examples directory or its parent (where gtpyhop.py is located)
#
import sys
sys.path.append('../')
import gtpyhop

import test_harness as th   # code for use in paging and debugging

# Rather than hard-coding the domain name, use the name of the current file.
# This makes the code more portable.
domain_name = __name__
the_domain = gtpyhop.Domain(domain_name)

###############################################################################
# States:

state0 = gtpyhop.State('state0')
state0.flag = -1


###############################################################################
# Methods:


def m_err(state):
    return [('putv', 0), ('getv', 1)]

def m0(state):
    return [('putv', 0), ('getv', 0)]

def m1(state):
    return [('putv', 1), ('getv', 1)]

gtpyhop.declare_task_methods('put_it',m_err,m0,m1)


def m_need0(state):
    return [('getv', 0)]

def m_need1(state):
    return [('getv', 1)]

gtpyhop.declare_task_methods('need0',m_need0)

gtpyhop.declare_task_methods('need1',m_need1)

gtpyhop.declare_task_methods('need01',m_need0,m_need1)

gtpyhop.declare_task_methods('need10',m_need1,m_need0)

###############################################################################
# Actions:

def putv(state,flag_val):
    state.flag = flag_val
    return state

def getv(state,flag_val):
    if state.flag == flag_val:
        return state

gtpyhop.declare_actions(putv,getv)

###############################################################################
# Problem:


###############################################################################
# Running the examples

print('-----------------------------------------------------------------------')
print(f"Created the domain '{domain_name}'. To run the examples, type this:")
print(f"{domain_name}.main()")

def main(do_pauses=True):
    """
    Run various examples.
    main() will pause occasionally to let you examine the output.
    main(False) will run straight through to the end, without stopping.
    """

    # If we've changed to some other domain, this will change us back.
    gtpyhop.current_domain = the_domain
    gtpyhop.print_domain()

    state1 = state0.copy()

    state1.display(heading='\nInitial state is')

    # two possible expected answers for check_result
    expect0 = [('putv', 0), ('getv', 0), ('getv', 0)]
    expect1 = [('putv', 1), ('getv', 1), ('getv', 1)]

    print("Next are some example problems with verbose=3 in order to see the backtracking.\n")
    gtpyhop.verbose = 3
    th.pause(do_pauses)
    
    print("""Below, seek_plan backtracks once to use a different method for 'put_it'.
""")

    # The comma after each task name is to make Python parse it as a tuple, not an atom
    result = gtpyhop.find_plan(state0,[('put_it',),('need0',)])
    th.check_result(result,expect0)
    th.pause(do_pauses)

    print("""The backtracking in this example is the same as in the first one.
""")
    result = gtpyhop.find_plan(state0,[('put_it',),('need01',)])
    th.check_result(result,expect0)
    th.pause(do_pauses)

    print("""Below, seek_plan backtracks to use a different method for 'put_it',
and later it backtracks to use a different method for 'need10'.
""")    
    result = gtpyhop.find_plan(state0,[('put_it',),('need10',)])
    th.check_result(result,expect0)
    th.pause(do_pauses)

    print("""First, seek_plan backtracks to use a different method for 'put_it'. But the
solution it finds for 'put_it' doesn't satisfy the preconditions of the
method for 'need1', making it backtrack to use a third method for 'put_it'.
""")    
    result = gtpyhop.find_plan(state0,[('put_it',),('need1',)])
    th.check_result(result,expect1)