from proc.PCBQueue import PCBQueue
from proc.Config import ProcessorNum


class Processor:
    def __init__(self):
        self.__readyList = []
        for i in range(ProcessorNum):
            self.__readyList.append([])

    def process(self, pcb_list: PCBQueue):
        for l in self.__readyList:
            if l:
                pid = l.pop(0)
                pcb_list.getPCBByPID(pid).process()
