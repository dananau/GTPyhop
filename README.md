# GTPyhop
## A Goal-Task-Network planning system written in Python

> **Dana S. Nau**  
> University of Maryland  
> July 22, 2021


GTPyhop is an automated planning system written in Python, that uses hierarchical planning techniques to construct plans of action for tasks and goals. GTPyhop plans for tasks in the same way as the [Pyhop](https://bitbucket.org/dananau/pyhop/) planner, and it is mostly backward-compatible with Pyhop. The way GTPyhop plans for goals is based on the [GDP](https://www.cs.umd.edu/~nau/papers/shivashankar2012hierarchical.pdf) algorithm.

### Features

Below is a brief summary of GTPyhop's main features. For more information, see
[this overview of GTPyhop](http://www.cs.umd.edu/~nau/papers/nau2021gtpyhop.pdf), and [these additional remarks](some_remarks.md).

- GTPyhop creates a *plan* (a sequence of actions) to accomplish a *to-do* list *T* consisting of actions, tasks, and goals. The objective is to construct a *solution plan*, i.e., a sequence of actions that accomplishes all of the items in *T*, in the order that they occur in *T*.  To do this, GTPyhop does a backtracking search in a *planning domain* that includes definitions of the actions, *task methods* that return todo-lists for accomplishing tasks, and *goal methods* that return to-do lists for achieving goals.

- Since it may contain both tasks and actions, the to-do list *T* generalizes both Pyhop’s task list and GDP’s goal list. The same is true for the to-do lists returned by GTPyhop's task methods and goal methods.

- GTPyhop is mostly backward-compatible with Pyhop. However, GTPyhop also includes more documentation than Pyhop, additional debugging features, and the ability to load multiple planning domains into memory and switch among them without having to restart Python each time.




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

  - The [additional remarks](some_remarks.md) document mentioned earlier. It include some details about states, actions, and methods, a discussion of backward-compatibility with Pyhop, and comparisons to other planners.
  

### Miscellany
    
[//]: # "[This paper](#Ban21) describes a re-entrant version of GTPyhop that has some advantages for integrating acting and planning (e.g., it overcomes the problem demonstrated in the `simple_htn_acting_error` file above."
  
- [Here is a paper](https://www.ijcai.org/Abstract/16/429) that classifies various kinds of hierarchical planning. In their terminology, GTPyhop's search strategy is a totally-ordered version of Goal-Task-Network (GTN) planning without sharing and task insertion.
  
