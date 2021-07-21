"""
An expanded version of the "travel from home to the park" example in
my lectures.
-- Dana Nau <nau@umd.edu>, July 20, 2021
"""

# kludge to make gtpyhop available regardless of whether the current directory
# is the Examples directory or its parent (where gtpyhop.py is located)
#
import sys
sys.path.append('../')
import gtpyhop

import random
import test_harness as th   # code for use in paging and debugging


# Rather than hard-coding the domain name, use the name of the current file.
# This makes the code more portable.
domain_name = __name__
the_domain = gtpyhop.Domain(domain_name)


################################################################################
# states and rigid relations

rigid = gtpyhop.State('rigid relations')
# These types are used by the 'is_a' helper function, later in this file
rigid.types = {
    'person':   ['alice', 'bob'],
    'location': ['home_a', 'home_b', 'park', 'station'],
    'taxi':     ['taxi1', 'taxi2']}
rigid.dist = {
    ('home_a', 'park'):8,    ('home_b', 'park'):2, 
    ('station', 'home_a'):1, ('station', 'home_b'):7,
    ('home_a', 'home_b'):7,  ('station','park'):9}

# prototypical initial state
state0 = gtpyhop.State('state0')
state0.loc = {'alice':'home_a', 'bob':'home_b', 'taxi1':'park',
    'taxi2':'station'}
state0.cash = {'alice':20, 'bob':15}
state0.owe = {'alice':0, 'bob':0}


###############################################################################
# Helper functions:


def taxi_rate(dist):
    "In this domain, the taxi fares are quite low :-)"
    return (1.5 + 0.5 * dist)


def distance(x,y):
    """
    If rigid.dist[(x,y)] = d, this function figures out that d is both
    the distance from x to y and the distance from y to x.
    """
    return rigid.dist.get((x,y)) or rigid.dist.get((y,x))


def is_a(variable,type):
    """
    In most classical planners, one would declare data-types for the parameters
    of each action, and the data-type checks would be done by the planner.
    GTPyhop doesn't have a way to do that, so the 'is_a' function gives us a
    way to do it in the preconditions of each action, command, and method.
    
    'is_a' doesn't implement subtypes (e.g., if rigid.type[x] = y and
    rigid.type[x] = z, it doesn't infer that rigid.type[x] = z. It wouldn't be
    hard to implement this, but it isn't needed in the simple-travel domain.
    """
    return variable in rigid.types[type]


###############################################################################
# Actions:

def walk(state,p,x,y):
    if is_a(p,'person') and is_a(x,'location') and is_a(y,'location') and x != y:
        if state.loc[p] == x:
            state.loc[p] = y
            return state

def call_taxi(state,p,x):
    if is_a(p,'person') and is_a(x,'location'):
        state.loc['taxi1'] = x
        state.loc[p] = 'taxi1'
        return state
    
def ride_taxi(state,p,y):
    # if p is a person, p is in a taxi, and y is a location:
    if is_a(p,'person') and is_a(state.loc[p],'taxi') and is_a(y,'location'):
        taxi = state.loc[p]
        x = state.loc[taxi]
        if is_a(x,'location') and x != y:
            state.loc[taxi] = y
            state.owe[p] = taxi_rate(distance(x,y))
            return state

def pay_driver(state,p,y):
    if is_a(p,'person'):
        if state.cash[p] >= state.owe[p]:
            state.cash[p] = state.cash[p] - state.owe[p]
            state.owe[p] = 0
            state.loc[p] = y
            return state


gtpyhop.declare_actions(walk, call_taxi, ride_taxi, pay_driver)


###############################################################################
# Commands:


# this does the same thing as the action model
def c_walk(state,p,x,y):
    if is_a(p,'person') and is_a(x,'location') and is_a(y,'location'):
        if state.loc[p] == x:
            state.loc[p] = y
            return state


# c_call_taxi, version used in simple_tasks1
# this is like the action model except that the taxi doesn't always arrive
def c_call_taxi(state,p,x):
    if is_a(p,'person') and is_a(x,'location'):
        if random.randrange(2) > 0:
            state.loc['taxi1'] = x
            state.loc[p] = 'taxi1'
            print('Action> c_call_taxi succeeded.  This happens with Pr = 1/2.')
            return state
        else:
            print('Action> c_call_taxi failed.  This happens with Pr = 1/2.')


# c_ride_taxi, version used in simple_tasks1
# this does the same thing as the action model
def c_ride_taxi(state,p,y):
    # if p is a person, p is in a taxi, and y is a location:
    if is_a(p,'person') and is_a(state.loc[p],'taxi') and is_a(y,'location'):
        taxi = state.loc[p]
        x = state.loc[taxi]
        if is_a(x,'location') and x != y:
            state.loc[taxi] = y
            state.owe[p] = taxi_rate(distance(x,y))
            return state


# this does the same thing as the action model
def c_pay_driver(state,p,y):
    return pay_driver(state,p,y)


gtpyhop.declare_commands(c_walk, c_call_taxi, c_ride_taxi, c_pay_driver)

###############################################################################
# Methods:

def do_nothing(state,p,y):
    if is_a(p,'person') and is_a(y,'location'):
        x = state.loc[p]
        if x == y:
            return []

def travel_by_foot(state,p,y):
    if is_a(p,'person') and is_a(y,'location'):
        x = state.loc[p]
        if x != y and distance(x,y) <= 2:
            return [('walk',p,x,y)]

def travel_by_taxi(state,p,y):
    if is_a(p,'person') and is_a(y,'location'):
        x = state.loc[p]
        if x != y and state.cash[p] >= taxi_rate(distance(x,y)):
            return [('call_taxi',p,x), ('ride_taxi',p,y), ('pay_driver',p,y)]

gtpyhop.declare_task_methods('travel',do_nothing,travel_by_foot,travel_by_taxi)


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

    th.pause(do_pauses)
    print("""
Use find_plan to plan how to get Alice from home to the park.
We'll do it several times with different values for 'verbose'.
""")


    expected = [('call_taxi', 'alice', 'home_a'), ('ride_taxi', 'alice', 'park'), ('pay_driver', 'alice', 'park')]

    print("-- If verbose=0, the planner will return the solution but print nothing.")
    gtpyhop.verbose = 0
    result = gtpyhop.find_plan(state1,[('travel','alice','park')])
    th.check_result(result,expected)

    print("-- If verbose=1, the planner will print the problem and solution,")
    print("-- and then return the solution.\n")
    gtpyhop.verbose = 1
    result = gtpyhop.find_plan(state1,[('travel','alice','park')])
    th.check_result(result,expected)

    print("-- If verbose=2, the planner will print the problem, a note at each")
    print("-- recursive call, and the solution. Then it will return the solution.\n")
    gtpyhop.verbose = 2
    result = gtpyhop.find_plan(state1,[('travel','alice','park')])
    th.check_result(result,expected)
    th.pause(do_pauses)

    print("-- If verbose=3, the planner will print even more information.\n")
    gtpyhop.verbose = 3
    result = gtpyhop.find_plan(state1,[('travel','alice','park')])
    th.check_result(result,expected)

    th.pause(do_pauses)
    print("""
Find a plan that will first get Alice to the park, then get Bob to the park.
""")
    gtpyhop.verbose = 2
    plan = gtpyhop.find_plan(state1,[('travel','alice','park'),('travel','bob','park')])

    th.check_result(plan,[('call_taxi', 'alice', 'home_a'), ('ride_taxi', 'alice', 'park'), ('pay_driver', 'alice', 'park'), ('walk', 'bob', 'home_b', 'park')])


    print("""
Next, we'll use run_lazy_lookahead to try to get Alice to the park. With
Pr = 1/2, the taxi won't arrive. In this case, run_lazy_lookahead will call
find_plan again, and find_plan will return the same plan as before. This will
happen repeatedly until either the taxi arrives or run_lazy_lookahead decides
it has tried too many times.""")
    th.pause(do_pauses)

    gtpyhop.verbose = 1
    new_state = gtpyhop.run_lazy_lookahead(state1,[('travel','alice','park')])

    th.pause(do_pauses)

    print('')
    print('If run_lazy_lookahead succeeded, then Alice is now at the park,')
    print('so the planner will return an empty plan:\n')

    plan = gtpyhop.find_plan(new_state,[('travel','alice','park')])
    th.check_result(plan,[])

    print("No more examples")


###############################################################################
# At this point, I used to call main() so the examples would run automatically,
# but I've removed that to maintain uniformity with the other example domains.
