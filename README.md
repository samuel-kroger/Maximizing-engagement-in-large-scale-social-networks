# Integer programming formulations for maximizing resilience in large-scale social networks

Codes, data, and results for "Integer programming formulations for maximizing resilience in large-scale social networks" by Samuel Kroger, Hamidreza Validi, and Illya V. Hicks.

The $k$-core of a graph is the maximal subgraph in which every node has degree $k$.
Below we computed the $4$-core of the karate graph, here there are 10 members of the $4$-core.
![Figure 1](git_images/karate_k4b0.png?raw=true "The 4-core of the karate graph")
In our paper and this github repo we explore solving an extension of $k$-core called anchored $k$-core.
In this variant we spend a budget $b$ to expand the size of the $k$-core.
Anchored nodes can be part of the anchored $k$-core even if the degree of the node is less than $k$.
![Figure 2](git_images/karate_k4b5.png?raw=true "The Anchored 4-core with budget 5 of the karate graph")