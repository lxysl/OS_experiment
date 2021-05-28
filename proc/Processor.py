from proc.EnumClass import PCBState, Property
from proc.PCB import PCB
from proc.Config import ProcessorNum
from proc.PCBQueue import PCBQueue


class Processor:
    def __init__(self):
        self.__processorNum = ProcessorNum  # 处理机个数
        self.__processorPCBList = [[] for _ in range(self.__processorNum)]  # 每个处理机上待处理的进程PID列表

    def getProcessorPCBList(self):
        return self.__processorPCBList

    def toJson(self):
        jsonList = []
        for index, processor in enumerate(self.__processorPCBList):
            jsonList.append({
                'id': '处理机' + str(index),
                'pid_list': [{'pid': pid} for pid in self.__processorPCBList[index]]
            })
        return {'processors': jsonList}

    def process(self, pcb_queue: PCBQueue):
        # 每个处理机执行一个单位时间的进程任务，更新每个处理机的进程所需时间
        current_exits = []
        for i in range(self.__processorNum):
            if l := self.__processorPCBList[i]:
                pcb_to_process = pcb_queue.getPCBByPID(l[0])
                if pcb_to_process.getProperty() == Property.INDEPENDENT:
                    pass  # 独立进程
                else:
                    # 同步进程
                    precursorList = pcb_to_process.getPrecursor()
                    preExitList = [pcb_queue.getPCBByPID(i).getState() == PCBState.EXIT for i in precursorList]
                    if sum(preExitList) != len(preExitList):
                        continue  # preExitList中不全部为True，前驱进程未全部完成
                    if current_exits != [] and [i for i in current_exits if i in precursorList] != []:
                        continue  # 其前驱进程刚在本次运行的不同处理机中结束
                if pcb_queue.getPCBByPID(l[0]).process():
                    exit_pid = l.pop(0)
                    current_exits.append(exit_pid)

    def removePCB(self, pcb: PCB):
        location = (0, 0)
        flag = False  # 处理机中是否存在该进程
        for i in range(self.__processorNum):
            for j, pid in enumerate(self.__processorPCBList[i]):
                if pid == pcb.getPID():
                    location = (i, j)
                    flag = True
                    break
        if flag:
            self.__processorPCBList[location[0]].pop(location[1])
            return True
        else:
            return False

    def dispatchPCB(self, sorted_list: list):
        # 为进程分配处理机
        self.__processorPCBList = [[] for _ in range(self.__processorNum)]
        processorID = 0
        for pid, priority in sorted_list:
            self.__processorPCBList[processorID].append(pid)
            processorID = (processorID + 1) % self.__processorNum
