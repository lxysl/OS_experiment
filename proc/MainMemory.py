from proc.Config import Memory, OSMemory
from proc.EnumClass import PCBState, MemoryBlockState, Property
from proc.PCB import PCB
from proc.PCBQueue import PCBQueue
from proc.Processor import Processor


class MainMemory:
    def __init__(self):
        self.__readyList = []
        # 有序分区表[[PID, 起址, 长度, 状态], ...]，按起始地址进行升序排序
        # 内存分区表中对应存储的PID，OS对应的内存表项用-1表示，未分配内存表项用-2表示
        self.__memory = [[-1, 0, OSMemory, MemoryBlockState.OS_ASSIGNED],
                         [-2, OSMemory, Memory - OSMemory, MemoryBlockState.UNASSIGNED]]
        # self.__memoryPCB = [-1, -2]

    def toJson(self):
        jsonList = []
        for index, memoryBlock in enumerate(self.__memory):
            jsonList.append({
                'memory_PCB': memoryBlock[0],
                'start': memoryBlock[1],
                'length': memoryBlock[2],
                'memory_state': memoryBlock[3].name,
            })
        return {'main_memory': jsonList}

    def checkAssignable(self, pcb: PCB):
        # 检测是否可分配空间，同时返回可分配内存空间的起始地址
        for index, memoryBlock in enumerate(self.__memory):
            if memoryBlock[3] == MemoryBlockState.UNASSIGNED and memoryBlock[2] >= pcb.getRam():
                return True, index  # memoryBlockNum = index
        return False, -1

    def insertPCB(self, pcb: PCB, memoryBlockNum: int):
        # 将进程插入内存之前需要先调用checkAssignable()检查是否可分配空间
        partition = self.__memory[memoryBlockNum]
        pcb_ram = pcb.getRam()
        pcb_id = pcb.getPID()
        self.__readyList.append(pcb_id)
        pcb.setState(PCBState.ACTIVE_READY)
        if partition[2] == pcb_ram:
            # 内存长度正好相等
            partition[0] = pcb_id
            partition[3] = MemoryBlockState.ASSIGNED
        else:
            self.__memory.insert(memoryBlockNum + 1,
                                 [-2, partition[1] + pcb_ram, partition[2] - pcb_ram, MemoryBlockState.UNASSIGNED])
            partition[0] = pcb_id
            partition[2] = pcb_ram
            partition[3] = MemoryBlockState.ASSIGNED

    def checkProcessable(self, pcb_queue: PCBQueue, processor: Processor):
        if len(self.__readyList) > 0:
            # 内存中有进程
            for l in processor.getProcessorPCBList():
                for pid in l:
                    # 处理机中有独立进程，或前驱已经结束的同步进程
                    pcb = pcb_queue.getPCBByPID(pid)
                    if pcb.getProperty() == Property.INDEPENDENT:
                        return True  # 独立进程
                    else:
                        # 同步进程
                        precursorList = pcb.getPrecursor()
                        preExitList = [pcb_queue.getPCBByPID(i).getState() == PCBState.EXIT for i in precursorList]
                        if sum(preExitList) == len(preExitList):
                            return True  # preExitList中全部为True，前驱进程全部完成
        return False

    def process(self, pcb_queue: PCBQueue, processor: Processor):
        # 处理机运行程序
        processor.process(pcb_queue)
        # 在Processor.process()后执行，用于清除内存中已经结束的进程，并合并未分配内存空间
        PCBToRemoveList = []
        for partition in self.__memory:
            pid = partition[0]
            if pid >= 0 and pcb_queue.getPCBByPID(pid).getState() == PCBState.EXIT:  # 如果内存中存在结束进程
                PCBToRemoveList.append(pid)
        if PCBToRemoveList:
            for pid in PCBToRemoveList:
                self.removePCB(pcb_queue.getPCBByPID(pid), processor)

    def removePCB(self, pcb: PCB, processor: Processor):
        # 从处理机中移除PCB
        isRemoved = processor.removePCB(pcb)
        # 从内存中移除PCB
        memoryBlockNum = 0
        pid = pcb.getPID()
        for index, value in enumerate(self.__memory):
            if value[0] == pid:
                memoryBlockNum = index
        self.__readyList.remove(pid)
        self.__memory[memoryBlockNum][0] = -2
        self.__memory[memoryBlockNum][3] = MemoryBlockState.UNASSIGNED
        self.__mergeMemory()

    def __mergeMemory(self):
        # 合并未分配的内存空间
        flag = False
        memoryBlockToMergeList = []  # 记录要合并的第二块及其后内存块的位置
        for index, value in enumerate(self.__memory):
            pid = value[0]
            if pid == -2:  # 检测到未分配的内存空间（-2）
                if not flag:  # 第一次检测到未分配的内存空间（-2）
                    flag = True
                else:  # 不是第一次检测到未分配的内存空间（-2），即有连续的未分配空间
                    memoryBlockToMergeList.append(index)
            if pid != -2:  # 检测到已分配的内存空间（!=-2）
                flag = False
        if memoryBlockToMergeList:
            beginMemoryBlockNum = memoryBlockToMergeList[0] - 1  # 要合并的第一个内存块的位置
            for partition in memoryBlockToMergeList[::-1]:
                memoryBlockToMerge = self.__memory.pop(partition)  # 倒序pop
                self.__memory[beginMemoryBlockNum][2] += memoryBlockToMerge[2]

    def dispatchProcessor(self, pcb_queue: PCBQueue, processor: Processor):
        # 对内存空间中（处于就绪队列中）的进程按抢占式优先权调度算法安排调度
        # 首先将独立进程，以及前驱已经完成的同步进程按优先权降序加入列表
        # 然后将同步进程按优先权降序加入列表
        # 最后为进程分配处理机
        freePIDDic = {}  # 独立进程，以及前驱已经完成的同步进程
        syncPIDDic = {}  # 同步进程
        for i in self.__readyList:
            pcb = pcb_queue.getPCBByPID(i)
            # 每个处理机中的进程状态设置为PCBState.ACTIVE_READY
            pcb.setState(PCBState.ACTIVE_READY)
            if pcb.getProperty() == Property.INDEPENDENT:
                # 独立进程
                freePIDDic[i] = pcb.getPriority()
            else:
                precursorList = pcb.getPrecursor()
                preExitList = [pcb_queue.getPCBByPID(i).getState() == PCBState.EXIT for i in precursorList]
                if sum(preExitList) == len(preExitList):
                    # preExitList中全部为True，前驱进程全部完成
                    freePIDDic[i] = pcb.getPriority()
                else:
                    # 同步进程
                    syncPIDDic[i] = pcb.getPriority()
        sortedFreeList = sorted(freePIDDic.items(), key=lambda item: item[1], reverse=True)  # 按优先权降序排序
        sortedSyncList = sorted(syncPIDDic.items(), key=lambda item: item[1], reverse=True)  # 按优先权降序排序
        sortedList = sortedFreeList + sortedSyncList
        processor.dispatchPCB(sortedList)
