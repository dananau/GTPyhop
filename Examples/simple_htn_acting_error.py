"""
An expanded version of the "travel from home to the park" example in my
lectures, modified to show how an unexpected problem at acting time can
cause an execution error if the methods are too brittle.

For a way to overcome this problem, see 

    Bansod, Nau, Patra and Roberts. Integrating Planning and Acting by Using
    a Re-Entrant HTN Planner. ICAPS HPlan Workshop, 2021.

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

# First initial state. In this one, both taxis are in good condition
state0a = gtpyhop.State('state0a')
state0a.loc = {'alice':'home_a', 'bob':'home_b', 'taxi1':'park',
    'taxi2':'station'}
state0a.cash = {'alice':20, 'bob':15}
state0a.owe = {'alice':0, 'bob':0}
state0a.taxi_condition = {'taxi1':'good', 'taxi2':'good'}


# Second initial state. In this one, both taxis are in bad condition
state0b = gtpyhop.State('state0b')
state0b.loc = {'alice':'home_a', 'bob':'home_b', 'taxi1':'park',
    'taxi2':'station'}
state0b.cash = {'alice':20, 'bob':15}
state0b.owe = {'alice':0, 'bob':0}
state0b.taxi_condition = {'taxi1':'bad', 'taxi2':'bad'}



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


# c_call_taxi, version used in simple_tasks2
# like the action model, but chooses the taxi randomly
def c_call_taxi(state,p,x):
    if is_a(p,'person') and is_a(x,'location'):
        taxi = 'taxi{}'.format(1+random.randrange(2))
        print(f'Action> The taxi is chosen randomly.')
        print(f'Action> This time it is {taxi}.')
        state.loc[taxi] = x
        state.loc[p] = taxi
        return state


# c_ride_taxi, version used in simple_tasks2.
# If the taxi isn't in good condition, it will break down.
def c_ride_taxi(state,p,y):
    # if p is a person, p is in a taxi, and y is a location:
    if is_a(p,'person') and is_a(state.loc[p],'taxi') and is_a(y,'location'):
        taxi = state.loc[p]
        x = state.loc[taxi]
        if is_a(x,'location') and x != y:
            if state.taxi_condition[taxi] == 'good':
                state.loc[taxi] = y
                state.owe[p] = taxi_rate(distance(x,y))
                return state
            else:
                print('Action> c_ride_taxi failed.')


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

    state0a.display(heading='\nInitial state')

    th.pause(do_pauses)
    print("Use run_lazy_lookahead to get Alice to the park.\n")
    gtpyhop.run_lazy_lookahead(state0a,[('travel','alice','park')])
    print('')
    th.pause(do_pauses)

    print("""
# Next is a demonstration of what can happen if the HTN methods are too
# brittle and a problem occurs at acting time. We'll try to use
# run_lazy_lookahead to get Alice to the park, but the taxi will break
# down while Alice is in it.  run_lazy_lookahead will call find_plan
# again, but an execution error will occur during planning because the
# HTN methods don't handle this case.
    """)


    state0b.display(heading='The initial state is')

    print('Next, the call to run_lazy_lookahead ...')
    th.pause(do_pauses)

    gtpyhop.run_lazy_lookahead(state0b,[('travel','alice','park')])
    th.pause(do_pauses)

    print("No more examples")


###############################################################################
# At this point, I used to call main() so the examples would run automatically,
# but I've removed that to maintain uniformity with the other example domains.
