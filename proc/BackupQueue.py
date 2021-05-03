from EnumClass import PCBState, Property
from proc.PCB import PCB
from proc.PCBQueue import PCBQueue
from proc.MainMemory import MainMemory


class BackupQueue:
    def __init__(self):
        self.__backupList = []

    def append(self, pid: int):
        self.__backupList.append(pid)

    def autoRemove(self, pcb_queue: PCBQueue, memory: MainMemory):
        # 从后备队列中找出优先级最高、无前驱（或前驱已经完成）且能放入内存的进程PID
        PIDDic = {i: pcb_queue.getPCBByPID(i).getProperty() for i in self.__backupList}
        sortedList = sorted(PIDDic.items(), key=lambda item: item[1], reverse=True)
        for pid, priority in sortedList:
            pcb = pcb_queue.getPCBByPID(pid)
            if pcb.getProperty() == Property.INDEPENDENT:
                # 独立进程
                isAssignable, partitionNum = memory.checkAssignable(pcb)
                if isAssignable:
                    memory.insertPCB(pcb, partitionNum)
                    self.__backupList.pop(pid)
            else:
                # 同步进程
                precursorList = pcb.getPrecursor()
                preExitList = [pcb_queue.getPCBByPID(i).getState() == PCBState.EXIT for i in precursorList]
                if sum(preExitList) == len(preExitList):
                    # 前驱进程全部完成
                    isAssignable, partitionNum = memory.checkAssignable(pcb)
                    if isAssignable:
                        memory.insertPCB(pcb, partitionNum)
                        self.__backupList.pop(pid)
