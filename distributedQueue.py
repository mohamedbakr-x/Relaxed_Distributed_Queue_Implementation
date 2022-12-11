"""
Filename: distributedQueue.py
2021 Summer Research Project
Bucknell University
Author: Mohamed Bakr under supervision of Professor Edward Talmage
Algorithm implementation for a k-out-of-order relaxed queue in a partially synchronous message passing system
Based on Algorithm 1 from:
E. Talmage and J. L. Welch, “Improving average performance by relaxing distributed data structures,” Lecture Notes in Computer Science, pp. 421–438, 2014.
"""

from pQueue import pQueue
from LQueue import LQueue
from mpi4py import MPI
from math import floor
import sys
import time

relaxationFactor = int(sys.argv[1])  # relaxation factor
debugLevel = int(sys.argv[2])  # debug level
testFileN = int(sys.argv[3])  # test file number

comm = MPI.COMM_WORLD  # Creates the MPI communication world
myRank = comm.Get_rank()  # Each process gets its rank
n = comm.Get_size()  # Gets the total number of processes running n

pending = pQueue()  # creates a priority queue for pending invocations
maxDelay = 0.3  # set maximum message delay in seconds
u = 0.05  # maxDelay - u is the minimum message delay
epsilon = 0.001  # epsilon the maximum out-of-synchronous time between any two processes
localQueue = LQueue()  # creates local queue version in each process
timers = pQueue()  # creates a priority queue to store timers
clean = True
pendingInstance = False

# Variables used in measuring average time invocations take
enqTimeList = []
deq_fTimeList = []
deq_sTimeList = []
enqStartTime = 0
enqEndTime = 0
deq_fStartTime = 0
deq_fEndTime = 0
deq_sStartTime = 0
deq_sEndTime = 0

# reqs = []

"""
setTimer 
@desc: Sets a new timer that expires after a certain timer delay passed as td
@params: 
    td: time delay for timer
    op: operation type
    value: value of operation
    ts: timestamp of operation
    TimerType: respond, selfPending, execute, invoke, Terminate
@return: does not have a return value
"""


def setTimer(td, op, value, ts, TimerType):
    tsTime, processID = ts
    expirationTime = tsTime + td
    timers.put((expirationTime, (op, value, (time.time(), processID), TimerType)))


"""
handleEnqueue
@desc: handles an Enqueue invocation by broadcasting to all process that a new value needs to be enqueued
@params: 
    processID: process at which enqueue happened
    value: value to be enqueued in the queue
@return: does not have a return value
"""


def handleEnqueue(processID, value):
    global pendingInstance
    pendingInstance = True

    global enqStartTime
    enqStartTime = time.time()

    # Broadcasting the enqueued value to all other processes
    for i in range(n):
        if myRank != i:
            req = comm.isend(("enq", value, (time.time(), processID)), dest=i)
            req.wait()
            # reqs.append(req)
        elif myRank == i:
            setTimer(maxDelay - u, "enq", value, (time.time(), processID), "selfPending")

    if debugLevel == 2:
        print("Process: ", myRank, "Enqueue broadcast to all from process: ", processID)

    setTimer(epsilon, "enq", value, (time.time(), processID), "respond")


"""
handleEnqueue
@desc: handles a Dequeue invocation based on whether it is a fast or a slow dequeue by announcing the dequeue to other processes
@params: 
    processID: process at which dequeue happened
@return: does not have a return value
"""


def handleDequeue(processID):
    global pendingInstance
    pendingInstance = True

    global deq_fStartTime
    global deq_sStartTime

    if localQueue.peekByLabel(processID, relaxationFactor) is not None:
        deq_fStartTime = time.time()
        ret = localQueue.peekByLabel(processID, relaxationFactor)
        for i in range(n):
            if myRank != i:
                req = comm.isend(("deq_f", ret, (time.time(), processID)), dest=i)
                req.wait()
            # reqs.append(req)

            elif myRank == i:
                setTimer(maxDelay - u, "deq_f", ret, (time.time(), processID), "selfPending")

        if debugLevel == 2:
            print("Process: ", myRank, "Dequeue broadcast to all from process: ", processID)
        if debugLevel == 1 or debugLevel == 2:
            print("Process: ", myRank, "The local Queue: ", localQueue.queue)

        setTimer(epsilon, "deq_f", ret, (time.time(), processID), "respond")
    else:
        deq_sStartTime = time.time()
        for i in range(n):
            if myRank != i:
                req = comm.isend(("deq_s", None, (time.time(), processID)), dest=i)
                req.wait()
                # reqs.append(req)
            elif myRank == i:
                setTimer(maxDelay - u, "deq_s", None, (time.time(), processID), "selfPending")


"""
handleEnqueue
@desc: handles any arrived messages by putting them on the pending queue and setting a timer to execute the messages contents
@params: 
    op: operation type of the message
    value: enqueue value for enq message or None for deq message
    ts: timestamp of the operation
@return: does not have a return value
"""
def handleMessage(op, value, ts):
    # Pushing the message to the priority queue based on time it arrived ts
    if debugLevel == 2:
        print("Process: ", myRank, "received message")
        print("Process: ", myRank, "putting it on pending")

    pending.put((ts[0], (op, value, ts)))

    if debugLevel == 1 or debugLevel == 2:
        print("Process: ", myRank, "Pending Queue: ", pending.queue)
    if debugLevel == 2:
        print("Process: ", myRank, "setting the Timer")

    setTimer(u + epsilon, op, value, ts, "execute")

"""
handleExpireTimer
@desc: handles any expired timers based on the timer type
@params: 
    op: operation type of the timer
    value: enqueue value for enq message or None for deq message
    ts: timestamp of timer
    TimerType: respond, selfPending, execute, invoke, Terminate
@ret does not have a return value
"""
def handleExpireTimer(op, value, ts, TimerType):
    global pendingInstance
    global enqEndTime
    global deq_fEndTime

    # if debugLevel == 2:
    #     print("Process: ", myRank, "Handling an expired Timer")

    tsTime, processID = ts
    if TimerType == "respond":
        if op == "deq_f":
            pendingInstance = False
            deq_fEndTime = time.time()
            deq_fTime = deq_fEndTime - deq_fStartTime
            deq_fTimeList.append(deq_fTime)

            if debugLevel == 2:
                print("Process: ", myRank, "Fast Dequeue Acknowledgement")

            return value
        else:
            pendingInstance = False
            enqEndTime = time.time()
            enqTime = enqEndTime - enqStartTime
            enqTimeList.append(enqTime)

            if debugLevel == 2:
                print("Process: ", myRank, "Enqueue Acknowledgement")
            return "ACK"

    elif TimerType == "execute" and not pending.empty():
        # print("Process: ", myRank, "Pending Queue: ", pending.queue)
        while tsTime >= (pending.peek()[0]):
            opP, valP, tsP = pending.get()[1]
            executeLocally(opP, valP, tsP)
            if pending.empty():
                break

    elif TimerType == "selfPending":
        pending.put((tsTime, (op, value, ts)))


    elif TimerType == "invoke" and not pendingInstance:
        if op == "invEnq":
            if debugLevel == 2:
                print("Process: ", myRank, "Creating an  Enqueue invocation")

            handleEnqueue(processID, value)
        elif op == "invDeq":

            if debugLevel == 2:
                print("Process: ", myRank, "Creating a Dequeue invocation")

            handleDequeue(processID)

    elif TimerType == "invoke" and pendingInstance:
        timers.put((time.time(), (op, value, ts, TimerType)))

    elif TimerType == "Terminate":
        # print("Process: ", myRank, " The local Queue: ", localQueue.queue)
        print("Process: ", myRank, " The local Queue [Flattened]: ", localQueue.flattenQueue())
        # print("Process: ", myRank, " Enqueue Time List: ", enqTimeList)
        # print("Process: ", myRank, " Fast Dequeue Time List: ", deq_fTimeList)
        # print("Process: ", myRank, " Slow Dequeue Time List: ", deq_sTimeList)
        # MPI.Request.waitall()
        quit()

"""
executeLocally
@desc: executes an enqueue or dequeue operation on the local version of the queue
@params: 
    op: operation type to be executed
    value: enqueue value for enq message or None for deq message
    ts: timestamp of operation
@ret does not have a return value
"""
def executeLocally(op, value, ts):
    global clean
    global pendingInstance
    global deq_sEndTime

    tsTime, processID = ts
    if op == "enq":
        # print("Process: ", myRank, " Clean Value: ", clean)
        if clean and localQueue.qsize() < relaxationFactor:
            processLabel = (localQueue.qsize()) % n
            localQueue.put((value, processLabel))

            if debugLevel == 1 or debugLevel == 2:
                print("Process: ", myRank, " The local Queue: ", localQueue.queue)

        else:
            localQueue.put((value, None))
            if debugLevel == 1 or debugLevel == 2:
                print("Process: ", myRank, " The local Queue: ", localQueue.queue)

    else:
        clean = False
        if op == "deq_f":
            if debugLevel == 1 or debugLevel == 2:
                print("Process: ", myRank, " Fast Dequeued Value: ", value)

            # deqProcess = processID
            # if deqProcess != myRank:
            localQueue.remove(value)
            # print("Process: ", myRank, " The local Queue: ", localQueue.queue)

        elif op == "deq_s":
            if localQueue.peekByLabel(processID, relaxationFactor) is not None:
                ret = localQueue.deqByLabel(processID, relaxationFactor)

                if debugLevel == 1 or debugLevel == 2:
                    print("Process: ", myRank, " Slow Dequeued Value: ", ret)

            else:
                ret = localQueue.deqByLabel(None, relaxationFactor)

                if debugLevel == 1 or debugLevel == 2:
                    print("Process: ", myRank, " Slow Dequeued Value: ", ret)

            labelOldestElement(processID)

            if processID == myRank:
                pendingInstance = False

                deq_sEndTime = time.time()
                deq_sTime = deq_sEndTime - deq_sStartTime
                deq_sTimeList.append(deq_sTime)

                # Solved an error here
                if localQueue.qsize() == 0:
                    clean = True
                return ret

        if localQueue.qsize() == 0:
            clean = True

"""
labelOldestElement
@desc: labels a certain number of queue elements by processID. It calculates the number of old elements that needs to be labeled. 
@params: 
    processID: the process ID that will be labeled to the elements
@ret does not have a return value
"""
def labelOldestElement(processID):
    numToLabel = min(floor(relaxationFactor / n), floor(localQueue.qsize() / n), localQueue.getUnlabeledCount())

    if debugLevel == 2:
        print("Process: ", myRank, "Labeling Oldest elements of num: ", numToLabel, "with process ID: ", processID)

    if numToLabel > 0:
        localQueue.labelOldestElement(processID, numToLabel)

"""
Main function that simulates a run through the algorithm by reading test file invocations and running them on the distributed Queue
"""
def main():
    # Simulate the manipulation of a queue by invoking events
    startTime = time.time()

    if debugLevel == 1 or debugLevel == 2:
        print("Process: ", myRank, "Start Time: ", startTime)


    # Reads invocations from the testfile and creates events out of them

    # testFileName = "Tests/test" + str(testFileN) + ".txt"
    testFileName = "correctionTests/test" + str(testFileN) + ".txt"
    # Reading events from file
    events = []
    with open(testFileName, "r") as eventsFile:
        for i in eventsFile.readlines():
            if i[0] != "#":
                tmpEvent = i.split(",")
                if myRank == int(tmpEvent[1]) or int(tmpEvent[1]) == -1:
                    try:
                        events.append(
                            (float(tmpEvent[0]), int(tmpEvent[1]), str(tmpEvent[2]).strip(), int(tmpEvent[3])))
                    except:
                        pass

    if debugLevel == 1 or debugLevel == 2:
        print("Process: ", myRank, "Events: ", events)

    # Sets timers for all of the events in the testfile
    for i in events:
        timeAfterStart, processID, eventAction, value = i
        # print(timeAfterStart, processID, eventAction, value)
        if eventAction == "Enq":
            setTimer(timeAfterStart, "invEnq", value, (startTime, processID), "invoke")
        elif eventAction == "Deq":
            setTimer(timeAfterStart, "invDeq", value, (startTime, processID), "invoke")
        elif eventAction == "Ter":
            setTimer(timeAfterStart, "Ter", value, (startTime, processID), "Terminate")

    # Initialize messageContent and receiver for messages
    req = comm.irecv(source=MPI.ANY_SOURCE)

    """
    Main loop that listens for any arrived messages and handles them
    The loop also keeps checking for expired timers to handle them
    The loop terminates when a timer of type "terminate" expires
    """
    while True:

        requestData = req.test()
        status = requestData[0]
        data = requestData[1]

        # print("Process: ", myRank, " requestData: ", requestData)
        if status and data is None:
            req = comm.irecv(source=MPI.ANY_SOURCE)

        elif data is not None:
            messageContent = requestData[1]
            # print("Process: ", myRank, " messageContent: ", messageContent)
            op, val, ts = messageContent
            handleMessage(op, val, ts)

        while not timers.empty() and time.time() >= timers.peek()[0]:
            # if debugLevel == 2:
            #     print("Process: ", myRank, "Getting expired timer")

            executeTimer = timers.get()
            op, val, ts, TimerType = executeTimer[1]
            handleExpireTimer(op, val, ts, TimerType)


main()
