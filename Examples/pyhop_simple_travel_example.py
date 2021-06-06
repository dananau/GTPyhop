"""
The simple_travel_example.py file from the Pyhop distribution, with minor
changes to make it compatible with GTPyhop.
Author: Dana Nau <nau@umd.edu>
June 5, 2021

Unlike the other example files, this one doesn't use the test harness,
because I wanted to keep things as close as possible to the Pyhop version of
the file.

To make the code work with GTPyhop, the necessary changes were:
- use gtpyhop module instead of pyhop
- replace keyword argument 'verbose' with global variable 'gtpyhop.verbose'
"""

# kludge to make GTPyhop available from the parent directory
import sys
sys.path.append('../')  
import gtpyhop


def taxi_rate(dist):
    return (1.5 + 0.5 * dist)

def walk(state,a,x,y):
    if state.loc[a] == x:
        state.loc[a] = y
        return state
    else: return False

def call_taxi(state,a,x):
    state.loc['taxi'] = x
    return state
    
def ride_taxi(state,a,x,y):
    if state.loc['taxi']==x and state.loc[a]==x:
        state.loc['taxi'] = y
        state.loc[a] = y
        state.owe[a] = taxi_rate(state.dist[x][y])
        return state
    else: return False

def pay_driver(state,a):
    if state.cash[a] >= state.owe[a]:
        state.cash[a] = state.cash[a] - state.owe[a]
        state.owe[a] = 0
        return state
    else: return False

gtpyhop.declare_operators(walk, call_taxi, ride_taxi, pay_driver)
print('')
gtpyhop.print_operators()



def travel_by_foot(state,a,x,y):
    if state.dist[x][y] <= 2:
        return [('walk',a,x,y)]
    return False

def travel_by_taxi(state,a,x,y):
    if state.cash[a] >= taxi_rate(state.dist[x][y]):
        return [('call_taxi',a,x), ('ride_taxi',a,x,y), ('pay_driver',a)]
    return False

gtpyhop.declare_methods('travel',travel_by_foot,travel_by_taxi)
print('')
gtpyhop.print_methods()

state1 = gtpyhop.State('state1')
state1.loc = {'me':'home'}
state1.cash = {'me':20}
state1.owe = {'me':0}
state1.dist = {'home':{'park':8}, 'park':{'home':8}}

print("""
********************************************************************************
Call gtpyhop.pyhop(state1,[('travel','me','home','park')]) with different verbosity levels
********************************************************************************
""")

print("- If verbose=0, GTPyhop returns the solution but prints nothing.\n")
gtpyhop.verbose = 0
gtpyhop.pyhop(state1,[('travel','me','home','park')])

print('- If verbose=1, GTPyhop prints the problem and solution, and returns the solution:')
gtpyhop.verbose = 1
gtpyhop.pyhop(state1,[('travel','me','home','park')])

print('- If verbose=2, GTPyhop also prints a note at each recursive call:')
gtpyhop.verbose = 2
gtpyhop.pyhop(state1,[('travel','me','home','park')])

print('- If verbose=3, GTPyhop also prints the intermediate states:')
gtpyhop.verbose = 3
gtpyhop.pyhop(state1,[('travel','me','home','park')])

