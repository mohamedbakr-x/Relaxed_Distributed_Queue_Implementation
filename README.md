# Relaxed Queue Implementation

2021 Summer Research Project <br />
Bucknell University <br />
Author: Mohamed Bakr under supervision of Professor Edward Talmage <br />
Algorithm implementation for a k-out-of-order relaxed queue in a partially synchronous message passing system <br />
Based on Algorithm 1 from: <br />
E. Talmage and J. L. Welch, “Improving average performance by relaxing distributed data structures,” Lecture Notes in Computer Science, pp. 421–438, 2014.

# Usage:
To run the Algorithm, first you need to have mpi4py library installed on your device <br />
for information on how to install the library please visit: https://mpi4py.readthedocs.io/en/stable/install.html

To run a simulation locally: <br />
mpiexec -n [number of processes] python3 distributedQueue.py [k relaxation factor] [debug level:0, 1, or 2] [test file number] <br />       

To run a simulation with a hostfile : <br />
mpiexec -n [number of processes] --hostfile [host file name] python3 distributedQueue.py [k relaxation factor] [debug level:0, 1, or 2] [test file number]<br />     

