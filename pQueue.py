"""
Filename: pQueue
2021 Summer Research Project
Bucknell University
Author: Mohamed Bakr under supervision of Professor Edward Talmage
Function: Augment python's built in priorityQueue to allow for peek without return
"""
import queue


class pQueue(queue.PriorityQueue):
    def peek(self):
        try:
            return self.queue[0]
        except:
            return None


"""
Testing pQueue's peek function
"""
# priorityQueue = pQueue()
# priorityQueue.put((2, "high pr"))
# priorityQueue.put((1, "low pr"))
#
# while priorityQueue:
#     print(priorityQueue.get())
#     if priorityQueue.peek() == None:
#         break
#
#
# print(priorityQueue.get())
# print(priorityQueue.peek())
# print(priorityQueue.get())
# print(priorityQueue.peek())
