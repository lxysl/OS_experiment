from EnumClass import PCBState
from proc.PCB import PCB


class PCBQueue:
    def __init__(self):
        self.__pcbList = []

    def getNextPID(self):
        return self.__pcbList[-1] + 1 if self.__pcbList else 0

    def getPCBByPID(self, pid: int):
        return self.__pcbList[pid]

    def append(self, pcb: PCB):
        self.__pcbList.append(pcb)

    def setPCBSuccessor(self, pcb: PCB):
        for i in pcb.getPrecursor():
            prePCB = self.getPCBByPID(i)
            prePCB.addSuccsesor(pcb.getPID())
