# GTPyhop
## A Goal-Task-Network planning system written in Python

> **Dana S. Nau**  
> University of Maryland  
> July 14, 2021


GTPyhop is an automated planning system that extends the 
[Pyhop](https://bitbucket.org/dananau/pyhop/) HTN planner to do hierarchical planning for both tasks and goals. It plans for tasks the same way that Pyhop does, and it is mostly backward-compatible with Pyhop. The way it plans for goals is based on the [GDP algorithm](https://www.cs.umd.edu/~nau/papers/shivashankar2012hierarchical.pdf).

### How GTPyhop works

The best overview of GTPyhop is [the published paper about it](http://www.cs.umd.edu/~nau/papers/nau2021gtpyhop.pdf), but here's a brief summary of how it works.

GTPyhop plans for a *to-do* list consisting of actions, tasks, and goals. It does this in a *planning domain* that includes definitions of actions, tasks, goals, and methods for achieving tasks and goals. 

Given a planning domain, a current state *s* and a to-do list *T*, GTPyhop constructs a solution plan π by planning for the items in *T* one by one in sequence. Here are the possibilities for each item:

  - If the item is an applicable action, GTPyhop executes the action to update *s*, and appends it to π.
  - If the item is a task, GTPyhop looks at the relevant task methods, and executes the first one that is applicable in *s*. This produces a (possibly empty) list of tasks, actions, and goals. GTPyhop inserts them into *T* to do next.
  - If the item is a goal, GTPyhop looks at the relevant goal methods, and executes the first one that is applicable in *s*. This produces a (possibly empty) list of tasks, actions, and goals. GTPyhop inserts them into *T* to do next, along with a way to check whether they actually achieve the goal.
  - Whenever one of the above steps fails (e.g., an action is inapplicable, a goal or task has no applicable methods, or a goal method doesn't achieve its goal), GTPyhop backtracks to the last point where it chose a method for a task or goal, to try a different method if one is available.

When GTPyhop reaches the end of *T*, it returns π as the solution plan.


### Other things in the GTPyhop distribution
  
  - A version of the Run-Lazy-Lookahead algorithm (see [*Automated Planning and Acting*](http://www.laas.fr/planning)), and several examples of integrated planning and acting using Run-Lazy-Lookahead and GTPyhop.
  
  - A simple test harness that's useful for debugging and demonstrating problem domains.
  
  - Several example problem domains. Go to the `Examples` directory, launch Python 3, and try one or more of the following:

        import simple_htn                   # some simple task-planning examples
        import simple_hgn                   # some simple goal-planning examples
        import backtracking_htn             # simple demonstration of backtracking
        import logistics_hgn                # goal-planning version of the "logistics" domain
        import blocks_gtn                   # goal-task-planning version of the blocks world
        import blocks_htn                   # task-planning version of the blocks world
        import blocks_hgn                   # goal-planning version of the blocks world
        import blocks_goal_splitting        # separating goals and solving them sequentially
        import pyhop_simple_travel_example  # example of near-backward-compatibility with Pyhop
        import simple_htn_acting_error      # example of a problem at acting time

  - A document giving [additional information](additional_information.md), including comparisons to other planners and a discussion of backward-compatibility with Pyhop.

### Miscellany
    
  - [This paper](#Ban21) describes a re-entrant version of GTPyhop that has some advantages for integrating acting and planning (e.g., it overcomes the problem demonstrated in the `simple_htn_acting_error` file above.
  - [Here is a paper](https://www.ijcai.org/Abstract/16/429) that classifies various kinds of hierarchical planning. In their terminology, GTPyhop's search strategy is a totally-ordered version of Goal-Task-Network (GTN) planning without sharing and task insertion.
  
