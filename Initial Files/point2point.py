# Based on examples from https://mpi4py.readthedocs.io/en/stable/tutorial.html#point-to-point-communication

from mpi4py import MPI
import time
import socket
from time import sleep

# name = socket.gethostbyname(socket.gethostname())

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
p = comm.Get_size()

msgStartTime = 0
msgEndTime = 0

print('rank: ',rank)
# print('hostname: ',name)



# Non-blocking send/receive
if rank == 0:
    for i in range(p):
        msgStartTime = time.time()
        req = comm.isend(msgStartTime, dest=i)

    # req2.Wait()
    # print("Process: ", rank, 'sent')

else:
    req = comm.irecv(source=0)
    while True:
        startTime = req.test()
        if startTime[0]:
            msgEndTime = time.time()
            msgTime = msgEndTime - startTime[1]
            print("Process: ", rank, "Message Time is sec: ", msgTime)
            break
    # print("Process: ", rank, 'received: ')



