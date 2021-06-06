"""
Some examples that show GTPyhop backtracking over several goals and methods.
Author: Dana Nau <nau@umd.edu>
June 5, 2021
"""

import sys

# kludge to make gtpyhop available from the parent directory
sys.path.append('../')  

import gtpyhop

# This avoids hard-coding the domain name, making the code more portable
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

def main():
    # Code for use in paging and debugging
    from test_harness import check_result, pause, set_trace
    
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
    pause()
    
    print("""Below, seek_plan backtracks once to use a different method for 'put_it'.
""")

    # The comma after each task name is to make Python parse it as a tuple, not an atom
    result = gtpyhop.find_plan(state0,[('put_it',),('need0',)])
    check_result(result,expect0)
    pause()

    print("""The backtracking in this example is the same as in the first one.
""")
    result = gtpyhop.find_plan(state0,[('put_it',),('need01',)])
    check_result(result,expect0)
    pause()

    print("""Below, seek_plan backtracks to use a different method for 'put_it',
and later it backtracks to use a different method for 'need10'.
""")    
    result = gtpyhop.find_plan(state0,[('put_it',),('need10',)])
    check_result(result,expect0)
    pause()

    print("""First, seek_plan backtracks to use a different method for 'put_it'. But the
solution it finds for 'put_it' doesn't satisfy the preconditions of the
method for 'need1', making it backtrack to use a third method for 'put_it'.
""")    
    result = gtpyhop.find_plan(state0,[('put_it',),('need1',)])
    check_result(result,expect1)