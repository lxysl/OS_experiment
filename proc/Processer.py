from proc.PCB import PCB
from proc.Config import ProcessorNum
from proc.PCBQueue import PCBQueue


class Processor:
    # 是MainMemory的内部类吗？
    def __init__(self):
        self.__processorNum = ProcessorNum  # 处理机个数
        self.__processorPCBList = [[] for _ in range(self.__processorNum)]  # 每个处理机上待处理的进程PID列表

    def toJson(self):
        jsonList = []
        for index, processor in enumerate(self.__processorPCBList):
            jsonList.append({
                'id': '处理机' + str(index),
                'pid_list': [{'pid': pid} for pid in self.__processorPCBList[index]]
            })
        return {'processors': jsonList}

    def process(self, pcb_list: PCBQueue):
        # 每个处理机执行一个单位时间的进程任务，更新每个处理机的进程所需时间
        for i in range(self.__processorNum):
            if l := self.__processorPCBList[i]:
                if pcb_list.getPCBByPID(l[0]).process():
                    l.pop(0)

    def removePCB(self, pcb: PCB):
        location = (0, 0)
        for i in range(self.__processorNum):
            for j in self.__processorPCBList[i]:
                if j == pcb.getPID():
                    location = (i, j)
                    break
        self.__processorPCBList[location[0]].pop(location[1])

    def dispatchPCB(self, sortedList: list):
        # 为进程分配处理机
        self.__processorPCBList = [[] for _ in range(self.__processorNum)]
        processorID = 0
        for pid, priority in sortedList:
            self.__processorPCBList[processorID].append(pid)
            processorID = (processorID + 1) % self.__processorNum
