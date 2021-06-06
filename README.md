# GTPyhop

Dana Nau, University of Maryland

June 3, 2021

## Summary

GTPyhop is a task-planning system based on [Pyhop](https://bitbucket.org/dananau/pyhop/), but generalized to plan for both tasks and goals. It does task planning in the same way as Pyhop, and it is mostly backward-compatible with Pyhop (as discussed later in this document). The way GTPyhop plans for goals is similar to GDP [2].

More specifically, a GTPyhop planning problem is specified by an *agenda* that is a list of tasks, actions, and goals. This generalizes Pyhop's *task list*, which contains tasks and actions but no goals. Like Pyhop, GTPyhop constructs a solution plan by planning for the agenda items one by one, going left-to-right. For each action in the agenda, GTPyhop applies it to update the current state, and appends it to the solution plan. For each task or goal in the agenda, GTPyhop chooses an applicable method, and the method returns a (possibly empty) list of tasks, actions, and goals to insert into the agenda.  If an  agenda item is an inapplicable action, or a goal or task has no applicable methods, then GTPyhop backtracks so it can choose different methods for earlier agenda items.

GTPyhop also includes:

  - A `Domain` class to contain a planning domain's actions, commands, tasks, goals, and methods. This makes it possible to import multiple planning-and-acting domains during a single GTPyhop session, without them interfering with each other.
  
  - An implementation of the Run-Lazy-Lookahead actor [3], a way to declare commands that the actor can perform, and several examples of integrated planning and acting using Run-Lazy-Lookahead and GTPyhop.
  
  - A simple test harness to facilitate displaying examples and debugging.

For some details about GTPyhop's HGN planning, see [Remarks about HGN Planning in GTPyhop](Remarks_about_HGN_planning_in_GTPyhop.md).

## Example problem domains

Launch Python 3, and try one or more of the following:

    import Examples.simple_goals
    import Examples.simple_tasks
    import Examples.simple_tasks_with_error
    import Examples.backtracking_tasks
    import Examples.blocks_tasks
    import Examples.blocks_goals
    import Examples.blocks_goal_splitting
    import Examples.pyhop_simple_travel_example



## Adapting Pyhop planning domains for use with GTPyhop

GTPyhop is mostly backward-compatible with Pyhop, but not completely so. Below is a list of the differences. To illustrate them, the last example above is a near-verbatim adaptation of Pyhop's [simple travel example](https://bitbucket.org/dananau/pyhop/src/master/simple_travel_example.py).

- Pyhop worked in both Python 2 and 3. GTPyhop requires Python 3.
- In Pyhop, `verbose` was a keyword argument having the default value 0. In GTPyhop, it is a global variable and its initial value is 1. 
- GTPyhop uses different names for the following functions. For backward compatibility, you can use the old Pyhop function names to call the new GTPyhop functions, but you'll get a message asking you to start using the new name instead.

    |Pyhop function | GTPyhop function or method|
     --- | --- 
    `pyhop.declare_methods` | `gtpyhop.declare_task_methods`*
    `pyhop.declare_operators` | `gtpyhop.declare_actions`
    `pyhop.print_operators` | `gtpyhop.print_actions`
    `pyhop.pyhop` | `gtpyhop.find_plan`
     
    \* In GTPyhop, you can call `gtpyhop.declare_task_methods` more than once for the same taskname, to add additional methods to the ones declared earlier.  In Pyhop, calling `declare_methods` more than once for the same taskname would keep only the methods declared in the last call.


## References

[1] D. Nau. [Game Applications of HTN Planning with State Variables](http://www.cs.umd.edu/~nau/papers/nau2013game.pdf). In *ICAPS Workshop on Planning in Games*, 2013. Keynote talk.

[2] V. Shivashankar, U. Kuter, D. S. Nau, and R. Alford. [A hierarchical goal-based formalism and algorithm for single-agent planning](https://www.cs.umd.edu/~nau/papers/shivashankar2012hierarchical.pdf). In *Proc. International Conference on Autonomous Agents and Multiagent Systems (AAMAS)*, 2012.

[3] M. Ghallab, D. S. Nau, and P. Traverso. [*Automated Planning and Acting*](http://www.laas.fr/planning). Cambridge University Press, Sept. 2016.