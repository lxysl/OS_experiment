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

    # def getSortedList(self):
    #     # 返回按优先级降序排序的未终止进程(PID:priority)元组列表
    #     PIDDic = {}
    #     for i in self.__pcbList:
    #         if i.getState() != PCBState.EXIT:
    #             PIDDic[i.getPID()] = i.getPriority()
    #     return sorted(PIDDic.items(), key=lambda item: item[1], reverse=True)
