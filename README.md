# GTPyhop
## A Goal-Task-Network planning system written in Python

> **Dana S. Nau**  
> University of Maryland  
> July 14, 2021


GTPyhop is an automated planning system to plan for both tasks and goals. It plans for tasks in the same way as the [Pyhop](https://bitbucket.org/dananau/pyhop/) planner [[Nau13](#Nau13)], and it is mostly backward-compatible with Pyhop. The way it plans for goals is based on the GDP algorithm [[Shi12](#Shi12)].

### How GTPyhop works

A GTPyhop planning problem is specified by a *todo list*, a sequence of tasks, actions, and goals. GTPyhop constructs a solution plan π by planning for these items one by one, in the order that they occur in the list. Here are the possibilities for each item:

  - If it is an applicable action, GTPyhop appends the action to π, and executes the action to update the current state.
  - If it is a task, GTPyhop looks through the list of relevant task methods, and executes the first one that is applicable in the current state. This produces a (possibly empty) list of tasks, actions, and goals. GTPyhop inserts them into the todo list.
  - If it is a goal, GTPyhop looks through the list of relevant goal methods, and executes the first one that is applicable in the current state. This produces a (possibly empty) list of tasks, actions, and goals. GTPyhop inserts them into the todo list, along with a way to check whether they actually achieve the goal.
  - Whenever one of the above steps fails (e.g., an action is inapplicable, a goal or task has no applicable methods, or a goal method doesn't achieve its goal), GTPyhop backtracks to choose a different method for an earlier task or goal in the todo list.

GTPyhop also provides a `Domain` class to contain the actions, tasks, goals, and methods for a problem domain. This makes it possible to use multiple problem domains during a single Python session, without them interfering with each other.

### Other things in the GTPyhop distribution
  
  - A simple acting algorithm called Run-Lazy-Lookahead [[Gha16](#Gha16)], and several examples of integrated planning and acting using Run-Lazy-Lookahead and GTPyhop.
  
  - A simple test harness that's useful for debugging and demonstrating problem domains.
  
  - Several example problem domains. Go to the `Examples` directory, launch Python 3, and try one or more of the following:

        import simple_hgn                   # some simple goal-planning examples
        import simple_htn                   # some simple task-planning examples
        import simple_htn_acting_error      # demonstration of an acting-time problem
        import backtracking_htn             # simple demonstration of backtracking
        import blocks_gtn                   # goal-task-planning version of the blocks world
        import blocks_htn                   # task-planning version of the blocks world
        import blocks_hgn                   # goal-planning version of the blocks world
        import blocks_goal_splitting        # separating goals and solving them sequentially
        import logistics_hgn                # adaptation of the "logistics" domain
        import pyhop_simple_travel_example  # a near-verbatim adaptation of a Pyhop example

### Further reading

  - The best overall description of GTPyhop is [[Nau21](#Nau21)].
  - [Some Remarks about GTPyhop](some_remarks.md) discusses some details of GTPyhop's operation, compares it to some other planners, and discusses backward-compatibility with Pyhop.
  - GTPyhop does a totally-ordered version of Goal-Task-Network (GTN) planning without sharing and task insertion. For definitions of those terms and their theoretical properties, see [[Alf16](#Alf16)].
  - [[Ban21](#Ban21)] describes a re-entrant version of GTPyhop that has some advantages for integrating acting and planning.
  

### References

<span id="Alf16">[Alf16]</span> R. Alford, V. Shivashankar, M. Roberts, J. Frank, and D.W. Aha.
[Hierarchical planning: relating task and goal decomposition with task sharing](https://www.ijcai.org/Abstract/16/429). 
In *IJCAI*, 2016, pp. 3022–3028.

<span id="Ban21">[Ban21]</span> Y. Bansod, D.S. Nau, S. Patra and M. Roberts.
Integrating Planning and Acting by Using a Re-Entrant HTN Planner. 
In *ICAPS Workshop on Hierarchical Planning (HPlan)*, 2021, to appear.

<span id="Gha16">[Gha16]</span> M. Ghallab, D.S. Nau, and P. Traverso.
[*Automated Planning and Acting*](http://www.laas.fr/planning). 
Cambridge University Press, Sept. 2016.

<span id="Nau13">[Nau13]</span> D.S. Nau. [Game Applications of HTN Planning with State Variables](http://www.cs.umd.edu/~nau/papers/nau2013game.pdf). 
In *ICAPS Workshop on Planning in Games*, 2013. Invited talk.

<span id="Nau21">[Nau21]</span> D.S. Nau, S. Patra, M. Roberts, Y. Bansod and R. Li.
GTPyhop: A Hierarchical Goal+Task Planner Implemented in Python.
In *ICAPS Workshop on Hierarchical Planning (HPlan)*, 2021, to appear.

<span id="Shi12">[Shi12]</span> V. Shivashankar, U. Kuter, D.S. Nau, and R. Alford.
[A hierarchical goal-based formalism and algorithm for single-agent planning](https://www.cs.umd.edu/~nau/papers/shivashankar2012hierarchical.pdf). 
In *Proc. International Conference on Autonomous Agents and Multiagent Systems (AAMAS)*, 2012.
