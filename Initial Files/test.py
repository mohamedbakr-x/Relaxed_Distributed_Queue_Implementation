from mpi4py import MPI

comm = MPI.COMM_WORLD
myRank = comm.Get_rank()
p = comm.Get_size()

if myRank != 0:
    message = "Hello from " + str(myRank)
    comm.send(message, dest=0)

else:
    for procid in range(1,p):
        message = comm.recv(source = procid)
        print("process 0 recieves message from process",procid, ":", message)
