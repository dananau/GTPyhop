"""
Examples file for blocks_goal_splitting.
-- Dana Nau <nau@umd.edu>, July 20, 2021
"""

# Uncomment this to use it in debugging:
# from IPython import embed
# from IPython.terminal.debugger import set_trace

import gtpyhop
import test_harness as th   # code for use in paging and debugging


# We must declare the current domain before importing methods and actions.
# To make the code more portable, we don't hard-code the domain name, but
# instead use the name of the package.
the_domain = gtpyhop.Domain(__package__)

from .methods import *
from .actions import *

print('-----------------------------------------------------------------------')
print(f"Created '{gtpyhop.current_domain}'. To run the examples, type this:")
print(f'{the_domain.__name__}.main()')


#############     beginning of tests     ################

def main(do_pauses=True):
    """
    Run various examples.
    main() will pause occasionally to let you examine the output.
    main(False) will run straight through to the end, without stopping.
    """

    # If we've changed to some other domain, this will change us back.
    print(f"Changing current domain to {the_domain}, if it isn't that already.")
    gtpyhop.current_domain = the_domain

    gtpyhop.print_domain()

    state1 = gtpyhop.State('state1')
    state1.pos={'a':'b', 'b':'table', 'c':'table'}
    state1.clear={'c':True, 'b':False,'a':True}
    state1.holding={'hand':False}

    state1.display('\nInitial state is')

    print("""
Below, both goal1a and goal1b specify that we want c on b, and b on a. 
However, goal1a also specifies that we want a on the table.
""")

    goal1a = gtpyhop.Multigoal('goal1a')
    goal1a.pos={'c':'b', 'b':'a', 'a':'table'}

    goal1a.display()

    goal1b = gtpyhop.Multigoal('goal1b')
    goal1b.pos={'c':'b', 'b':'a'}

    goal1b.display()

    ### goal1b omits some of the conditions of goal1a,
    ### but those conditions will need to be achieved anyway

    th.pause(do_pauses)

    print("""
Run GTPyhop with goal1a and goal1b, starting in state1. Both should produce the
same plan, but it won't be a very good plan, because m_split_multigoal doesn't know
how to choose the best order for achieving the goals.
""")

    state1.display("Initial state is")

    # Tell the test harness what answer to expect, so it can signal an error
    # if gtpyhop returns an incorrect answer. Checks like this have been very
    # very helpful for debugging both gtpyhop and the various example domains.

    expected = [('unstack', 'a', 'b'), ('putdown', 'a'), ('pickup', 'c'), ('stack', 'c', 'b'), ('unstack', 'c', 'b'), ('putdown', 'c'), ('pickup', 'b'), ('stack', 'b', 'a'), ('pickup', 'c'), ('stack', 'c', 'b')]

    plan1 = gtpyhop.find_plan(state1,[goal1a])
    th.check_result(plan1,expected)

    plan2 = gtpyhop.find_plan(state1,[goal1b])
    th.check_result(plan2,expected)
    th.pause(do_pauses)


    print("""
Run GTPyhop on two more planning problems. Like before, goal2a omits some
of the conditions in goal2a, but both goals should produce the same plan.
""")

    state2 = gtpyhop.State('state2')
    state2.pos={'a':'c', 'b':'d', 'c':'table', 'd':'table'}
    state2.clear={'a':True, 'c':False,'b':True, 'd':False}
    state2.holding={'hand':False}

    state2.display('The initial state is')
    
    goal2a = gtpyhop.Multigoal('goal2a')
    goal2a.pos={'b':'c', 'a':'d', 'c':'table', 'd':'table'}
    goal2a.clear={'a':True, 'c':False,'b':True, 'd':False}
    goal2a.holding={'hand':False}

    goal2a.display()
    
    goal2b = gtpyhop.Multigoal('goal2b')
    goal2b.pos={'b':'c', 'a':'d'}

    goal2b.display()
    
    ### goal2b omits some of the conditions of goal2a,
    ### but those conditions will need to be achieved anyway.

    expected = [('unstack', 'a', 'c'), ('putdown', 'a'), ('unstack', 'b', 'd'), ('stack', 'b', 'c'), ('pickup', 'a'), ('stack', 'a', 'd')] 

    plan1 = gtpyhop.find_plan(state2,[goal2a])
    th.check_result(plan1,expected)

    plan2 = gtpyhop.find_plan(state2,[goal2b])
    th.check_result(plan2,expected)
    th.pause(do_pauses)


    # In some Python installations, the default recursion limit is too small to
    # run gtpyhop on the next planning problem. If so, we increase it.

    import sys
    reclimit = sys.getrecursionlimit()
    if reclimit < 1200:
        print(f"Increase Python's recursion limit from {reclimit} to 1200""", end='')
        sys.setrecursionlimit(1200)
        print(" ... done.")

    print("""
Define problem bw_large_d from the SHOP distribution. 
""")

    state3 = gtpyhop.State('state3')
    state3.pos = {1:12, 12:13, 13:'table', 11:10, 10:5, 5:4, 4:14, 14:15, 15:'table', 9:8, 8:7, 7:6, 6:'table', 19:18, 18:17, 17:16, 16:3, 3:2, 2:'table'}
    state3.clear = {x:False for x in range(1,20)}
    state3.clear.update({1:True, 11:True, 9:True, 19:True})
    state3.holding={'hand':False}

    state3.display('The initial state is')
    
    goal3 = gtpyhop.Multigoal('goal3')
    goal3.pos = {15:13, 13:8, 8:9, 9:4, 4:'table', 12:2, 2:3, 3:16, 16:11, 11:7, 7:6, 6:'table'}
    goal3.clear = {17:True, 15:True, 12:True}

    goal3.display()
    
    expected = [('unstack', 1, 12), ('putdown', 1), ('unstack', 12, 13), ('putdown', 12), ('unstack', 11, 10), ('putdown', 11), ('unstack', 10, 5), ('putdown', 10), ('unstack', 5, 4), ('putdown', 5), ('unstack', 4, 14), ('putdown', 4), ('unstack', 14, 15), ('putdown', 14), ('pickup', 15), ('stack', 15, 13), ('unstack', 9, 8), ('putdown', 9), ('unstack', 15, 13), ('putdown', 15), ('pickup', 13), ('stack', 13, 8), ('unstack', 13, 8), ('putdown', 13), ('unstack', 8, 7), ('stack', 8, 9), ('unstack', 8, 9), ('putdown', 8), ('pickup', 9), ('stack', 9, 4), ('unstack', 19, 18), ('putdown', 19), ('unstack', 18, 17), ('putdown', 18), ('unstack', 17, 16), ('putdown', 17), ('unstack', 16, 3), ('putdown', 16), ('unstack', 3, 2), ('putdown', 3), ('pickup', 12), ('stack', 12, 2), ('unstack', 12, 2), ('putdown', 12), ('pickup', 2), ('stack', 2, 3), ('unstack', 2, 3), ('putdown', 2), ('pickup', 3), ('stack', 3, 16), ('unstack', 3, 16), ('putdown', 3), ('pickup', 16), ('stack', 16, 11), ('unstack', 16, 11), ('putdown', 16), ('pickup', 11), ('stack', 11, 7), ('pickup', 15), ('stack', 15, 13), ('unstack', 15, 13), ('putdown', 15), ('pickup', 13), ('stack', 13, 8), ('unstack', 13, 8), ('putdown', 13), ('pickup', 8), ('stack', 8, 9), ('pickup', 12), ('stack', 12, 2), ('unstack', 12, 2), ('putdown', 12), ('pickup', 2), ('stack', 2, 3), ('unstack', 2, 3), ('putdown', 2), ('pickup', 3), ('stack', 3, 16), ('unstack', 3, 16), ('putdown', 3), ('pickup', 16), ('stack', 16, 11), ('pickup', 15), ('stack', 15, 13), ('unstack', 15, 13), ('putdown', 15), ('pickup', 13), ('stack', 13, 8), ('pickup', 12), ('stack', 12, 2), ('unstack', 12, 2), ('putdown', 12), ('pickup', 2), ('stack', 2, 3), ('unstack', 2, 3), ('putdown', 2), ('pickup', 3), ('stack', 3, 16), ('pickup', 15), ('stack', 15, 13), ('pickup', 12), ('stack', 12, 2), ('unstack', 12, 2), ('putdown', 12), ('pickup', 2), ('stack', 2, 3), ('pickup', 12), ('stack', 12, 2)]
    th.pause(do_pauses)


    print("""
Run gtpyhop on bw_large_d. It will find a long plan, because m_split_multigoal
doesn't know how to choose the best order for achieving the goals.
""")

    plan = gtpyhop.find_plan(state3,[goal3])
    th.check_result(plan,expected)
    th.pause(do_pauses)


    print("""
Call run_lazy_lookahead on the same problem:
""")

    new_state = gtpyhop.run_lazy_lookahead(state3, [goal3])

    print("The goal should now be satisfied, so the planner should return an empty plan:\n")

    plan = gtpyhop.find_plan(new_state, [goal3])
    th.check_result(plan,[])

    print("No more examples")


# It's tempting to make the following call to main() unconditional, to run the
# examples without making the user type an extra command. But if we do this
# and an error occurs while main() is executing, we get a situation in which
# the actions, methods, and examples files have been imported but the module
# hasn't been - which causes problems if we try to import the module again.

if __name__=="__main__":
    main()
