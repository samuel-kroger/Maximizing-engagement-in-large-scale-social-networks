# Maximizing resilience in large-scale social networks

Codes, data, and results for "Maximizing resilience in large-scale social networks" by Samuel Kroger, Hamidreza Validi, and Illya V. Hicks.

The $k$-core of a graph is the maximal subgraph in which every vertex has a degree of at least $k$.
Below we computed the $4$-core of the karate graph. Blue vertices represent the members of the $4$-core. Interestingly, both administrator (John A) and instructor (Mr. Hi) belong to the $4$-core!

![Figure 1](git_images/karate_k4b0.png?raw=true "The 4-core of the karate graph")

Motivated by maximizing resilience in social networks, we propose an integer programming model for solving the maximum anchored $k$-core problem. In this variant of the maximum $k$-core problem, we spend a budget $b$ to expand the size of the $k$-core. Anchored (or purchased) vertices can be part of the anchored $k$-core even if their degree is less than $k$. In the following network of the karate club, blue vertices form a set of $4$-core and yellow vertices represent an anchored vertex set when the total budget $b$ is 4. It should be noted that all yellow vertices (anchored vertices) have a degree less than 4.

![Figure 2](git_images/karate_k4b5.png?raw=true "The Anchored 4-core with budget 5 of the karate graph")

In the "src" directory, you will find the codes employed in the paper.
The heuristic RCM comes from the [Residual Core Maximization: An efficient algorithm for maximizing the size of the k-core](https://epubs.siam.org/doi/abs/10.1137/1.9781611976236.37)
The heuristic OLAK comes from the [OLAK: an efficient algorithm to prevent unraveling in social networks](https://dl.acm.org/doi/abs/10.14778/3055330.3055332?casa_token=0pjIWubvxCcAAAAA:CEnA7bA_ocYH6--CIpfGsJ3zuICIrXdS9NxWcyAumXnl0Ppb-KH4cPUF4ABq-y2MxTWE2xnfBf1Af4s)
The code for the implementations of OLAK and RCM come from this [github repo](https://github.com/rlaishra/RCM/).
The PORTA directory contains the [PORTA](http://porta.zib.de/) software used in the paper.
To run our models, run comp_experiment.py which will run based off of the data.json file.

## How to run the code?

In the "data" directory, you can find all the data used in the paper. Data is also publically avialble at [SNAP](https://snap.stanford.edu/data/) and [Network Repository](https://networkrepository.com/index.php).

git_images contains the images in the README

The results directory has csv data and log files of the runs.

```
C:\src\comp_expermient.py
```
