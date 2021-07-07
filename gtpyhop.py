# SPDX-FileCopyrightText: 2021 University of Maryland
# SPDX-License-Identifier: BSD-3-Clause-Clear

# GTPyhop, version 1.1
# Author: Dana Nau <nau@umd.edu>, July 7, 2021

"""
GTPyhop is an automated planning system that can plan for both tasks and
goals. It requires Python 3. 

Accompanying this file are a README.md file giving an overview of GTPyhop,
and several examples of how to use GTPyhop. To run them, try importing any
of the modules in the Examples directory.
"""

# For use in debugging:
# from IPython import embed
# from IPython.terminal.debugger import set_trace

import copy, sys, pprint, re

################################################################################
# How much information to print while the program is running

verbose = 1
"""
verbose is a global value whose initial value is 1. Its value determines how
much debugging information GTPyhop will print:
 - verbose = 0: print nothing
 - verbose = 1: print the initial parameters and the answer
 - verbose = 2: also print a message on each recursive call
 - verbose = 3: also print some info about intermediate computations
"""

################################################################################
# States and goals

# Sequence number to use when making copies of states.
_next_state_number = 0

class State():
    """
    s = State(state_name, **kwargs) creates an object that contains the
    state-variable bindings for a state-of-the-world.
      - state_name is the name to use for the new state.
      - The keyword args are the names and initial values of state variables.
        A state-variable's initial value is usually {}, but it can also
        be a dictionary of arguments and their initial values.
    
    Example: here are three equivalent ways to specify a state named 'foo'
    in which boxes b and c are located in room2 and room3:
        First:
           s = State('foo')
           s.loc = {}   # create a dictionary for things like loc['b']
           s.loc['b'] = 'room2'
           s.loc['c'] = 'room3'
        Second:
           s = State('foo',loc={})
           s.loc['b'] = 'room2'
           s.loc['c'] = 'room3'
        Third:
           s = State('foo',loc={'b':'room2', 'c':'room3'})
    """
    
    def __init__(self, state_name, **kwargs):
        """
        state_name is the name to use for the state. The keyword
        args are the names and initial values of state variables.
        """
        self.__name__ = state_name
        vars(self).update(kwargs)
            
    def __str__(self):
        return f"<State {self.__name__}>"
        
    def __repr__(self):
        return _make_repr(self, 'State')

    def copy(self,new_name=None):
        """
        Make a copy of the state. For its name, use new_name if it is given.
        Otherwise use the old name, with a suffix '_copy#' where # is an integer.
        """
        global _next_state_number
        the_copy = copy.deepcopy(self)
        if new_name:
            the_copy.__name__ = new_name
        else:
            the_copy.__name__ = _name_for_copy(the_copy.__name__, _next_state_number)
            _next_state_number += 1
        return the_copy

    def display(self, heading=None):
        """
        Print the state's state-variables and their values.
         - heading (optional) is a heading to print beforehand.
        """
        _print_object(self, heading=heading)

    def state_vars(self):
        """Return a list of all state-variable names in the state"""
        return [v for v in vars(self) if v != '__name__']


# Sequence number to use when making copies of multigoals.
_next_multigoal_number = 0

class Multigoal():
    """
    g = Multigoal(goal_name, **kwargs) creates an object that represents
    a conjunctive goal, i.e., the goal of reaching a state that contains
    all of the state-variable bindings in g.
      - goal_name is the name to use for the new multigoal.
      - The keyword args are name and desired values of state variables.

    Example: here are three equivalent ways to specify a goal named 'goal1'
    in which boxes b and c are located in room2 and room3:
        First:
           g = Multigoal('goal1')
           g.loc = {}   # create a dictionary for things like loc['b']
           g.loc['b'] = 'room2'
           g.loc['c'] = 'room3'
        Second:
           g = Multigoal('goal1', loc={})
           g.loc['b'] = 'room2'
           g.loc['c'] = 'room3'
        Third:
           g = Multigoal('goal1',loc={'b':'room2', 'c':'room3'})
    """

    def __init__(self, multigoal_name, **kwargs):
        """
        multigoal_name is the name to use for the multigoal. The keyword
        args are the names and desired values of state variables.
        """
        self.__name__ = multigoal_name
        vars(self).update(kwargs)
            
    def __str__(self):
        return f"<Multigoal {self.__name__}>"
        
    def __repr__(self):
        return _make_repr(self, 'Multigoal')

    def copy(self,new_name=None):
        """
        Make a copy of the multigoal. For its name, use new_name if it is given.
        Otherwise use the old name, with a suffix '_copy#' where # is an integer.
        """
        global _next_multigoal_number
        the_copy = copy.deepcopy(self)
        if new_name:
            the_copy.__name__ = new_name
        else:
            the_copy.__name__ = _name_for_copy(the_copy.__name__, _next_multigoal_number)
            _next_multigoal_number += 1
        return the_copy

    def display(self, heading=None):
        """
        Print the multigoal's state-variables and their values.
         - heading (optional) is a heading to print beforehand.
        """
        _print_object(self, heading=heading)

    def state_vars(self):
        """Return a list of all state-variable names in the multigoal"""
        return [v for v in vars(self) if v != '__name__']


################################################################################
# Auxiliary functions for state and multigoal objects.


def _make_repr(object, class_name):
    """Return a string that can be used to reconstruct the object"""
    x = f"{class_name}('{object.__name__}', "
    x += ', '.join([f'{v}={vars(object)[v]}' for v in vars(object) if v != '__name__'])
    x += ')'
    return x
    

def _name_for_copy(old_name,next_integer):
    """
    Create a name to use for a copy of an object.
    - old_name is the name of the old object.
    - next_integer is the number to use at the end of the new name.
    """
    # if old_name ends in '_copy#' where # is an integer, then
    # just replace # with next_integer
    if re.findall('_copy_[0-9]*$',old_name):
        new_name = re.sub('_[0-9]*$', f'_{next_integer}', old_name)
    # otherwise use old_name with '_copy' and next_integer appended
    else:
        new_name = f'{old_name}_copy_{next_integer}'
    return new_name


def _print_object(object, heading=None):
    """
    Print the state-variables and values in 'object', which may be either a
    state or a multigoal. 'heading' is an optional heading to print beforehand.
    """
    if heading == None:
        heading = get_type(object)
    if object != False:
        title = f"{heading} {object.__name__}:"
        dashes = '-'*len(title)
        print(title)
        print(dashes)
        for (varname,val) in vars(object).items():
            if varname != '__name__':
                print(f"  - {varname} = {val}")
        print('')
    else: 
        print('{heading} = False','\n')


# print_state and print_multigoal are identical except for their names.
print_state = _print_object
print_multigoal = _print_object

def get_type(object):
    """Return object's type name"""
    return type(object).__name__


################################################################################
# A class for holding planning-and-acting domains.


class Domain():
    """
    d = Domain(domain_name) creates an object to contain the actions, commands,
    and methods for a planning-and-acting domain. 'domain_name' is the name to
    use for the new domain.
    """

    def __init__(self,domain_name):
        """domain_name is the name to use for the domain."""

        global _domains, current_domain
        
        self.__name__ = domain_name

        _domains.append(self)
        current_domain = self
        
        # dictionary that maps each action name to the corresponding function
        self._action_dict = {}    
            
        # dictionary that maps each command name to the corresponding function
        self._command_dict = {}
        
        # dictionary that maps each task name to a list of relevant methods
        # _verify_g and _verify_mg are described later in this file.
        self._task_method_dict = \
            {'_verify_g': [_m_verify_g], '_verify_mg': [_m_verify_mg]}
        
        # dictionary that maps each unigoal name to a list of relevant methods
        self._unigoal_method_dict = {}
        
        # list of all methods for multigoals
        self._multigoal_method_list = []

    def __str__(self):
        return f"<Domain {self.__name__}>"
        
    def __repr__(self):
        return _make_repr(self, 'Domain')

    def copy(self,new_name=None):
        """
        Make a copy of the domain. For its name, use new_name if it is given.
        Otherwise use the old name, with a suffix '_copy#' where # is an integer.
        """
        global _next_domain_number
        the_copy = copy.deepcopy(self)
        if new_name:
            the_copy.__name__ = new_name
        else:
            the_copy.__name__ = _name_for_copy(the_copy.__name__, _next_domain_number)
            _next_domain_number += 1
        return the_copy

    def display(self):
        """Print the domain's actions, commands, and methods."""
        print_domain(self)
        

# Sequence number to use when making copies of domains.
_next_domain_number = 0

# A list of all domains that have been created
_domains = []


current_domain = None
"""
The Domain object that find_plan, run_lazy_lookahead, etc., will use.
"""

################################################################################
# Functions to print information about a domain


def print_domain(domain=None):
    """
    Print domain's actions, commands, and methods. The optional 'domain'
    argument defaults to the current domain
    """
    if domain == None:
        domain = current_domain
    print(f'\nDomain name: {domain.__name__}')
    print_actions(domain)
    print_commands(domain)
    print_methods(domain)

def print_actions(domain=None):
    """Print the names of all the actions"""
    if domain == None:
        domain = current_domain
    if domain._action_dict:
        print('-- Actions:', ', '.join(domain._action_dict))
    else:
        print('-- There are no actions --')

def print_operators():
    if verbose > 0:
        print("""
        >> print_operators exists to provide backward compatibility
        >> with Pyhop. In the future, please use print_actions instead.""")
    return print_actions()

def print_commands(domain=None):
    """Print the names of all the commands"""
    if domain == None:
        domain = current_domain
    if domain._command_dict:
        print('-- Commands:', ', '.join(domain._command_dict))
    else:
        print('-- There are no commands --')

def _print_task_methods(domain):
    """Print a table of the task_methods for each task"""
    if domain._task_method_dict:
        print('')
        print('Task name:         Relevant task methods:')
        print('---------------    ----------------------')
        for task in domain._task_method_dict:
            print(f'{task:<19}' + ', '.join(    \
                [f.__name__ for f in domain._task_method_dict[task]]))
        print('')
    else:
        print('-- There are no task methods --')

def _print_unigoal_methods(domain):
    """Print a table of the unigoal_methods for each state_variable_name"""
    if domain._unigoal_method_dict:
        print('State var name:    Relevant unigoal methods:')
        print('---------------    -------------------------')
        for var in domain._unigoal_method_dict:
            print(f'{var:<19}' + ', '.join( \
                [f.__name__ for f in domain._unigoal_method_dict[var]]))
        print('')
    else:
        print('-- There are no unigoal methods --')

def _print_multigoal_methods(domain):
    """Print the names of all the multigoal_methods"""
    if domain._multigoal_method_list:
        print('-- Multigoal methods:', ', '.join(  \
                [f.__name__ for f in domain._multigoal_method_list]))
    else:
        print('-- There are no multigoal methods --')
    
def print_methods(domain=None):
    """Print tables showing what all the methods are"""
    if domain == None:
        domain = current_domain
    _print_task_methods(domain)
    _print_unigoal_methods(domain)
    _print_multigoal_methods(domain)


################################################################################
# Functions to declare actions, commands, tasks, unigoals, multigoals


def declare_actions(*actions):
    """
    declare_actions adds each member of 'actions' to the current domain's list
    of actions. For example, this says that pickup and putdown are actions:
        declare_actions(pickup,putdown)
        
    declare_actions can be called multiple times to add more actions.
    
    You can see the current domain's list of actions by executing
        current_domain.display()
    """
    if current_domain == None:
        raise Exception(f"cannot declare actions until a domain has been created.")
    current_domain._action_dict.update({act.__name__:act for act in actions})
    return current_domain._action_dict



def declare_operators(*actions):
    if verbose > 0:
        print("""
        >> declare_operators exists to provide backward compatibility
        >> with Pyhop. In the future, please use declare_actions instead.""")
    return declare_actions(*actions)


def declare_commands(*commands):
    """
    declare_commands adds each member of 'commands' to the current domain's
    list of commands.  Each member of 'commands' should be a function whose
    name has the form c_foo, where foo is the name of an action. For example,
    this says that c_pickup and c_putdown are commands:
        declare_commands(c_pickup,c_putdown)
    
    declare_commands can be called several times to add more commands.

    You can see the current domain's list of commands by executing
        current_domain.display()

    """
    if current_domain == None:
        raise Exception(f"cannot declare commands until a domain has been created.")
    current_domain._command_dict.update({cmd.__name__:cmd for cmd in commands})
    return current_domain._command_dict


def declare_task_methods(task_name, *methods):
    """
    'task_name' should be a character string, and 'methods' should be a list
    of functions. declare_task_methods adds each member of 'methods' to the
    current domain's list of methods to use for tasks of the form
        (task_name, arg1, ..., argn).     

    Example:
        declare_task_methods('travel', travel_by_car, travel_by_foot)
    says that travel_by_car and travel_by_foot are methods and that GTPyhop
    should try using them for any task whose task name is 'travel', e.g.,
        ('travel', 'alice', 'store')
        ('travel', 'alice', 'umd', 'ucla')
        ('travel', 'alice', 'umd', 'ucla', 'slowly')
        ('travel', 'bob', 'home', 'park', 'looking', 'at', 'birds')

    This is like Pyhop's declare_methods function, except that it can be
    called several times to declare more methods for the same task.
    """
    if current_domain == None:
        raise Exception(f"cannot declare methods until a domain has been created.")
    if task_name in current_domain._task_method_dict:
        old_methods = current_domain._task_method_dict[task_name]
        # even though current_domain._task_method_dict[task_name] is a list,
        # we don't want to add any methods that are already in it
        new_methods = [m for m in methods if m not in old_methods]
        current_domain._task_method_dict[task_name].extend(new_methods)
    else:
        current_domain._task_method_dict.update({task_name:list(methods)})
    return current_domain._task_method_dict


def declare_methods(task, *methods):
    if verbose > 0:
        print("""
        >> declare_methods exists to provide backward compatibility with
        >> Pyhop. In the future, please use declare_task_methods instead.""")
    return declare_task_methods(task, *methods)


def declare_unigoal_methods(state_var_name, *methods):
    """
    'state_var_name' should be a character string, and 'methods' should be a
    list of functions. declare_unigoal_method adds each member of 'methods'
    to the current domain's list of relevant methods for goals of the form
        (state_var_name, arg, value)
    where 'arg' and 'value' are the state variable's argument and the desired
    value. For example,
        declare_unigoal_method('loc',travel_by_car)
    says that travel_by_car is relevant for goals such as these:
        ('loc', 'alice', 'ucla')
        ('loc', 'bob', 'home')

    The above kind of goal, i.e., a desired value for a single state
    variable, is called a "unigoal". To achieve a unigoal, GTPyhop will go
    through the unigoal's list of relevant methods one by one, trying each
    method until it finds one that is successful.

    To see each unigoal's list of relevant methods, use
        current_domain.display()    
    """
    if current_domain == None:
        raise Exception(f"cannot declare methods until a domain has been created.")
    if state_var_name not in current_domain._unigoal_method_dict:
        current_domain._unigoal_method_dict.update({state_var_name:list(methods)})
    else:
        old_methods = current_domain._unigoal_method_dict[state_var_name]
        new_methods = [m for m in methods if m not in old_methods]
        current_domain._unigoal_method_dict[state_var_name].extend(new_methods)
    return current_domain._unigoal_method_dict    


def declare_multigoal_methods(*methods):
    """
    declare_multigoal_methods adds each method in 'methods' to the current
    domain's list of multigoal methods. For example, this says that
    stack_all_blocks and unstack_all_blocks are multigoal methods:
        declare_multigoal_methods(stack_all_blocks, unstack_all_blocks)
    
    When GTPyhop tries to achieve a multigoal, it will go through the list
    of multigoal methods one by one, trying each method until it finds one
    that is successful. You can see the list by executing
        current_domain.display()

    declare_multigoal_methods can be called multiple times to add more
    multigoal methods to the list.
    
    For more information, see the docstring for the Multigoal class.
    """
    if current_domain == None:
        raise Exception(    \
                f"cannot declare methods until a domain has been created.")
    new_mg_methods = [m for m in methods if m not in \
                      current_domain._multigoal_method_list]
    current_domain._multigoal_method_list.extend(new_mg_methods)
    return current_domain._multigoal_method_list    

    
################################################################################
# A built-in multigoal method and its helper function.


def m_split_multigoal(state,multigoal):
    """
    m_split_multigoal is the only multigoal method that GTPyhop provides,
    and GTPyhop won't use it unless the user declares it explicitly using
        declare_multigoal_methods(m_split_multigoal)

    The method's purpose is to try to achieve a multigoal by achieving each
    of the multigoal's individual goals sequentially. Parameters:
        - 'state' is the current state
        - 'multigoal' is the multigoal to achieve 

    If multigoal is true in the current state, m_split_multigoal returns
    []. Otherwise, it returns a goal list
        [g_1, ..., g_n, multigoal],

    where g_1, ..., g_n are all of the goals in multigoal that aren't true
    in the current state. This tells the planner to achieve g_1, ..., g_n
    sequentially, then try to achieve multigoal again. Usually this means
    m_split_multigal will be used repeatedly, until it succeeds in producing
    a state in which all of the goals in multigoal are simultaneously true.

    The main problem with m_split_multigoal is that it isn't smart about
    choosing the order in which to achieve g_1, ..., g_n. Some orderings may
    work much better than others. Thus, rather than using the method as it's
    defined below, one might want to modify it to choose a good order, e.g.,
    by using domain-specific information or a heuristic function.
    """
    goal_dict = _goals_not_achieved(state,multigoal)
    goal_list = []
    for state_var_name in goal_dict:
        for arg in goal_dict[state_var_name]:
            val = goal_dict[state_var_name][arg]
            goal_list.append((state_var_name,arg,val))
    if goal_list:
        # achieve goals, then check whether they're all simultaneously true
        return goal_list + [multigoal]
    return goal_list


# helper function for m_split_multigoal above:

def _goals_not_achieved(state,multigoal):
    """
    _goals_not_achieved takes two arguments: a state s and a multigoal g.
    It returns a dictionary of the goals in g that aren't true in s.
    For example, suppose
        s.loc['c0'] = 'room0', g.loc['c0'] = 'room0',
        s.loc['c1'] = 'room1', g.loc['c1'] = 'room3',
        s.loc['c2'] = 'room2', g.loc['c2'] = 'room4'.
    Then _goals_not_achieved(s, g) will return
        {'loc': {'c1': 'room3', 'c2': 'room4'}}    
    """
    unachieved = {}
    for name in vars(multigoal):
        if name != '__name__':
            for arg in vars(multigoal).get(name):
                val = vars(multigoal).get(name).get(arg)
                if val != vars(state).get(name).get(arg):
                    # want arg_value_pairs.name[arg] = val
                    if not unachieved.get(name):
                        unachieved.update({name:{}})
                    unachieved.get(name).update({arg:val})
    return unachieved


################################################################################
# Functions to verify whether unigoal_methods achieve the goals they are
# supposed to achieve.


verify_goals = True
"""
If verify_goals is True, then whenever the planner uses a method m to refine
a unigoal or multigoal, it will insert a "verification" task into the
current partial plan. If verify_goals is False, the planner won't insert any
verification tasks into the plan.

The purpose of the verification task is to raise an exception if the
refinement produced by m doesn't achieve the goal or multigoal that it is
supposed to achieve. The verification task won't insert anything into the
final plan; it just will verify whether m did what it was supposed to do.
"""


def _m_verify_g(state, method, state_var, arg, desired_val, depth):
    """
    _m_verify_g is a method that GTPyhop uses to check whether a
    unigoal method has achieved the goal for which it was used.
    """
    if vars(state)[state_var][arg] != desired_val:
        raise Exception(f"depth {depth}: method {method} didn't achieve",
                f"goal {state_var}[{arg}] = {desired_val}")
    if verbose >= 3:
        print(f"depth {depth}: method {method} achieved",
                f"goal {state_var}[{arg}] = {desired_val}")
    return []       # i.e., don't create any subtasks or subgoals


def _m_verify_mg(state, method, multigoal, depth):
    """
    _m_verify_g is a method that GTPyhop uses to check whether a multigoal
    method has achieved the multigoal for which it was used.
    """
    goal_dict = _goals_not_achieved(state,multigoal)
    if goal_dict:
        raise Exception(f"depth {depth}: method {method} " + \
                        f"didn't achieve {multigoal}]")
    if verbose >= 3:
        print(f"depth {depth}: method {method} achieved {multigoal}")
    return []


################################################################################
# Applying actions, commands, and methods


def _apply_action_and_continue(state, task1, todo_list, plan, depth):
    """
    _apply_action_and_continue is called only when task1's name matches an
    action name. It applies the action by retrieving the action's function
    definition and calling it on the arguments, then calls seek_plan
    recursively on todo_list.
    """
    if verbose >= 3:
        print(f'depth {depth} action {task1}: ', end='')
    action = current_domain._action_dict[task1[0]]
    newstate = action(state.copy(),*task1[1:])
    if newstate:
        if verbose >= 3:
            print('applied')
            newstate.display()
        return seek_plan(newstate, todo_list, plan+[task1], depth+1)
    if verbose >= 3:
        print('not applicable')
    return False


def _refine_task_and_continue(state, task1, todo_list, plan, depth):
    """
    If task1 is in the task-method dictionary, then iterate through the list
    of relevant methods to find one that's applicable, apply it to get
    additional todo_list items, and call seek_plan recursively on
            [the additional items] + todo_list.

    If the call to seek_plan fails, go on to the next method in the list.
    """
    relevant = current_domain._task_method_dict[task1[0]]
    if verbose >= 3:
        print(f'depth {depth} task {task1} methods {[m.__name__ for m in relevant]}')
    for method in relevant:
        if verbose >= 3: 
            print(f'depth {depth} trying {method.__name__}: ', end='')
        subtasks = method(state, *task1[1:])
        # Can't just say "if subtasks:", because that's wrong if subtasks == []
        if subtasks != False and subtasks != None:
            if verbose >= 3:
                print('applicable')
                print(f'depth {depth} subtasks: {subtasks}')
            result = seek_plan(state, subtasks+todo_list, plan, depth+1)
            if result != False and result != None:
                return result
        else:
            if verbose >= 3:
                print(f'not applicable')
    if verbose >= 3:
        print(f'depth {depth} could not accomplish task {task1}')        
    return False


def _refine_unigoal_and_continue(state, goal1, todo_list, plan, depth):
    """
    If goal1 is in the unigoal-method dictionary, then iterate through the
    list of relevant methods to find one that's applicable, apply it to get
    additional todo_list items, and call seek_plan recursively on
          [the additional items] + [verify_g] + todo_list,

    where [verify_g] verifies whether the method actually achieved goal1.
    If the call to seek_plan fails, go on to the next method in the list.
    """
    if verbose >= 3:
        print(f'depth {depth} goal {goal1}: ', end='')
    (state_var_name, arg, val) = goal1
    if vars(state).get(state_var_name).get(arg) == val:
        if verbose >= 3:
            print(f'already achieved')
        return seek_plan(state, todo_list, plan, depth+1)
    relevant = current_domain._unigoal_method_dict[state_var_name]
    if verbose >= 3:
        print(f'methods {[m.__name__ for m in relevant]}')
    for method in relevant:
        if verbose >= 3: 
            print(f'depth {depth} trying method {method.__name__}: ', end='')
        subgoals = method(state,arg,val)
        # Can't just say "if subgoals:", because that's wrong if subgoals == []
        if subgoals != False and subgoals != None:
            if verbose >= 3:
                print('applicable')
                print(f'depth {depth} subgoals: {subgoals}')
            if verify_goals:
                verification = [('_verify_g', method.__name__, \
                                 state_var_name, arg, val, depth)]
            else:
                verification = []
            todo_list = subgoals + verification + todo_list
            result = seek_plan(state, todo_list, plan, depth+1)
            if result != False and result != None:
                return result
        else:
            if verbose >= 3:
                print(f'not applicable')        
    if verbose >= 3:
        print(f'depth {depth} could not achieve goal {goal1}')        
    return False


def _refine_multigoal_and_continue(state, goal1, todo_list, plan, depth):
    """
    If goal1 is a multigoal, then iterate through the list of multigoal
    methods to find one that's applicable, apply it to get additional
    todo_list items, and call seek_plan recursively on
          [the additional items] + [verify_mg] + todo_list,

    where [verify_mg] verifies whether the method actually achieved goal1.
    If the call to seek_plan fails, go on to the next method in the list.
    """
    if verbose >= 3:
        print(f'depth {depth} multigoal {goal1}: ', end='')
    relevant = current_domain._multigoal_method_list
    if verbose >= 3:
        print(f'methods {[m.__name__ for m in relevant]}')
    for method in relevant:
        if verbose >= 3: 
            print(f'depth {depth} trying method {method.__name__}: ', end='')
        subgoals = method(state,goal1)
        # Can't just say "if subgoals:", because that's wrong if subgoals == []
        if subgoals != False and subgoals != None:
            if verbose >= 3:
                print('applicable')
                print(f'depth {depth} subgoals: {subgoals}')
            if verify_goals:
                verification = [('_verify_mg', method.__name__, goal1, depth)]
            else:
                verification = []
            todo_list = subgoals + verification + todo_list
            result = seek_plan(state, todo_list, plan, depth+1)
            if result != False and result != None:
                return result
        else:
            if verbose >= 3:
                print(f'not applicable')
    if verbose >= 3:
        print(f'depth {depth} could not achieve multigoal {goal1}')        
    return False


############################################################
# The planning algorithm


def find_plan(state, todo_list):
    """
    find_plan tries to find a plan that accomplishes the items in todo_list,
    starting from the given state, using whatever methods and actions you
    declared previously. If successful, it returns the plan. Otherwise it
    returns False. Arguments:
     - 'state' is a state;
     - 'todo_list' is a list of goals, tasks, and actions.
    """
    if verbose >= 1: 
        todo_string = '[' + ', '.join([_item_to_string(x) for x in todo_list]) + ']'
        print(f'FP> find_plan, verbose={verbose}:')
        print(f'    state = {state.__name__}\n    todo_list = {todo_string}')
    result = seek_plan(state, todo_list, [], 0)
    if verbose >= 1: print('FP> result =',result,'\n')
    return result


def pyhop(state, todo_list):
    if verbose > 0:
        print("""
        >> The function 'pyhop' exists to provide backward compatibility
        >> with Pyhop. In the future, please use find_plan instead.""")
    return find_plan(state, todo_list)


def seek_plan(state, todo_list, plan, depth):
    """
    Workhorse for find_plan. Arguments:
     - state is the current state
     - todo_list is the current list of goals, tasks, and actions
     - plan is the current partial plan
     - depth is the recursion depth, for use in debugging
    """
    if verbose >= 2: 
        todo_string = '[' + ', '.join([_item_to_string(x) for x in todo_list]) + ']'
        print(f'depth {depth} todo_list ' + todo_string)
    if todo_list == []:
        if verbose >= 3:
            print(f'depth {depth} no more tasks or goals, return plan')
        return plan
    item1 = todo_list[0]
    ttype = get_type(item1)
    if ttype in {'Multigoal'}:
        return _refine_multigoal_and_continue(state, item1, todo_list[1:], plan, depth)
    elif ttype in {'list','tuple'}:
        if item1[0] in current_domain._action_dict:
            return _apply_action_and_continue(state, item1, todo_list[1:], plan, depth)
        elif item1[0] in current_domain._task_method_dict:
            return _refine_task_and_continue(state, item1, todo_list[1:], plan, depth)
        elif item1[0] in current_domain._unigoal_method_dict:
            return _refine_unigoal_and_continue(state, item1, todo_list[1:], plan, depth)
    raise Exception(    \
        f"depth {depth}: {item1} isn't an action, task, unigoal, or multigoal\n")
    return False


def _item_to_string(item):
    """Return a string representation of a task or goal."""
    ttype = get_type(item)
    if ttype == 'list':
        return str([str(x) for x in item])
    elif ttype == 'tuple':
        return str(tuple([str(x) for x in item]))
    else:       # a multigoal
        return str(item)


################################################################################
# An actor


def run_lazy_lookahead(state, todo_list, max_tries=10):
    """
    An adaptation of the run_lazy_lookahead algorithm from Ghallab et al.
    (2016), Automated Planning and Acting. It works roughly like this:
        loop:
            plan = find_plan(state, todo_list)
            if plan = [] then return state    // the new current state 
            for each action in plan:
                try to execute the corresponding command
                if the command fails, continue the outer loop
    Arguments: 
      - 'state' is a state;
      - 'todo_list' is a list of tasks, goals, and multigoals;
      - max_tries is a bound on how many times to execute the outer loop.
      
    Note: whenever run_lazy_lookahead encounters an action for which there is
    no corresponding command definition, it uses the action definition instead.
    """
    
    if verbose >= 1: 
        print(f"RLL> run_lazy_lookahead, verbose = {verbose}, max_tries = {max_tries}")
        print(f"RLL> initial state: {state.__name__}")
        print('RLL> To do:', todo_list)

    for tries in range(1,max_tries+1):
        if verbose >= 1: 
            ordinals = {1:'st',2:'nd',3:'rd'}
            if ordinals.get(tries):
                print(f"RLL> {tries}{ordinals.get(tries)} call to find_plan:\n")
            else:
                print(f"RLL> {tries}th call to find_plan:\n")
        plan = find_plan(state, todo_list)
        if plan == False or plan == None:
            if verbose >= 1:
                raise Exception(
                        f"run_lazy_lookahead: find_plan has failed")
            return state
        if plan == []:
            if verbose >= 1: 
                print(f'RLL> Empty plan => success',
                      f'after {tries} calls to find_plan.')
            if verbose >= 2: state.display(heading='> final state')
            return state
        for action in plan:
            command_name = 'c_' + action[0]
            command_func = current_domain._command_dict.get(command_name)
            if command_func == None:
                if verbose >= 1: 
                    print(f'RLL> {command_name} not defined, using {action[0]} instead\n')
                command_func = current_domain._action_dict.get(action[0])
                
            if verbose >= 1:
                print('RLL> Command:', [command_name] + list(action[1:]))
            new_state = _apply_command_and_continue(state, command_func, action[1:])
            if new_state == False:
                if verbose >= 1: 
                    print(f'RLL> WARNING: command {command_name} failed; will call find_plan.')
                    break
            else:
                if verbose >= 2: 
                    new_state.display()
                state = new_state
        # if state != False then we're here because the plan ended
        if verbose >= 1 and state:
            print(f'RLL> Plan ended; will call find_plan again.')
        
    if verbose >= 1: print('RLL> Too many tries, giving up.')
    if verbose >= 2: state.display(heading='RLL> final state')
    return state


def _apply_command_and_continue(state, command, args):
    """
    _apply_command_and_continue applies 'command' by retrieving its
    function definition and calling it on the arguments.
    """
    if verbose >= 3:
        print(f"_apply_command_and_continue {command.__name__}, args = {args}")
    next_state = command(state.copy(),*args)
    if next_state:
        if verbose >= 3:
            print('applied')
            next_state.display()
        return next_state
    else:
        if verbose >= 3:
            print('not applicable')
        return False


###############################################################################
# Print brief information about how to interpret the program's output

print(f"\nImported GTPyhop version 1.0.")
print(f"Messages from find_plan will be prefaced with 'FP>'.")
print(f"Messages from run_lazy_lookahead will be prefaced with 'RLL>'.")
