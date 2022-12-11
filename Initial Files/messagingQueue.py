"""
Trying to implement a queue using MPI
"""
from mpi4py import MPI
import time




comm = MPI.COMM_WORLD
myRank = comm.Get_rank()
p = comm.Get_size()

localQueue = []

def sendEnqueue(value):
    if myRank == 0:
        localQueue.append(value)
        print("Added locally")
        print("Sending a new enqueue")
        start = time.time()
        comm.send(value, dest=1)
        return start

def recieveEnqueu():
    if myRank != 0:
        value = comm.recv(source=0)
        end = time.time()
        localQueue.append(value)
        return end



start = sendEnqueue(2)
end = recieveEnqueu()
timeTaken = end - start
print(localQueue)
print("Time Taken for send/receive: ", timeTaken)


