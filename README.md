# GTPyhop
## A Goal-Task-Network planning system written in Python

> **Dana S. Nau**  
> University of Maryland  
> July 22, 2021


GTPyhop is an automated planning system written in Python, that uses hierarchical planning techniques to construct plans of action for tasks and goals.  The way GTPyhop plans for tasks is very similar to the [Pyhop](https://bitbucket.org/dananau/pyhop/) planner, and GTPyhop is mostly backward-compatible with Pyhop. The way GTPyhop plans for goals is inspired by the [GDP](https://www.cs.umd.edu/~nau/papers/shivashankar2012hierarchical.pdf) algorithm. However, GTPyhop may use both tasks and goals throughout its planning process.

Here is a brief summary of GTPyhop's features:


- GTPyhop creates a *plan* (a sequence of actions) to accomplish a *to-do* list *T* consisting of actions, tasks, and goals. The objective is to construct a *solution plan*, i.e., a sequence of actions that accomplishes all of the items in *T*, in the order that they occur in *T*.  To do this, GTPyhop does a backtracking search in a *planning domain* that includes definitions of what the actions do, *task methods* 
telling how to accomplish tasks, and *goal methods* telling how to achieve goals.

- Unlike the task lists used in Pyhop and the goal lists used in GDP, GTPyhop's to-do list may contain both tasks and goals. The same is true for the to-do lists returned by GTPyhop's task methods and goal methods. Thus GTPyhop may switch back and forth between tasks and goals throughout its planning process.

- GTPyhop is mostly backward-compatible with Pyhop. However, GTPyhop includes more documentation, more debugging features, and the ability to load multiple planning domains into memory and switch among them without having to restart Python each time.

For further information, see this [overview of GTPyhop](http://www.cs.umd.edu/~nau/papers/nau2021gtpyhop.pdf) and this [additional information](additional_information.md).


### Things in the GTPyhop distribution

  - The [GTPyhop source file](gtpyhop.py), the [open-source license](LICENSE.txt), and a simple [test harness](test_harness.py) for debugging and demonstrating problem domains.
  
  - Several example problem domains and test problems. Go to the `Examples` directory, launch Python 3, and try one or more of the following:

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

  - A version of the Run-Lazy-Lookahead algorithm described in [*Automated Planning and Acting*](http://www.laas.fr/planning). The above test problems include demonstrations of integrated planning and acting using Run-Lazy-Lookahead and GTPyhop.
  
  - The [additional information](additional_information.md) document mentioned earlier. It includes some details about states, actions, and methods, a discussion of backward-compatibility with Pyhop, and comparisons to other planners. 
  

### Related work
    
<!-- 
[This paper](#Ban21) describes a re-entrant version of GTPyhop that has some advantages for integrating acting and planning (e.g., it overcomes the problem demonstrated in the `simple_htn_acting_error` file above.
-->

- The [overview of GTPyhop](http://www.cs.umd.edu/~nau/papers/nau2021gtpyhop.pdf) mentioned above, from the 2021 HPlan workshop.

- A paper about a [re-entrant version of GTPyhop](http://www.cs.umd.edu/~nau/papers/bansod2021integrating.pdf), from the 2021 HPlan workshop.

- Slides from a [presentation about Pyhop](http://www.cs.umd.edu/~nau/papers/nau2013game.pdf) at the 2013 ICAPS Workshop on Planning in Games.


- A paper that classifies [various kinds of hierarchical planning](https://www.ijcai.org/Abstract/16/429). In their terminology, GTPyhop's search strategy is a totally-ordered version of Goal-Task-Network (GTN) planning, without sharing and task insertion.
  
