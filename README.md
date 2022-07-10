# Maximizing resilience in large-scale social networks

Codes, data, and results for "Maximizing resilience in large-scale social networks" by Samuel Kroger, Hamidreza Validi, and Illya V. Hicks.

The $k$-core of a graph is the maximal subgraph in which every vertex has a degree of at least $k$.
Below we computed the $4$-core of the karate graph. Blue vertices represent the members of the $4$-core. Interestingly, both administrator (John A) and instructor (Mr. Hi) belong to the $4$-core!

![Figure 1](git_images/karate_k4b0.png?raw=true "The 4-core of the karate graph")

In our paper and this github repo we explore solving an extension of $k$-core called anchored $k$-core.
In this variant we spend a budget $b$ to expand the size of the $k$-core.
Anchored nodes can be part of the anchored $k$-core even if the degree of the node is less than $k$.

![Figure 2](git_images/karate_k4b5.png?raw=true "The Anchored 4-core with budget 5 of the karate graph")

In the code directory you will find all of the code used in the paper.
The heuristic RCM comes from the [paper](https://www.osti.gov/servlets/purl/1766701)
The heuristic OLAK comes from the [paper](http://www.vldb.org/pvldb/vol10/p649-zhang.pdf)
The code for the implementations of OLAK and RCM come from this [github repo](https://github.com/rlaishra/RCM/).
The PORTA directory contains the [PORTA](http://porta.zib.de/) software used in the paper.
To run our models, run comp_experiment.py which will run based off of the data.json file.

## How to run the code?

IN the code data you will find all the data used in the paper they are publically avialble from [SNAP](https://snap.stanford.edu/data/) and the [Network Repository](https://networkrepository.com/index.php)

git_images contains the images in the README

The results directory has csv data and log files of the runs.

```
C:\src\comp_expermient.py
```
