# Remarks about HGN planning in GTPyhop

> Dana Nau  
> University of Maryland  
> June 3, 2021


### Contents:
 - [Comparison with GDP](#GDP)
 - [Comparison with HGNpyhop](#HGNpyhop)
 - [GTPyhop goals, tasks, and methods](#Goals)
 - [Checking whether a method has achieved a goal](#Checking)
 - [References](#References)

## <span id="GDP">Comparison with GDP</span>

In HGN planners such as GDP [1] and GoDel [2], an action may be applied to a goal if the current state satisfies all of the action's preconditions, at least one of its effects matches a goal, and none of its effects negates any of the goals. In contrast, GTPyhop does not apply actions directly to goals. GTPyhop will not put an action into the plan unless the action is in the agenda, either because it was there initially or because a method put it there.

For example, consider a classical action (written in state-variable notation [3]) for unloading a container from a robot at a particular location:

        unload(robot, container, location):
            precond: loc[robot] = location, loc[container] = robot
            effects: loc[container] = location, cargo[robot] = 'nil'

GDP and GoDel would consider such an action to be relevant for both of the following goals:

> goal 1: reach a state `s` in which `loc[container] = location`;  \
> goal 2: reach a state `s` in which `cargo[robot] = 'nil'`.

That isn't feasible in GTPyhop, because the preconditions and effects of a GTPyhop action are not fixed in advance, but instead are computed using arbitrary Python code. The only way to tell what effects an action will have is to execute the code and see what state it produces. To find an action that is applicable in a state *s* and whose effects satisfy a goal *g*, we would need to do a backtracking search through many combinations of actions and parameter values, trying each one to see if executing it in *s* will produce a state that satisfies *g*. This would be unacceptably expensive. Thus when trying to accomplish a goal, GTPyhop doesn't look at actions, it only looks at goal methods.

In GTPyhop, one can still use actions to accomplish goals, with much less computational expense, by writing a small number of methods: one method for each of the action's effects. For example, suppose we have the following GTPyhop action for unloading a container from a robot at a particular location:

        def unload(state, robot, container, location):
            if state.loc[container] == robot and state.loc[robot] == location:
                state.loc[container] = location
                state.cargo[robot] = 'nil'
                return state

        gtpyhop.declare_actions(unload)

Then we can write the following two methods:

- A method `m_unload_at_loc` that we declare relevant for goal 1, which is `('loc', container, location)` in GTPyhop notation.  If `container` is currently on a robot whose location is `location`, then this method will use `unload` to unload the container:

        def m_unload_at_loc(state, container, location):
            r = state.loc[container]
            if is_a(r, 'robot') and state.loc[r] == location:
                return [('unload', r, container, location)]

        gtpyhop.declare_unigoal_methods('loc', m_unload_at_loc)

    The above code requires a helper function `is_a` that tells what an object's type is.
    
- A method `m_unload_cargo` that we declare relevant for goal 2, which is `('cargo', robot, desired_cargo)` in GTPyhop notation. If the desired cargo is `nil` (i.e., empty) and the robot's cargo is non-`nil` in the current state, then this method will use `unload` to unload the cargo:

        def m_unload_cargo(state, robot, desired_cargo):
            c = state.cargo[robot]
            if desired_cargo == 'nil' and c != 'nil':
                return [('unload', robot, c, state.loc[robot])]

        gtpyhop.declare_unigoal_methods('cargo', m_unload_cargo)

If a domain definition includes such methods for all of the actions, then GTPyhop will behave similarly to GDP -- though not identically, since GTPyhop won't have access to the heuristic function that GDP uses to guide its search.


## <span id="HGNpyhop">Comparison with HGNPyhop</span>

There is a fork of Pyhop called [HGNpyhop](https://github.com/ospur/hgn-pyhop),
in which one may declare an action to be directly relevant for a goal. At first glance, this seems like a desirable feature, and I seriously considered adding it to GTPyhop -- but I ultimately decided against it, for the following reason.

To make an action relevant for a goal of the form `(variable, arg, value)`, [HGNpyhop](https://github.com/ospur/hgn-pyhop) requires the action to be callable as `action_name(arg,value)`. Consider the following two cases:

 - To make the `unload` action relevant for `('loc', container, location)`, we would need to rewrite it to be callable as `unload(state,container,location)`, and declare it relevant for `loc`. The rewrite would need to look like the following, where `is_a` would be a helper function for determining an object's type:

        def unload(state, container, location):
            r = state.loc[container]
            if is_a(r,'robot') and state.loc[r] == location:
                state.loc[container] = location
                state.cargo[r] = 'nil'
                return state

        hgn_pyhop.declare_operators('loc', unload)

 - In contrast, to make `unload` relevant for `('cargo', robot, desired_cargo)`, we would need to rewrite it to be callable as `unload(robot, desired_cargo)`, and declare it relevant for `cargo`. The rewrite would need to look like this:

        def unload(state, robot, desired_cargo):
            c = state.cargo[robot]
            if desired_cargo == 'nil' and c != 'nil':
                state.loc[c] = state.loc[robot]
                state.cargo[robot] = 'nil'
                return state

        hgn_pyhop.declare_operators('cargo', unload)
 
Both rewrites make the `unload` action harder to understand, and neither of them satisfies the requirement that in HGN planning algorithms such as GDP and Godel, `unload` must be relevant for *both* goals. To accomplish this in HGNpyhop, I think something like the following might work, though I haven't tested it to make sure:

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

Such a definition of the `unload` action is quite unintuitive. Furthermore, one can construct examples of other actions and goals, for which an `is_a` test on the arguments would not be sufficient to tell which piece of code to execute. I would not want to incorporate something like this into GTPyhop.


## <span id="Goals">Goals, tasks, and methods in GTPyhop</span>

GTPyhop has two types of goals: *unigoals* (individual goals, as in the earlier examples) and *multigoals* (conjunctions of individual goals). Below we describe each kind of goal and what its methods are like, and briefly compare them with GTPyhop's tasks.

**Unigoals:** 

A unigoal is a 3-tuple `(state_variable_name, arg, value)` that specifies a desired value for a state variable. For example, the unigoal

        ('loc', 'c1', 'loc2') 

represents the goal of reaching a state `s` such that `s.loc['c1'] = 'loc2'`. In the `m_unload_at_loc` example earlier, the declaration

        gtpyhop.declare_unigoal_methods('loc', m_unload_at_loc)

tells Pyhop that `m_unload_at_loc` is relevant for not only `('loc', 'c1', 'loc2')`, but *any* unigoal of the form `('loc',` *arg*, *value*). That is probably more general than what we want. To ensure that GTPyhop will use the method only when *arg* is a container and *value* is a location, we can rewrite to include an `if` test like this:

        def m_unload_at_loc(state, container, location):
            if is_a(container, 'container') and is_a(location, 'location'):
                r = state.loc[container]
                if is_a(r, 'robot') and state.loc[r] == location:
                    return [('unload', r, container, location)]

        gtpyhop.declare_unigoal_methods('loc', m_unload_at_loc)

**Multigoals:** 

Syntactically, a multigoal looks similar to a state -- but unlike a state, it specifies desired (rather than current) values for some (rather than all) of the state variables. For example, this:

        g = Multigoal('goal1', loc={})
        g.loc['c1'] = 'loc2'
        g.loc['container3'] = 'loc2'

says we want to reach any state `s` such that `s.loc['c1'] = 'loc2'` and `s.loc['container3'] = 'location4'`. Here is a multigoal method that might be useful for `goal1`:

        def m_move_to_loc2(state,mg):
            containers_to_move = [c for c in mg.loc if \
                    is_a(c,'container') and s.loc != 'loc2']
            # for this to work, we'll need to define a 'distance' function:
            containers_to_move.sort(key = lambda x: distance(loc[x],'loc2'))
            return [('loc', c, mg.loc[c]) for c in containers_to_move]

        gtpyhop.declare_multigoal_methods(m_unload_at_loc)

The method takes two arguments: the current state and the multigoal.  It returns a list of unigoals, one for each container that needs to be moved to `loc2`. The containers are sorted in order of their distance from `loc2`, so that the closest ones will be moved first. 

The `declare_multigoal_methods` declaration says that `m_move_to_loc2` is relevant not only for `goal1`, but for all multigoals. If you want GTPyhop to use the method only for certain kinds of multigoals, the body of the method will need to include some `if` tests to exclude the others, e.g., like this:

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

**Tasks:** 

In GTPyhop, as in Pyhop, a task is written as a tuple

        (task_name, arg1, arg2, ..., argn)

that specifies an activity to perform. Except for the indefinite number of arguments, this looks syntactically similar to a goal. The way we tell GTPyhop that it is a task, rather than a goal, is by declaring task methods for it. For example, this:

        def m_unload_container(state, container, location):
            if is_a(container, 'container') and is_a(location, 'location'):
                r = state.loc[container]
                if is_a(r, 'robot') and state.loc[r] == location:
                    return [('unload', r, container, location)]

        gtpyhop.declare_task_methods('unload_container', m_unload_container)

tells GTPyhop to consider using `m_unload_container` for any task of the form

        ('unload_container' container location)

Notice that the definition of `m_unload_container` looks nearly identical to the `m_unload_at_loc` method defined earlier, except for the `declare_task_methods` declaration. In this simple example, it doesn't make much difference whether we use a task or a unigoal, but there are various situations where each of them may be more preferable than the other.

It is easy to have both goal methods and task methods in the same planning domain. For example, in the `m_move_to_loc2` multigoal-method defined earlier, we could replace the last line with

                return [('move_container', c, mg.loc[c]) for c in containers_to_move]

where `move_container` is a task for which we have declared one or more task methods.

## <span id="Checking">Checking whether a method has achieved a goal</span>

If *g* is a goal and *m* is a method that has been declared to be relevant for *g*, then *g* should be true upon completion of *m*. By default, when *m* finishes, GTPyhop will check whether *g* is true, and will backtrack if *g* is false.

To perform this check, GTPyhop inserts into the agenda, immediately after the subtasks generated by *m*, a special "verification" task for which GTPyhop provides a built-in method. If *g* is satisfied, then the method returns an empty subtask list, hence puts nothing into the plan. If *g* is not satisfied, the method signals an error.

An obvious question is whether such checks are useful. They may be useful while developing and debugging a domain, but the proliferation of verification tasks in the agenda adds overhead and interferes with readability of GTPyhop's debugging printout. Thus one may prefer to turn them off -- which can be done by putting the following into the domain definition or at the beginning of a planning problem:

        verify_goals = False 

Depending on feedback from users, I'll consider whether to make `verify_goals = False` the default.

---------

## <span id="References">References</span>

[1] V. Shivashankar, U. Kuter, D. S. Nau, and R. Alford. [A hierarchical goal-based formalism and algorithm for single-agent planning](https://www.cs.umd.edu/~nau/papers/shivashankar2012hierarchical.pdf). In Proc. International Conference on Autonomous Agents and Multiagent Systems (AAMAS), 2012.

[2] V. Shivashankar, R. Alford, U. Kuter, and D. Nau. [The GoDeL planning system: A more perfect union of domain-independent and hierarchical planning](https://www.cs.umd.edu/~nau/papers/shivashankar2013godel.pdf). In Proc. International Joint Conference on Artificial Intelligence (IJCAI), pp. 2380–2386, 2013.

[3] M. Ghallab, D. S. Nau, and P. Traverso. [*Automated Planning and Acting*](http://www.laas.fr/planning). Cambridge University Press, Sept. 2016.