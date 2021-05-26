from proc.EnumClass import PCBState, Property
from proc.PCB import PCB
from proc.PCBQueue import PCBQueue
from proc.MainMemory import MainMemory


class BackupQueue:
    def __init__(self):
        self.__backupList = []

    def toJson(self):
        jsonList = []
        for pid in self.__backupList:
            jsonList.append({'pid': pid})
        return {'backup_queue': jsonList}

    def appendPCB(self, pcb: PCB):
        self.__backupList.append(pcb.getPID())
        pcb.setState(PCBState.STATIC_READY)

    def autoRemove(self, pcb_queue: PCBQueue, memory: MainMemory):
        # 从后备队列中找出优先级最高、无前驱（或前驱已经完成）且能放入内存的进程PID
        PIDDic = {i: pcb_queue.getPCBByPID(i).getPriority() for i in self.__backupList}
        sortedList = sorted(PIDDic.items(), key=lambda item: item[1], reverse=True)  # 按优先权降序排序
        for pid, priority in sortedList:
            pcb = pcb_queue.getPCBByPID(pid)
            if pcb.getProperty() == Property.INDEPENDENT:
                # 独立进程
                isAssignable, partitionNum = memory.checkAssignable(pcb)
                if isAssignable:
                    memory.insertPCB(pcb, partitionNum)
                    self.__backupList.pop(pid)
                    return pcb.getPID()
            else:
                # 同步进程
                precursorList = pcb.getPrecursor()
                preExitList = [pcb_queue.getPCBByPID(i).getState() == PCBState.EXIT for i in precursorList]
                if sum(preExitList) == len(preExitList):
                    # preExitList中全部为True，前驱进程全部完成
                    isAssignable, partitionNum = memory.checkAssignable(pcb)
                    if isAssignable:
                        memory.insertPCB(pcb, partitionNum)
                        self.__backupList.pop(pid)
                        return pcb.getPID()
        return -1   # 无进程进入内存

    def removePCB(self, pcb: PCB):
        self.__backupList.remove(pcb.getPID())
