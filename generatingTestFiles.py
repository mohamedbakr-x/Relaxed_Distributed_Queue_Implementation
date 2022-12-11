"""
Filename: generatingTestFiles.py
2021 Summer Research Project
Bucknell University
Author: Mohamed Bakr under supervision of Professor Edward Talmage
Function: Generate test files for the distributed Queue algorithm with random invocations
"""
import random
import decimal
import sys

numberOfProcesses = int(sys.argv[1])
testFileN = 4
invocations = ["Enq", "Deq"]
timeAfterStart = 0
enqTotal = 0
deqTotal = 0

filename = "Tests/test" + str(testFileN) + ".txt"
f = open(filename, "w")
for i in range(2000):
    randTime = float(decimal.Decimal(random.randrange(1,100))/100)
    timeAfterStart = round(timeAfterStart + randTime, 2)
    process = random.choice(range(numberOfProcesses))
    invocation = random.choice(invocations)

    if invocation == "Enq":
        value = random.randint(0, 100)
        enqTotal += 1
    else:
        value = -1
        deqTotal += 1

    line = str(timeAfterStart) + ", " + str(process) + ", " + invocation + ", " + str(value) + "\n"
    f.write(line)

finalTime = timeAfterStart + 5
terminateLine = str(finalTime) + ", -1, Ter, -1\n"
f.write(terminateLine)
f.close()
# print("Total Enqueues: ", enqTotal)
# print("Total Dequeues: ", deqTotal)
# print("Number of elements in the queue should be: ", enqTotal-deqTotal)




