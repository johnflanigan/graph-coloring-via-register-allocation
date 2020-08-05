# Register Allocation and Spilling via Graph Coloring

## Register Allocation
* Define basic compiler terminology required.
* Explain motivation for register allocation.
* Explain how graph coloring concept maps to register allocation.

## Overview of Chaitin's algorithm
* Broad overview of Chaitin's algorithm. 
* Describe steps of algorithm.

## Basic Example
* Discussion of simple example that is easily colorable.
* Discuss liveness.
* Discuss intermediate language and how it maps to simple code example.

## Subsumption Example
* Discussion of subsumption.
* Example where unnecessary copy operations are eliminated.

## Multiple Building Blocks
* Discussion of larger example with multiple building blocks.

## Spilling
* Take same example as in multiple building blocks, but reduce available colors to force spilling registers.
* Discussion of spilling, frequency
* What does spilling mean to register allocation?
* Explain motivation of frequency approach.
  * Discussion of frequency algorithm.

## Improvements (__If above content is too sparse__)
* Discussion of improvements introduced by Briggs et al. Implementation focused on Chaitin's algorithm so this discussion will not have examples.

## Running locally
* Instructions on running locally

## Resources
* Paper I am implementing
  * https://cs.gmu.edu/~white/CS640/p98-chaitin.pdf
* Used to better understand paper 
  * http://kodu.ut.ee/~varmo/TM2010/slides/tm-reg.pdf
* Another example, provides useful test cases with multiple building blocks
  * http://web.cecs.pdx.edu/~mperkows/temp/register-allocation.pdf
* SETL documentation
  * https://www.sciencedirect.com/science/article/pii/0898122175900115
* Briggs et al. paper
  * http://www.cs.utexas.edu/users/mckinley/380C/lecs/briggs-thesis-1992.pdf
* Python graph drawing
  * https://networkx.github.io/
