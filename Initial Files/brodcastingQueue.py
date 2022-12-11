"""
Trying to implement a queue using MPI
"""
from queue import Queue

from mpi4py import MPI
import time




comm = MPI.COMM_WORLD
myRank = comm.Get_rank()
p = comm.Get_size()

localQueue = Queue()
count = 0
values = [0,1,2,3,4,5,6,7,8,9,10,11]
value = values[count]
process = 0


while count < len(values):
    if myRank == process:
        value = values[count]
        localQueue.put(value)
        print(value, "Added locally to process ", myRank)
        print("Broadcasting a new enqueue")
        start = time.time()
        comm.bcast(value, root=process)

    if myRank != process:
        value = comm.bcast(value, root=process)
        end = time.time()
        localQueue.put(value)

    count += 1
    process += 1
    process = process%3




print(localQueue.queue)
timeTaken = end - start
print("Time Taken for send/receive: ", timeTaken)
