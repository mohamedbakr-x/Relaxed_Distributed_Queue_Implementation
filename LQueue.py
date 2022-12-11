"""
Filename: LQueue
2021 Summer Research Project
Bucknell University
Author: Mohamed Bakr under supervision of Professor Edward Talmage
Function: Augment python's built in queue with extra functionality
"""
import queue


class LQueue(queue.Queue, object):
    def __init__(self):
        super(LQueue, self).__init__()
        self.unlabeledCount = 0  # counter for unlabeled elements

    # Inherit the put function but adds ability to increment counter for unlabeled elements
    def put(self, item, block=True, timeout=None):
        super().put(item, block, timeout)
        if type(item) is tuple and item[1] is None:
            self.unlabeledCount += 1  # increment unlabeled counter if element is ublabeled

    # Getter for the unlabeled elements counter
    def getUnlabeledCount(self):
        return self.unlabeledCount

    # Peek on the first element of the queue without returning it
    def peek(self):
        try:
            return self.queue[0]
        except:
            return None

    # Helper function to return last element of the queue
    def getTail(self):
        length = self.qsize()
        return self.queue[length - 1]

    # Helper function to display the flattened queue i.e. elements without their labels
    def flattenQueue(self):
        flattenedQueue = []
        if type(self.peek()) is tuple:
            for element in self.queue:
                flattenedQueue.append(element[0])
        else:
            for element in self.queue:
                flattenedQueue.append(element)
        return flattenedQueue

    # Function that peeks on oldest element with a certain process label without returning it
    def peekByLabel(self, processLabel, k):
        for i in range(min(self.qsize(), k)):
            if self.queue[i][1] == processLabel:
                return self.queue[i]
            elif self.queue[i][1] is None:
                return None

    # Function that dequeues the oldest elements labeled by a certain process
    def deqByLabel(self, processLabel, k):
        for i in range(min(self.qsize(), k)):
            if self.queue[i][1] == processLabel:
                deqElement = self.queue[i]
                self.queue.remove(deqElement)
                return deqElement
            elif self.queue[i][1] is None:
                return None

    # Takes oldest numToLabel elements in the queue and labels them with processLabel
    def labelOldestElement(self, processLabel, numToLabel):
        for i in range(self.qsize()):
            element = self.queue[i]
            if element[1] is None:
                tempList = list(element)
                tempList[1] = processLabel
                self.queue[i] = tuple(tempList)
                numToLabel -= 1
                if numToLabel == 0:
                    break

    # removes value from the queue
    def remove(self, value):
        for element in self.queue:
            if element[0] == value[0]:
                self.queue.remove(element)
                break


"""
Testing the LQueue class
"""
# lq = LQueue()
# lq.put((1, 1))
# lq.put((1, 2))
# lq.put((3, 3))
# lq.put((6, None))
# lq.put((8, None))
# lq.put((8, None))
# print("peek by label at process 2: ", lq.peekByLabel(3, 4))
# ret = lq.peekByLabel(2,4)
# lq.labelElement(2, 1)
# fq = lq.flattenQueue()
# lq.remove((1,1))
# lq.labelOldestElement(2,3)
# print(">>>>>>",lq.getUnlabeledCount())
# print("ret ", lq.deqByLabel(None,5))
# print(lq.queue)
# print(lq.qsize())

