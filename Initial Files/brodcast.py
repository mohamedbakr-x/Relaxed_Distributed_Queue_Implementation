from mpi4py import MPI

comm = MPI.COMM_WORLD
myRank = comm.Get_rank()
p = comm.Get_size()
name = ""

if myRank == 0:
    name = str(input("Enter your name: "))
    print("\nBroadcasting your name to all processes")
    name = comm.bcast(name, root=0)


else:
    name = comm.bcast(name, root=0)
    print("Hello ", name , "from process ", myRank)
