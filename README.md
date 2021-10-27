# GridPi

## update - 9/27/20

### Objective
This project was largely an exploration of a modular power system dispatch design. The core problem that prompted it was that every microgrid I'd encountered had its own set of control objectives. Power systems share many of the same goals, but depending on the architecture they achieve those goals (or a subset of goals) differently. The idea was to break the high-level control system into modular pieces, and construct a dispatch control tree/pipeline based on what pieces were loaded.

I began work on the project after reading Steven Skeina's [The Algorithm Design Manual]https://www3.cs.stonybrook.edu/~skiena/. I thought it would be a good application to cement my understanding of (directed) graphs.

### Outcome
I now tend to make the argument all microgrid have the same set of goals:
1. Improve resilience.
2. Minimize cost of energy.
3. Minimize emissions.

The first goal is captured in the primary control objective: don't blackout.  Goals two and three are optimization problems. So solve the optimization problem first, and let that drive the dispatch system. Trying to account for each component's attributes at the highest level of dispatch will overwhelm your design with complexity (even if you wrote a hot graph algorithm to wrangle that complexity).  

Main take-away: **don't design complex systems.**
