from proc.PCB import PCB


class PCBQueue:
    def __init__(self):
        self.__pcbList = []

    def getNextPID(self):
        return self.__pcbList[-1].getPID() + 1 if self.__pcbList else 0

    def getPCBByPID(self, pid: int):
        return self.__pcbList[pid]

    def toJson(self):
        pcb_list = []
        for pcb in self.__pcbList:
            pcb_list.append(pcb.toJson())
        return {'pcb_list': pcb_list}

    def append(self, pcb: PCB):
        self.__pcbList.append(pcb)
        self.setPCBSuccessor(pcb)

    def setPCBSuccessor(self, pcb: PCB):
        for i in pcb.getPrecursor():
            prePCB = self.getPCBByPID(i)
            prePCB.addSuccessor(pcb.getPID())
