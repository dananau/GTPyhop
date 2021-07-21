"""
This file is based on the logistics-domain examples included with HGNpyhop:
    https://github.com/ospur/hgn-pyhop
For a discussion of the adaptations that were needed, see the relevant
section of Some_GTPyhop_Details.md in the top-level directory.
-- Dana Nau <nau@umd.edu>, July 20, 2021
"""


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


################################################################################
# Actions

def drive_truck(state, t, l):
        state.truck_at[t] = l
        return state


def load_truck(state, o, t):
        state.at[o] = t
        return state


def unload_truck(state, o, l):
        t = state.at[o]
        if state.truck_at[t] == l:
            state.at[o] = l
            return state


def fly_plane(state, plane, a):
        state.plane_at[plane] = a
        return state


def load_plane(state, o, plane):
        state.at[o] = plane
        return state


def unload_plane(state, o, a):
        plane = state.at[o]
        if state.plane_at[plane] == a:
            state.at[o] = a
            return state


gtpyhop.declare_actions(drive_truck, load_truck, unload_truck, fly_plane, load_plane, unload_plane)


################################################################################
# Helper functions for the methods


# Find a truck in the same city as the package
def find_truck(state, o):
    for t in state.trucks:
        if state.in_city[state.truck_at[t]] == state.in_city[state.at[o]]:
            return t
    return False


# Find a plane in the same city as the package; if none available, find a random plane
def find_plane(state, o):
    for plane in state.airplanes:
        if state.in_city[state.plane_at[plane]] == state.in_city[state.at[o]]:
            return plane
    return plane


# Find an airport in the same city as the location
def find_airport(state, l):
    for a in state.airports:
        if state.in_city[a] == state.in_city[l]:
            return a
    return False


################################################################################
# Methods to call the actions


def m_drive_truck(state, t, l):
    if t in state.trucks and l in state.locations and state.in_city[state.truck_at[t]] == state.in_city[l]:
        return [('drive_truck', t, l)]


def m_load_truck(state, o, t):
    if o in state.packages and t in state.trucks and state.at[o] == state.truck_at[t]:
        return [('load_truck', o, t)]    


def m_unload_truck(state, o, l):
    if o in state.packages and state.at[o] in state.trucks and l in state.locations:
        return [('unload_truck', o, l)]    


def m_fly_plane(state, plane, a):
    if plane in state.airplanes and a in state.airports:
        return [('fly_plane', plane, a)]


def m_load_plane(state, o, plane):
    if o in state.packages and plane in state.airplanes and state.at[o] == state.plane_at[plane]:
        return [('load_plane', o, plane)]    


def m_unload_plane(state, o, a):
    if o in state.packages and state.at[o] in state.airplanes and a in state.airports:
        return [('unload_plane', o, a)]    


gtpyhop.declare_unigoal_methods('at', m_load_truck, m_unload_truck, m_load_plane, m_unload_plane)
gtpyhop.declare_unigoal_methods('truck_at', m_drive_truck)
gtpyhop.declare_unigoal_methods('plane_at', m_fly_plane)

################################################################################
# Other methods


def move_within_city(state, o, l):
    if o in state.packages and state.at[o] in state.locations and state.in_city[state.at[o]] == state.in_city[l]:
        t = find_truck(state, o)
        if t:
            return [('truck_at', t, state.at[o]), ('at', o, t), ('truck_at', t, l), ('at', o, l)]
    return False


def move_between_airports(state, o, a):
    if o in state.packages and state.at[o] in state.airports and a in state.airports and state.in_city[state.at[o]] != state.in_city[a]:
        plane = find_plane(state, o)
        if plane:
            return [('plane_at', plane, state.at[o]), ('at', o, plane), ('plane_at', plane, a), ('at', o, a)]
    return False


def move_between_city(state, o, l):
    if o in state.packages and state.at[o] in state.locations and state.in_city[state.at[o]] != state.in_city[l]:
        a1 = find_airport(state, state.at[o])
        a2 = find_airport(state, l)
        if a1 and a2:
            return [('at', o, a1), ('at', o, a2), ('at', o, l)]
    return False


gtpyhop.declare_unigoal_methods('at', move_within_city, move_between_airports, move_between_city)


################################################################################
# Examples

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

    state1 = gtpyhop.State('state1')
    state1.packages = {'package1', 'package2'}
    state1.trucks = {'truck1', 'truck6'}
    state1.airplanes = {'plane2'}
    state1.locations = {'location1', 'location2', 'location3', 'airport1', 'location10', 'airport2'}
    state1.airports = {'airport1', 'airport2'}
    state1.cities = {'city1', 'city2'}


    state1.at = {'package1': 'location1',
                 'package2': 'location2'}
    state1.truck_at = {
                 'truck1': 'location3',
                 'truck6': 'location10'
    }
    state1.plane_at = {
                 'plane2': 'airport2'}
    state1.in_city = {'location1': 'city1',
                      'location2': 'city1',
                      'location3': 'city1',
                      'airport1': 'city1',
                      'location10': 'city2',
                      'airport2': 'city2'}

    gtpyhop.verbose = 3

    th.pause(do_pauses)

    print("""
    ----------
    Goal 1: package1 is at location2; package2 is at location3 (transport within the same city)
    ----------
    """)
    gtpyhop.find_plan(state1, [('at', 'package1', 'location2'), ('at', 'package2', 'location3')])

    th.pause(do_pauses)

    print("""
    ----------
    Goal 2: package1 is at location10 (transport to a different city)
    ----------
    """)
    gtpyhop.find_plan(state1, [('at', 'package1', 'location10')])

    th.pause(do_pauses)

    print("""
    ----------
    Goal 3: package1 is at location1 (no actions needed)
    ----------
    """)
    gtpyhop.find_plan(state1, [('at', 'package1', 'location1')])

    print("No more examples")
