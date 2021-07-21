"""
An expanded version of the "travel from home to the park" example in
my lectures, modified to use goals instead of tasks.
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
# rigid relations, states, goals

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

# initial goal
goal1 = gtpyhop.Multigoal('goal1')
goal1.loc = {'alice':'park'}

# another initial goal
goal2 = gtpyhop.Multigoal('goal2')
goal2.loc = {'bob':'park'}

# bigger initial goal
goal3 = gtpyhop.Multigoal('goal3')
goal3.loc = {'alice':'park', 'bob':'park'}


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


# c_call_taxi
# like the action model, but chooses the taxi randomly
def c_call_taxi(state,p,x):
    if is_a(p,'person') and is_a(x,'location'):
        taxi = 'taxi{}'.format(1+random.randrange(2))
        print(f'Action> the taxi is chosen randomly. This time it is {taxi}.')
        state.loc[taxi] = x
        state.loc[p] = taxi
        return state


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

gtpyhop.declare_unigoal_methods('loc',travel_by_foot,travel_by_taxi)

# GTPyhop provides a built-in multigoal method called m_split_multigoal to
# separate a multigoal G into a collection of unigoals. It returns a list of
# goals [g1, ..., gn, G], where g1, ..., gn are the unigoals in G that aren't
# true in the current state. Since G is at the end of the list, seek_plan
# will first plan for g1, ..., gn and then call m_split_multigoal again, in
# order to re-achieve any goals that (due to deleted-condition interactions)
# became false while accomplishing g1, ..., gn.

# The main problem with m_split_multigoal is that it isn't smart about
# choosing an order in which to achieve g1, ..., gn. Usually some orders
# will work better than others, and a possible project would be to create a
# heuristic function to choose a good order.

gtpyhop.declare_multigoal_methods(gtpyhop.m_split_multigoal)


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

#    state1.display(heading='\nThe initial state is')

    print("""
Next, several planning problems using the above domain and initial state.
""")
    th.pause(do_pauses)
    
    print("""
Below, we give find_plan the goal of having alice be at the park.
We do it several times with different values for 'verbose'.
""")


    expected = [('call_taxi', 'alice', 'home_a'), ('ride_taxi', 'alice', 'park'), ('pay_driver', 'alice', 'park')]

    print("If verbose=0, the planner returns the solution but prints nothing:")
    gtpyhop.verbose = 0
    result = gtpyhop.find_plan(state1,[('loc','alice','park')])
    th.check_result(result,expected)

    print("""If verbose=1, then in addition to returning the solution, the planner prints
both the problem and the solution"
""")
    gtpyhop.verbose = 1
    result = gtpyhop.find_plan(state1,[('loc','alice','park')])
    th.check_result(result,expected)

    print("""If verbose=2, the planner also prints a note at each recursive call.  Below,
_verify_g is a task used by the planner to check whether a method has
achieved its goal.
""")
    gtpyhop.verbose = 2
    result = gtpyhop.find_plan(state1,[('loc','alice','park')])
    th.check_result(result,expected)
    th.pause(do_pauses)

    print("""
If verbose=3, the planner prints even more information. 
""")
    gtpyhop.verbose = 3
    result = gtpyhop.find_plan(state1,[('loc','alice','park')])
    th.check_result(result,expected)

    th.pause(do_pauses)
    print("""
Next, we give find_plan a sequence of two goals: first for Alice to be at the
park, then for Bob to be at the park. Since this is a sequence, it doesn't
matter whether they're both at the park at the same time.
""")

    gtpyhop.verbose = 2
    plan = gtpyhop.find_plan(state1,[('loc','alice','park'),('loc','bob','park')])

    th.check_result(plan,[('call_taxi', 'alice', 'home_a'), ('ride_taxi', 'alice', 'park'), ('pay_driver', 'alice', 'park'), ('walk', 'bob', 'home_b', 'park')])

    th.pause(do_pauses)


    state1.display(heading='\nInitial state')

    print("""
A multigoal g looks similar to a state, but usually it includes just a few of
the state variables rather than all of them. It specifies *desired* values
for those state variables, rather than current values. The goal is to produce
a state that satisfies all of the desired values.

Below, goal3 is the goal of having Alice and Bob at the park at the same time.
""")
    
    goal3.display()
    
    
    print("""
Next, we'll call find_plan on goal3, with verbose=2. In the printout,
_verify_mg is a task used by the planner to check whether a multigoal
method has achieved all of the values specified in the multigoal.
""")
    th.pause(do_pauses)
    
    gtpyhop.verbose = 2
    plan = gtpyhop.find_plan(state1,[goal3])
    th.check_result(plan,[('call_taxi', 'alice', 'home_a'), ('ride_taxi', 'alice', 'park'), ('pay_driver', 'alice', 'park'), ('walk', 'bob', 'home_b', 'park')])

    th.pause(do_pauses)
    print('\nCall run_lazy_lookahead with verbose=1:\n')

    gtpyhop.verbose = 1
    new_state = gtpyhop.run_lazy_lookahead(state1,[('loc','alice','park')])
    print('')
    
    th.pause(do_pauses)
    
    print('\nAlice is now at the park, so the planner will return an empty plan:\n')

    gtpyhop.verbose = 1
    plan = gtpyhop.find_plan(new_state,[('loc','alice','park')])
    th.check_result(plan,[])

    print("No more examples")


###############################################################################
# At this point, I used to call main() so the examples would run automatically,
# but I've removed that to maintain uniformity with the other example domains.
