
# Additional Information about GTPyhop

> **Dana S. Nau**  
> University of Maryland  
> July 22, 2021

---

## Contents

 1. [Planning algorithm](#Planning)
 2. [States and actions](#States)
 3. [Tasks and task methods](#Tasks)
 4. [Goals and goal methods](#Goals)
 5. [Other properties of goals and tasks](#Other)
 6. [Backward compatibility with Pyhop](#Pyhop)
 7. [Comparisons with other planners](#GDP)  
     7.1. [GDP and GoDeL](#GDP)  
     7.2. [HGNpyhop](#HGNpyhop)
 8. [References](#References)

---

Before reading this document, you might want to read [[Nau21](#Nau21)] to get some familarity with GTPyhop.

## <span id="Planning">1. Planning algorithm</span>

Here is a summary of GTPyhop's planning algorithm. For pseudocode, see [[Nau21](#Nau21)].

GTPyhop starts with an initial [state](#States) *s*, and a *to-do* list *T* consisting of [actions](#States), [tasks](#Tasks), and [goals](#Goals). The objective is to construct a *solution plan* π, i.e., a sequence of actions that begins in *s* and accomplishes all of the items in *T* in left-to-right order. 
GTPyhop does this in a *planning domain* that includes definitions of actions, methods for accomplishing tasks, and methods for achieving goals. 


GTPyhop does a backtracking search, starting with an empty list π. It goes left-to-right through the items in *T*, and considers the following possibilities for each item:

  - If the item is an applicable action *a*, GTPyhop executes *a* to update *s*, and appends *a* to π.
  - If the item is a task *t*, GTPyhop looks for a task method that is both relevant for *t* and applicable in *s*, and uses it to get a to-do list for accomplishing *t*. GTPyhop inserts the items in this list into *T* to do next.
  - If the item is a goal *g*, GTPyhop looks for a goal method that is both relevant for *g* and applicable in *s*, and uses it to get a to-do list for achieving *g*. GTPyhop inserts the items in this list into *T* to do next, along with a way to check whether they actually achieve *g*.
  - Whenever one of the above steps fails (e.g., an action is inapplicable, a goal or task has no applicable methods, or a goal method doesn't achieve its goal), GTPyhop backtracks to the last point where it chose a method for a task or goal, to try a different method if one is available.

If GTPyhop reaches the end of *T*, it returns π as the solution plan. If GTPyhop is unable to reach the end of *T*, it returns failure.

## <span id="States">2. States and actions</span>

### States

GTPyhop, like Pyhop, represents a state as an object that contains state-variable
bindings. For example, consider the following state object:

    state0 = gtpyhop.State('state0')
    state0.loc = {'alice':'home', 'taxi1':'park'}
    state0.cash = {'alice':20}
    state0.distance = {('home','park'):8, ('station','home'):1, ('station','park'):9}
    
This specifies that 

    state0.loc['alice'] = 'home_a',
    state0.loc['taxi1'] = 'park',
    state0.cash['alice'] = 20,
    state0.distance[('home','park')] = 8,
    state0.distance[('station','home')] = 1,
    state0.distance[('station','park')] = 9.

Note that each state variable has exactly one argument, e.g., `'alice'` or `'taxi1'`. However, the argument may be any hashable Python object, e.g., `'alice'` or the tuple  `('station','home')`, but not the list `['station','home']`.

Although a `State` is object is used mainly to represent a state of the world, it can also be used for other collections of variables. For example, in [Examples/simple_htn.py](Examples/simple_htn.py) and [Examples/simple_hgn.py](Examples/simple_hgn.py), the `State` object named `rigid` contains some "rigid" properties that are true in every state of the world.
    

### Actions

Actions in GTPyhop are written in much the same way as in Pyhop. For example, here is a GTPyhop action for unloading a container from a robot at a particular location:

    def unload(state, robot, container, location):
        if state.loc[container] == robot and state.loc[robot] == location:
            state.loc[container] = location
            state.cargo[robot] = 'nil'
            return state

    gtpyhop.declare_actions(unload)

In Pyhop there would be two minor differences:

- If an action is inapplicable (i.e., if the `if` test fails in the above example), Pyhop would require it to return `False`. In GTPyhop, it may either return `False` or (as above) not return a value.

 - The last line would begin with `pyhop` rather than `gtpyhop`.
 

## <span id="Tasks">3. Tasks and task methods</span>

In GTPyhop, as in Pyhop, a task is written as a tuple that specifies an activity to perform, e.g.,

    (task_name, arg1, arg2, ..., argn)

Methods for tasks look nearly the same as in Pyhop. For example, this:

    def m_unload_container(state, container, location):
        # 'is_a' needs to be a function that returns an object's type
        r = state.loc[container]
        if is_a(r, 'robot') and state.loc[r] == location:
            return [('unload', r, container, location)]

    gtpyhop.declare_task_methods('unload_container', m_unload_container)

defines a task method called `m_unload_container` and tells GTPyhop to consider using it for any task of the form

    ('unload_container' container location)

In Pyhop there would be two minor differences:

- If a method is inapplicable (i.e., if the `if` test fails in the above example), Pyhop requires it to return `False`. In GTPyhop, it may either return `False` or (as above) not return a value.

 - The last line would begin with `pyhop` rather than `gtpyhop`.
 

## <span id="Goals">4. Goals and goal methods</span>

GTPyhop has two types of goals: *unigoals* (individual goals) and *multigoals* (conjunctions of individual goals).

### Unigoals

A unigoal is a 3-tuple `(state_variable_name, arg, value)` that specifies a desired value for a state variable. For example, the following unigoal represents the goal of reaching a state `s` such that `s.loc['c1'] = 'loc2'`:

    ('loc', 'c1', 'loc2') 

Notice that the above triple has the same syntax as a taskname with two arguments. The way to tell GTPyhop that it is a unigoal, rather than a task, is to declare a *unigoal method* for it. A unigoal method always takes three arguments: the current state, and the name and argument of the state-variable. If a unigoal method is applicable, it returns a (possibly empty) list of actions, tasks, and goals. For example, here is a method for the above unigoal:

    def m_unload_at_loc(state, container, location):
        r = state.loc[container]
        # 'is_a' needs to be a function that returns an object's type
        if is_a(r, 'robot') and state.loc[r] == location:
            return [('unload', r, container, location)]

    gtpyhop.declare_unigoal_methods('loc', m_unload_at_loc)

This looks nearly identical to the task method defined earlier, except for the `declare_unigoal_methods` declaration. In this simple example, it doesn't make much difference whether we use a task or a unigoal, but there are various situations where each of them may be more preferable than the other.

**Restricting a unigoal method's relevance:**

The above declaration tells GTPyhop that `m_unload_at_loc` is relevant not only for `('loc', 'c1', 'loc2')`, but also for any other unigoal of the form `('loc',` *arg*, *value*). That is probably more general than what we want. To make GTPyhop use the method only when *arg* is a container and *value* is a location, we can rewrite it to include an additional `if` test that excludes other values of *arg* and *value*:

    def m_unload_at_loc(state, container, location):
        if is_a(container, 'container') and is_a(location, 'location'):
            r = state.loc[container]
            if is_a(r, 'robot') and state.loc[r] == location:
                return [('unload', r, container, location)]

    gtpyhop.declare_unigoal_methods('loc', m_unload_at_loc)

For an example of a situation where such restrictions are important, see the definitions of `m_move1`, `m_get`, and `m_put` in the [Examples/blocks_hgn/methods.py](Examples/blocks_hgn/methods.py) file.
    

### Multigoals

Syntactically, a multigoal looks similar to a state -- but unlike a state, it specifies desired (rather than current) values for some (rather than all) of the state variables. For example, here is a multigoal saying we want to reach any state `s` such that `s.loc['c1'] = 'loc2'` and `s.loc['c3'] = 'loc4'`:

    g = Multigoal('goal1')
    g.loc = {'c1':'loc2', 'c3':'loc4'}

A multigoal method always takes two arguments: the current state and the multigoal.  If it is applicable, it returns a (possibly empty) list of actions, tasks, and goals. For example, here is a multigoal method that might be useful for `goal1`:

    def m_move_to_loc2(state,mg):
        containers_to_move = [c for c in mg.loc if \
                is_a(c,'container') and s.loc != 'loc2']
        # for this to work, we'll need to define a 'distance' function:
        containers_to_move.sort(key = lambda x: distance(loc[x],'loc2'))
        return [('loc', c, mg.loc[c]) for c in containers_to_move]

    gtpyhop.declare_multigoal_methods(m_unload_at_loc)

This method returns a list of unigoals, one for each container that needs to be moved to `loc2`. The containers are sorted in order of their distance from `loc2`, so that the closest ones will be moved first. 

**Restricting a multigoal method's relevance:**

The `declare_multigoal_methods` declaration says that `m_move_to_loc2` is relevant not only for `goal1`, but for all multigoals. If you want GTPyhop to use the method only for certain kinds of multigoals, the body of the method will need to include some `if` tests to exclude the other multigoals:

    def m_move_to_loc2(state,mg):
        # require mg to include some locations of containers:
        if 'loc' in mg.state_vars() and \
                [c for c in mg.loc if is_a(item,'container')]:
            containers_to_move = [c for c in mg.loc if \
                    is_a(c,'container') and s.loc != 'loc2']
            # for this to work, we'll need to define a 'distance' function:
            containers_to_move.sort(key = lambda x: distance(loc[x],'loc2'))
            return [('loc', c, mg.loc[c]) for c in containers_to_move]

    gtpyhop.declare_multigoal_methods(m_unload_at_loc)

For the above method to work, we would need to define a unigoal method, e.g., `move_c_to_loc(c,l)` for moving a container `c` to a location `l`, and declare

    gtpyhop.declare_unigoal_methods('loc', move_c_to_loc)


## <span id="Other">5. Other properties of goals and tasks</span>

### Goal Task Network (GTN) Planning

It is easy to have both goal methods and task methods in the same planning domain. Any method, regardless of whether it is a task method or goal method, can return a list that contains actions, subtasks, and subgoals. For example, in the `m_move_to_loc2` multigoal-method defined earlier, we could replace the last line with

    return [('move_container', c, mg.loc[c]) for c in containers_to_move]

where `move_container` is a task for which we have declared one or more task methods. 

### Checking whether a method has achieved a goal

If *g* is a goal and *m* is a method that has been declared to be relevant for *g*, then *g* should be true upon completion of *m*. By default, when *m* finishes, GTPyhop will check whether *g* is true, and will backtrack if *g* is false.

To perform this check, GTPyhop inserts into the agenda, immediately after the subtasks generated by *m*, a special "verification" task for which GTPyhop provides a built-in method. If *g* is satisfied, then the method returns an empty subtask list, hence puts nothing into the plan. If *g* is not satisfied, the method signals an error.

An obvious question is whether such checks are useful. They may be useful while developing and debugging a domain, but the proliferation of verification tasks in the agenda adds overhead and interferes with readability of GTPyhop's debugging printout. Thus one may prefer to turn them off -- which can be done by putting the following into the domain definition or at the beginning of a planning problem:

    verify_goals = False 

Depending on feedback from users, I'll consider whether to make `verify_goals = False` the default.


## <span id="Pyhop">6. Backward Compatibility with Pyhop</span>


GTPyhop is mostly backward-compatible with Pyhop, but not completely so. Below is a list of the differences. To illustrate them, the [`pyhop_simple_travel_example`](Examples/pyhop_simple_travel_example) example domain is a near-verbatim adaptation of Pyhop's [simple travel example](https://bitbucket.org/dananau/pyhop/src/master/simple_travel_example.py).

- Pyhop worked in both Python 2 and 3. GTPyhop requires Python 3.
- GTPyhop requires a domain declaration before any actions and methods can be defined.
- In Pyhop, `verbose` was a keyword argument having the default value 0. In GTPyhop, it is a global variable and its initial value is 1. 
- GTPyhop uses different names for the following functions. For backward compatibility, you can still use the old Pyhop function names, but a message will ask you to use the new names in the future.

    |     Pyhop |     GTPyhop |
     --- | --- 
    `pyhop.declare_methods` | `gtpyhop.declare_task_methods`*
    `pyhop.declare_operators` | `gtpyhop.declare_actions`
    `pyhop.print_operators` | `gtpyhop.print_actions`
    `pyhop.pyhop` | `gtpyhop.find_plan`
     
    \* There is a minor difference between these two functions. In Pyhop, if `'task1'` is a task name and you call `pyhop.declare_methods('task1', …)` more than once, the only methods for `task1` will be the ones in the last call. In GTPyhop, you can call `gtpyhop.declare_task_methods('task1', …)` more than once to add additional methods for `task1`.  


## <span id="Comparisons">7. Comparisons with other planners</span>

### <span id="GDP">7.1. GDP and GoDel</span>

In HGN planners such as GDP [[Shi12](#Shi12)] and GoDel [[Shi13](#Shi13)], an action *a* may be applied to a goal if the current state satisfies *a*'s preconditions, *a* has an effect that matches the goal, and none of *a*'s effects negate the goal. In contrast, GTPyhop does not apply actions directly to goals. GTPyhop will not put an action into the plan unless the action is in the agenda, either because it was there initially or because a method put it there.

To see why, let us rewrite the `unload` action in classical precondition-and-effects notation [[Gha16](#Gha16)]:

    unload(robot, container, location):
        precond: loc[robot] = location, loc[container] = robot
        effects: loc[container] = location, cargo[robot] = 'nil'

GDP and GoDel would consider such an action to be relevant for both of the following goals:

 - goal 1: reach a state `s` in which `loc[container] = location`;
 - goal 2: reach a state `s` in which `cargo[robot] = 'nil'`.

That isn't feasible in GTPyhop, because the preconditions and effects of a GTPyhop action are not fixed in advance, but instead are computed using arbitrary Python code. The only way to tell what effects an action will have is to execute the code and see what state it produces. To find an action that is applicable in a state *s* and whose effects satisfy a goal *g*, we would need to do a backtracking search through many combinations of actions and parameter values, trying each one to see if executing it in *s* will produce a state that satisfies *g*. This would be unacceptably expensive. Thus when trying to accomplish a goal, GTPyhop doesn't look at actions, it only looks at goal methods.

In GTPyhop, one can still use actions to accomplish goals, with much less computational expense, by writing a small number of methods: one method for each of the action's effects. For example, suppose we have the following GTPyhop action for unloading a container from a robot at a particular location:

    def unload(state, robot, container, location):
        if state.loc[container] == robot and state.loc[robot] == location:
            state.loc[container] = location
            state.cargo[robot] = 'nil'
            return state

    gtpyhop.declare_actions(unload)

Then we can write the following two methods:

- A goal-method `m_unload_at_loc` that we declare relevant for goal 1.  If `container` is currently on a robot whose location is `location`, then this method will return the desired `unload` action:

        def m_unload_at_loc(state, container, location):
            r = state.loc[container]
            # 'is_a' needs to be a function that returns an object's type
            if is_a(r, 'robot') and state.loc[r] == location:
                return [('unload', r, container, location)]

        gtpyhop.declare_unigoal_methods('loc', m_unload_at_loc)

    The `declare_unigoal_methods` declaration makes `m_unload_at_loc` relevant for `('loc', container, location)`, which is goal 1 in GTPyhop notation.
    
- A goal-method `m_unload_cargo` that we declare relevant for goal 2. If the desired cargo is `'nil'` (i.e., empty) and the robot's current cargo isn't `'nil'`, then this method will return the desired `unload` action:

        def m_unload_cargo(state, robot, desired_cargo):
            c = state.cargo[robot]
            if desired_cargo == 'nil' and c != 'nil':
                return [('unload', robot, c, state.loc[robot])]

        gtpyhop.declare_unigoal_methods('cargo', m_unload_cargo)

    The `declare_unigoal_methods` declaration makes `m_unload_cargo` relevant for `('cargo', robot, desired_cargo)`, which is goal 2 in GTPyhop notation.
    
If a domain definition includes such methods for all of the actions, then GTPyhop will behave similarly to GDP -- though not identically, since GTPyhop won't have access to the heuristic function that GDP uses to guide its search.



### <span id="HGNpyhop">7.2. HGNPyhop</span>

There is a fork of Pyhop called [HGNpyhop](https://github.com/ospur/hgn-pyhop) in which one may declare an action to be directly relevant for a goal. This seems like a nice feature, and I seriously considered adding it to GTPyhop -- but I ultimately decided against it, because it creates unfortunate restrictions on how the actions can be used.

In HGNPyhop, to declare an action relevant for a goal of the form `(variable, arg, value)`, the action must be callable as `action_name(arg,value)`. Consider what this means for goals 1 and 2 in the previous section:

 - To make `unload` relevant for goal 1, `('loc', container, location)`, we would need to rewrite it to be callable as `unload(state,container,location)`, and declare it relevant for `loc`. The rewrite would look like this:

        def unload(state, container, location):
            r = state.loc[container]
            # 'is_a' needs to be a function that returns an object's type
            if is_a(r,'robot') and state.loc[r] == location:
                state.loc[container] = location
                state.cargo[r] = 'nil'
                return state

        hgn_pyhop.declare_operators('loc', unload)

 - To make `unload` relevant for goal 2, `('cargo', robot, desired_cargo)`, we would need to rewrite it to be callable as `unload(robot, desired_cargo)`, and declare it relevant for `cargo`. The rewrite would look like this:

        def unload(state, robot, desired_cargo):
            c = state.cargo[robot]
            if desired_cargo == 'nil' and c != 'nil':
                state.loc[c] = state.loc[robot]
                state.cargo[robot] = 'nil'
                return state

        hgn_pyhop.declare_operators('cargo', unload)
 
Both rewrites make the `unload` action harder to understand -- and neither of them makes it relevant for *both* goals. To accomplish that in HGNpyhop, I think something like the following *might* work, though I haven't tested it to make sure:

    def unload(state, arg1, arg2):
        if is_a(arg1,'container') and is_a(arg2,'loc'):
            r = state.loc[arg1]
            if is_a(r,'robot') and state.loc[r] == arg2:
                state.loc[arg1]=arg2
                state.cargo[r]=nil
        elif is_a(arg1,'robot') and arg2 == 'nil':
            c = state.cargo[arg1]
            if desired_cargo == 'nil' and c != 'nil':
                state.loc[c] = state.loc[arg1]
                state.cargo[arg1] = 'nil'
        else:
            state = False
        return state

    hgn_pyhop.declare_operators('loc', unload)
    hgn_pyhop.declare_operators('cargo', unload)

This definition is much harder to understand than the original one. Furthermore, one can construct examples of other actions and goals for which an `is_a` test on the arguments would not be sufficient to tell which piece of code to execute. 

To summarize: it can be difficult to tell HGNpyhop that an action *a* is relevant for achieving a particular one of its effects, and even more difficult to tell HGNpyhop that *a* also is relevant for achieving its other effects. Without a way to do this, if those effects are goals that we want to achieve, HGNpyhop won't be able to use *a* to achieve them.

In GTPyhop, we can overcome this problem by defining, for each effect *e* of *a*, a unigoal_method for *e* that returns the list [*a*]. This is possible because GTPyhop allows actions to appear in the list of items returned by a method -- which is not allowed in HGNpyhop, nor in HGN planners such as GDP and GoDel.

As an example of how to do this, see [Examples/logistics_hgn.py](Examples/logistics_hgn.py)


## <span id="References">8. References</span>

<!--
<span id="Alf16">[Alf16]</span> R. Alford, V. Shivashankar, M. Roberts, J. Frank, and D.W. Aha.
[Hierarchical planning: relating task and goal decomposition with task sharing](https://www.ijcai.org/Abstract/16/429). 
In *IJCAI*, 2016, pp. 3022–3028.
-->

<span id="Gha16">[Gha16]</span> M. Ghallab, D. S. Nau, and P. Traverso. [*Automated Planning and Acting*](http://www.laas.fr/planning). Cambridge University Press, Sept. 2016.

<span id="Nau21">[Nau21]</span> D. Nau, S. Patra, M. Roberts, Y. Bansod and R. Li. [GTPyhop: A Hierarchical Goal+Task Planner Implemented in Python](http://www.cs.umd.edu/users/nau/papers/Nau21gtpyhop.pdf). ICAPS HPlan Workshop, 2021. 

<span id="Shi12">[Shi12]</span> V. Shivashankar, U. Kuter, D. S. Nau, and R. Alford. [A hierarchical goal-based formalism and algorithm for single-agent planning](https://www.cs.umd.edu/~nau/papers/shivashankar2012hierarchical.pdf). In *Proc. International Conference on Autonomous Agents and Multiagent Systems (AAMAS)*, 2012.

<span id="Shi13">[Shi13]</span> V. Shivashankar, R. Alford, U. Kuter, and D. Nau. [The GoDeL planning system: A more perfect union of domain-independent and hierarchical planning](https://www.cs.umd.edu/~nau/papers/shivashankar2013godel.pdf). In Proc. International Joint Conference on Artificial Intelligence (IJCAI), pp. 2380–2386, 2013.
