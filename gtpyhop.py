"""
GTPyhop is a planner based on Pyhop, that can plan for both tasks and
goals. It requires Python 3. 

This file provides the following classes, functions, and variables. There
are docstrings for each of them. A good place to start might be the
docstrings for find_plan and run_lazy_lookahead.

- classes and their methods: 
    Domain:    copy, display
    Multigoal: copy, display
    State:     copy, display

- functions:
    find_plan              seek_plan                 run_lazy_lookahead
    declare_actions        declare_commands        
    declare_task_methods   declare_unigoal_methods   declare_multigoal_methods
    print_actions          print_commands            print_methods
    get_type               m_split_multigoal

- global variables:
    current_domain         verbose          verify_goals

Accompanying this file are a README.md file that's an overview of GTPyhop,
and several files to give examples of how to use GTPyhop. To run them, try
importing one or more of the following from the Examples directory:
    simple_goals                simple_tasks
    simple_tasks_with_error     backtracking_tasks
    blocks_tasks                blocks_goals
    blocks_goal_splitting       pyhop_simple_travel_example

See also the blocked comment entitled "Applying actions and commands".
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
    Each member of actions must be a function name (not a string).
    declare_actions tells GTPyhop that each of them is an action. For
    example, this tells GTPyhop that pickup and putdown are actions:
        declare_actions(pickup,putdown)
    
    declare_actions can be called several times to declare more actions.
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
    Each member of commands must be a function name (not a string), and the
    name should have the form c_foo, where foo is the name of an action.
    declare_commands tells GTPyhop that each of the functions is a command.
    Example: the following tells GTPyhop that c_pickup and c_putdown are
    commands:
        declare_commands(c_pickup,c_putdown)
    
    declare_commands can be called several times to declare more commands.
    """
    if current_domain == None:
        raise Exception(f"cannot declare commands until a domain has been created.")
    current_domain._command_dict.update({cmd.__name__:cmd for cmd in commands})
    return current_domain._command_dict


def declare_task_methods(task_name, *methods):
    """
    declare_task_methods modifies the current domain (i.e., the domain object
    stored in the global variable 'current_domain') to specify that the
    methods are relevant for tasks of the form (task_name, arg1, ..., argn).     
      - task_name must be a character string
      - each member of 'methods' must be a function name    

    Example:
        declare_task_methods('travel', travel_by_car, travel_by_foot)
    tells Pyhop that travel_by_car and travel_by_foot are methods and are 
    relevant for tasks such as these:
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


def declare_unigoal_methods(var_name, *methods):
    """
    GTPyhop has two types of goals: unigoals (individual goals) and multigoals 
    (conjunctions of goals). A unigoal is represented as a 3-tuple
            (name, arg, value)
    giving a desired value for a state variable. For example,
            ('loc', 'robot1', 'location2') 
    says we want to reach a state s in which s.loc['robot1'] = 'location2'.
    
    declare_unigoal_methods(var_name, *methods) declares that the methods
    in 'methods' are relevant for any unigoal (name, arg, value) such that
    name is 'var_name'.
        - 'var_name' must be a character string
        - each member of 'methods' must be a function name    
    Example:
            declare_unigoal_method('loc',travel_by_car)
    says that travel_by_car is relevant for goals such as these:
            ('loc', 'alice', 'ucla')
            ('loc', 'bob', 'home')

    The declaration becomes part of the current domain (i.e., the domain
    object stored in the global variable 'current_domain').
    
    declare_unigoal_methods can be called several times to declare more
    methods for the same goal.
    """
    if current_domain == None:
        raise Exception(f"cannot declare methods until a domain has been created.")
    if var_name not in current_domain._unigoal_method_dict:
        current_domain._unigoal_method_dict.update({var_name:list(methods)})
    else:
        old_methods = current_domain._unigoal_method_dict[var_name]
        new_methods = [m for m in methods if m not in old_methods]
        current_domain._unigoal_method_dict[var_name].extend(new_methods)
    return current_domain._unigoal_method_dict    


def declare_multigoal_methods(*methods):
    """
    declare_multigoal_methods modifies the current domain (i.e., the domain
    object stored in the global variable 'current_domain') to specify that
    the methods are relevant for all multigoals.
      - each member of 'methods' must be a function name    

    Example:
        declare_multigoal_methods(stack_all_blocks,unstack_all_blocks)
    says that stack_all_blocks and unstack_all_blocks are multigoal methods.

    declare_multigoal_methods can be called several times to declare
    more multigoal methods.
    
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
    m_split_multigoal is the only multigoal method that GTPyhop provides, and
    GTPyhop won't use it unless the user declares it explicitly using
    gtpyhop.declare_multigoal_methods. Its purpose is to achieve a multigoal
    by sequentially achieving the multigoal's individual goals. Parameters:
        - state is the current state
        - multigoal is the multigoal to achieve 

    If multigoal is true in the current state, then m_split_multigoal returns
    []. Otherwise, it returns a goal list [g_1, ..., g_n, multigoal], where
    g_1, ..., g_n are the goals in multigoal that aren't true in the current
    state. This tells the planner to achieve g_1, ..., g_n sequentially, and
    then try again to achieve multigoal. 

    If the planner again uses m_split_multigoal to try to achieve multigoal,
    m_split_multigoal will produce another list like the one above. This will
    keep happening until the planner produces a state in which all of the
    goals in multigoal are simultaneously true.

    The main problem with m_split_multigoal is that it isn't smart about
    choosing the order in which to achieve g_1, ..., g_n. Some orderings may
    work much better than others. Thus it might be desirable to modify
    the method to use a heuristic function to choose a good order.
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
a unigoal or multigoal, it will insert a "verification" task into the current
partial plan. If verify_goals is False, the planner won't insert any
verification tasks into the plan.
    
The purpose of the verification task is to raise an exception if the refinement
produced by m doesn't achieve the goal or multigoal that it is supposed to
achieve. The verification task won't insert anything into the final plan; it
just will verify whether m did what it was supposed to do.
"""


def _m_verify_g(state, method, state_var, arg, desired_val, depth):
    """
    _m_verify_g is a method that GTPyhop uses to check whether a unigoal_method
    has achieved the goal that it was used to achieve.
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
    method has achieved the multigoal that it was used to achieve.
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


def _apply_action(state, task1, agenda, plan, depth):
    """
    apply_action is called only when task1's name matches an action name.
    It applies the action by retrieving the action's function definition
    and calling it on the arguments.
    """
    if verbose >= 3:
        print(f'depth {depth} action {task1}: ', end='')
    action = current_domain._action_dict[task1[0]]
    newstate = action(state.copy(),*task1[1:])
    if newstate:
        if verbose >= 3:
            print('applied')
            newstate.display()
        return seek_plan(newstate, agenda, plan+[task1], depth+1)
    if verbose >= 3:
        print('not applicable')
    return False


def _apply_command(state, command, args):
    """
    apply_command is called only when task1's name matches a command name.
    It applies the command by retrieving the command's function definition
    and calling it on the arguments.
    """
    if verbose >= 3:
        print(f"_apply_command {command.__name__}, args = {args}")
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


def _find_task_method(state, task1, agenda, plan, depth):
    """
    If task1 is in the task-method dictionary, then iterate through the
    list of relevant methods until we find one that's applicable, apply
    it to get additional agenda items, and call seek_plan recursively on
            [the additional items] + agenda.
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
            result = seek_plan(state, subtasks+agenda, plan, depth+1)
            if result != False and result != None:
                return result
        else:
            if verbose >= 3:
                print(f'not applicable')
    if verbose >= 3:
        print(f'depth {depth} could not accomplish task {task1}')        
    return False


def _find_unigoal_method(state, goal1, agenda, plan, depth):
    """
    If goal1 is in the unigoal-method dictionary, then iterate through the
    list of relevant methods until we find one that's applicable, apply it
    to get additional agenda items, and call seek_plan recursively on
          [the additional items] + [verify_g] + agenda,
    where [verify_g] verifies whether the method actually achieved goal1.
    If the call to seek_plan fails, go on to the next method in the list.
    """
    if verbose >= 3:
        print(f'depth {depth} goal {goal1}: ', end='')
    (state_var_name, arg, val) = goal1
    if vars(state).get(state_var_name).get(arg) == val:
        if verbose >= 3:
            print(f'already achieved')
        return seek_plan(state, agenda, plan, depth+1)
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
            agenda = subgoals + verification + agenda
            result = seek_plan(state, agenda, plan, depth+1)
            if result != False and result != None:
                return result
        else:
            if verbose >= 3:
                print(f'not applicable')        
    if verbose >= 3:
        print(f'depth {depth} could not achieve goal {goal1}')        
    return False


def _find_multigoal_method(state, goal1, agenda, plan, depth):
    """
    If goal1 is a multigoal, then iterate through the list of multigoal
    methods until we find one that's applicable, apply it to get additional
    agenda items, and call seek_plan recursively on
          [the additional items] + [verify_mg] + agenda,
    where [verify_mg] verifies whether the method actually achieved goal1.
    If the call to seek_plan fails, go on to the next method in the list.


    Unlike with unigoal methods, the call to seek_plan doesn't include a
    verification test because it's not clear what we're supposed to verify.
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
            agenda = subgoals + verification + agenda
            result = seek_plan(state, agenda, plan, depth+1)
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


def find_plan(state, agenda):
    """
    find_plan tries to find a plan that accomplishes the items in agenda,
    starting from the given state, using whatever methods and actions you 
    declared previously. If successful, it returns the plan. Otherwise it
    returns False. Arguments:
     - 'state' is a state;
     - 'agenda' is a list of goals, tasks, and actions;
    """
    if verbose >= 1: 
        agenda_str = '[' + ', '.join([_item_to_string(x) for x in agenda]) + ']'
        print(f'FP> find_plan, verbose={verbose}:')
        print(f'    state = {state.__name__}\n    agenda = {agenda_str}')
    result = seek_plan(state, agenda, [], 0)
    if verbose >= 1: print('FP> result =',result,'\n')
    return result


def pyhop(state, agenda):
    if verbose > 0:
        print("""
        >> The function 'pyhop' exists to provide backward compatibility
        >> with Pyhop. In the future, please use find_plan instead.""")
    return find_plan(state, agenda)


def seek_plan(state, agenda, plan, depth):
    """
    Workhorse for find_plan. Arguments:
     - state is the current state
     - agenda is the current list of goals, tasks, and actions
     - plan is the current partial plan
     - depth is the recursion depth, for use in debugging
    """
    if verbose >= 2: 
        agenda_str = '[' + ', '.join([_item_to_string(x) for x in agenda]) + ']'
        print(f'depth {depth} agenda ' + agenda_str)
    if agenda == []:
        if verbose >= 3:
            print(f'depth {depth} no more tasks or goals, return plan')
        return plan
    item1 = agenda[0]
    ttype = get_type(item1)
    if ttype in {'list','tuple'}:
        if item1[0] in current_domain._action_dict:
            return _apply_action(state, item1, agenda[1:], plan, depth)
        elif item1[0] in current_domain._task_method_dict:
            return _find_task_method(state, item1, agenda[1:], plan, depth)
        elif item1[0] in current_domain._unigoal_method_dict:
            return _find_unigoal_method(state, item1, agenda[1:], plan, depth)
    elif ttype in {'Multigoal'}:
        return _find_multigoal_method(state, item1, agenda[1:], plan, depth)

    raise Exception(    \
        f"depth {depth}: {item1} isn't an action, task, goal, or multigoal\n")
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


def run_lazy_lookahead(state, agenda, max_tries=10):
    """
    An adaptation of the run_lazy_lookahead algorithm from Ghallab et al.
    (2016), Automated Planning and Acting. It works roughly like this:
        loop:
            plan = find_plan(state, agenda)
            if plan = []:
                return state    // the new current state 
            for each action in plan:
                execute the corresponding command
                if the command fails:
                    continue the outer loop
    Arguments: 
      - 'state' is a state;
      - 'agenda' is a list of tasks, goals, and multigoals;
      - max_tries is a bound on how many times to execute the outer loop.
      
    Note: whenever run_lazy_lookahead encounters an action for which there is
    no corresponding command definition, it uses the action definition instead.
    """
    
    if verbose >= 1: 
        print(f"RLL> run_lazy_lookahead, verbose = {verbose}, max_tries = {max_tries}")
        print(f"RLL> initial state: {state.__name__}")
        print('RLL> To do:', agenda)

    for tries in range(1,max_tries+1):
        if verbose >= 1: 
            ordinals = {1:'st',2:'nd',3:'rd'}
            if ordinals.get(tries):
                print(f"RLL> {tries}{ordinals.get(tries)} call to find_plan:\n")
            else:
                print(f"RLL> {tries}th call to find_plan:\n")
        plan = find_plan(state, agenda)
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
            new_state = _apply_command(state, command_func, action[1:])
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

###############################################################################
# Create a default domain for GTPyhop to use if the user doesn't define one.
# I would prefer to put this near the definition of the Domain class, but it
# must come after some things that the Domain class's __init__ function uses.

current_domain = Domain('default domain')

print(f"\nImported GTPyhop version 1.0.")
print(f"Messages from find_plan will be prefaced with 'FP>'.")
print(f"Messages from run_lazy_lookahead will be prefaced with 'RLL>'.")
