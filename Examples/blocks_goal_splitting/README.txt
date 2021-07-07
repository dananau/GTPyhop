The blocks_goal_splitting domain illustrates how to achieve blocks-world multigoals using GTPyhop's built-in m_split_multigoal method, which splits a multigoal into a list of unigoals and tries to achieve them sequentially. Due to deleted-condition interactions (in which achieving a later unigoal undoes a previously-achieved unigoal), this usually won't produce a state in which the entire multigoal has been achieved. If repeated sufficiently many times, it will eventually produce such a state -- but as illustrated by the planning problems in the examples.py file, the solution plans are much longer than they need to be.

This would work much better if GTPyhop had an intelligent way to choose an order in which to achieve the unigoals. That would require either modifying m_split_multigoals to use a heuristic function (which is something we have not implemented), or else writing a domain-specific multigoal method and using it instead of m_split_multigoals, as in the blocks_hybrid example domain.

--Dana Nau, July 2, 2021

