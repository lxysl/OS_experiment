from proc.EnumClass import PCBState
from proc.PCB import PCB
from proc.PCBQueue import PCBQueue
from proc.MainMemory import MainMemory


class HangingQueue:
    def __init__(self):
        self.__hangingList = []

    def toJson(self):
        jsonList = []
        for pid in self.__hangingList:
            jsonList.append({'pid': pid})
        return {'hanging_queue': jsonList}

    def appendPCB(self, pcb: PCB):
        self.__hangingList.append(pcb.getPID())
        pcb.setState(PCBState.SUSPENDING)

    def removePCB(self, pcb: PCB):
        self.__hangingList.remove(pcb.getPID())
