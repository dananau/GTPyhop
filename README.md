# GTPyhop
## A Goal-Task-Network planning system written in Python

> **Dana S. Nau**  
> University of Maryland  
> July 6, 2021  


GTPyhop is an automated planning system that extends the [Pyhop](https://bitbucket.org/dananau/pyhop/) planner to plan for both tasks and goals. GTPyhop plans for tasks in the same way as Pyhop [[Nau13](#Nau13)], and is mostly backward-compatible with Pyhop. The way it plans for goals is based on the GDP algorithm [[Shi12](#Shi12)].

A GTPyhop planning problem is specified by a *todo list* that contains tasks, actions, and goals. To construct a solution plan, GTPyhop goes one by one through the items in the todo list. Here are the possibilities for each item:

  - If it is an applicable action, GTPyhop applies it to update the current state, and appends it to the solution plan.
  - If it is a task, GTPyhop looks through the list of relevant tasks methods, and applies the first one that is applicable. This produces a (possibly empty) list of tasks, actions, and goals that GTPyhop inserts into the todo list.
  - If it is a goal *g*, GTPyhop looks through the list of relevant goal methods, and applies the first one that is applicable. This produces a (possibly empty) list of tasks, actions, and goals that GTPyhop inserts into the todo list, along with a way to check whether they actually achieve *g*.
  - If a failure occurs (e.g., the action is inapplicable, or a goal or task that has no applicable methods, or a goal method doesn't achieve its goal), GTPyhop backtracks to choose different methods for earlier tasks and goals in the todo list.

GTPyhop also includes:

  - A `Domain` class to contain the actions, commands, tasks, goals, and methods for a planning and acting domain. This makes it possible to import multiple domains during a single Python run, without them interfering with each other.
  
  - An implementation of a simple acting algorithm called Run-Lazy-Lookahead [[Gha16](#Gha16)], a way to declare commands for the actor to perform, and several examples of integrated planning and acting using Run-Lazy-Lookahead and GTPyhop.
  
  - A simple test harness that's useful for running and debugging examples.
  
  - Several example planning and acting domains (see below).

### Further reading

  - The best overall description of GTPyhop is [[Nau21](#Nau21)].
  - [Some GTPyhop Details](Some_GTPyhop_Details.md) discusses some details of GTPyhop's operation, compares it to some other planners, and discusses backward-compatibility with Pyhop.
  - GTPyhop does a totally-ordered version of Goal-Task-Network (GTN) planning without sharing and task insertion. For precise definitions of those terms and their theoretical properties, see [[Alf16](#Alf16)].

### Example problem domains

Launch Python 3, and try one or more of the following:

    import Examples.simple_goals
    import Examples.simple_tasks
    import Examples.simple_tasks_with_error
    import Examples.backtracking_tasks
    import Examples.blocks_hybrid
    import Examples.blocks_tasks
    import Examples.blocks_goals
    import Examples.blocks_goal_splitting
    import Examples.logistics_goals
    import Examples.pyhop_simple_travel_example




### References

<span id="Alf16">[Alf16]</span> R. Alford, V. Shivashankar, M. Roberts, J. Frank, and D.W. Aha. [Hierarchical planning: relating task and goal decomposition with task sharing](https://www.ijcai.org/Abstract/16/429). In IJCAI, 2016, pp. 3022–3028.

<span id="Gha16">[Gha16]</span> M. Ghallab, D. S. Nau, and P. Traverso. [*Automated Planning and Acting*](http://www.laas.fr/planning). Cambridge University Press, Sept. 2016.

<span id="Nau13">[Nau13]</span> D. Nau. [Game Applications of HTN Planning with State Variables](http://www.cs.umd.edu/~nau/papers/Nau13game.pdf). In *ICAPS Workshop on Planning in Games*, 2013. Invited talk.

<span id="Nau21">[Nau21]</span> D. Nau, S. Patra, M. Roberts, Y. Bansod and R. Li. [GTPyhop: A Hierarchical Goal+Task Planner Implemented in Python](http://www.cs.umd.edu/users/nau/papers/Nau21gtpyhop.pdf). ICAPS HPlan Workshop, 2021. 

<span id="Shi12">[Shi12]</span> V. Shivashankar, U. Kuter, D. S. Nau, and R. Alford. [A hierarchical goal-based formalism and algorithm for single-agent planning](https://www.cs.umd.edu/~nau/papers/shivashankar2012hierarchical.pdf). In *Proc. International Conference on Autonomous Agents and Multiagent Systems (AAMAS)*, 2012.
