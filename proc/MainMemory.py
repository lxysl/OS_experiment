from proc.Config import Memory, OSMemory
from proc.EnumClass import PCBState, MemoryBlockState
from proc.PCB import PCB
from proc.PCBQueue import PCBQueue
from proc.Processer import Processor


class MainMemory:
    def __init__(self):
        self.__readyList = []
        # 有序分区表[[起址, 长度, 状态], ...]，按起始地址进行升序排序
        self.__memory = [[0, OSMemory, MemoryBlockState.OS_ASSIGNED],
                         [OSMemory, Memory - OSMemory, MemoryBlockState.UNASSIGNED]]
        self.__memoryPCB = [-1, -2]  # 内存分区表中对应存储的PID，OS对应的内存表项用-1表示，未分配内存表项用-2表示

    def checkAssignable(self, pcb: PCB):
        # 检测是否可分配空间，同时返回可分配内存空间的起始地址
        for index, memoryBlock in enumerate(self.__memory):
            if memoryBlock[2] == MemoryBlockState.UNASSIGNED and memoryBlock[1] >= pcb.getRam():
                return True, index  # memoryBlockNum = index
        return False, -1

    def insertPCB(self, pcb: PCB, memoryBlockNum: int):
        # 将进程插入内存之前需要先调用checkAssignable()检查是否可分配空间
        partition = self.__memory[memoryBlockNum]
        pcb_ram = pcb.getRam()
        pcb_id = pcb.getPID()
        self.__readyList.append(pcb_id)
        if partition[1] == pcb_ram:
            # 内存长度正好相等
            partition[2] = MemoryBlockState.ASSIGNED
            self.__memoryPCB[memoryBlockNum] = pcb_id
        else:
            self.__memory.insert(memoryBlockNum,
                                 [partition[0] + pcb_ram, partition[1] - pcb_ram, MemoryBlockState.UNASSIGNED])
            self.__memoryPCB.insert(memoryBlockNum, pcb_id)
            partition[1] = pcb_ram
            partition[2] = MemoryBlockState.ASSIGNED

    def process(self, pcb_queue: PCBQueue):
        # 在Processor.process()后执行，用于清除内存中已经结束的进程，并合并未分配内存空间
        PCBToRemoveList = []
        for i in self.__memoryPCB:
            if i >= 0 and pcb_queue.getPCBByPID(i).getState() == PCBState.EXIT:  # 如果内存中存在结束进程
                PCBToRemoveList.append(i)
        if PCBToRemoveList:
            for i in PCBToRemoveList:
                self.removePCB(pcb_queue.getPCBByPID(i))

    def removePCB(self, pcb: PCB):
        # 从内存中移除PCB
        memoryBlockNum = 0
        pid = pcb.getPID()
        for index, value in enumerate(self.__memoryPCB):
            if value == pid:
                memoryBlockNum = index
        self.__readyList.remove(pid)
        self.__memoryPCB[memoryBlockNum] = -2
        self.__memory[memoryBlockNum][2] = MemoryBlockState.UNASSIGNED
        self.__mergeMemory()

    def __mergeMemory(self):
        # 合并未分配的内存空间
        flag = False
        memoryBlockToMergeList = []  # 记录要合并的第二块及其后内存块的位置
        for index, value in enumerate(self.__memoryPCB):
            if value == -2:  # 检测到未分配的内存空间（-2）
                if not flag:  # 第一次检测到未分配的内存空间（-2）
                    flag = True
                else:  # 不是第一次检测到未分配的内存空间（-2），即有连续的未分配空间
                    memoryBlockToMergeList.append(index)
            if value != -2:  # 检测到已分配的内存空间（!=-2）
                flag = False
        if memoryBlockToMergeList:
            beginMemoryBlockNum = memoryBlockToMergeList[0] - 1  # 要合并的第一个内存块的位置
            for i in memoryBlockToMergeList:
                memoryBlockToMerge = self.__memory.pop(i)
                self.__memory[beginMemoryBlockNum][1] += memoryBlockToMerge[1]

    def dispatchProcessor(self, pcb_queue: PCBQueue, processor: Processor):
        # 对内存空间中（处于就绪队列中）的进程按抢占式优先权调度算法安排调度
        PIDDic = {i: pcb_queue.getPCBByPID(i).getPriority() for i in self.__readyList}
        sortedList = sorted(PIDDic.items(), key=lambda item: item[1], reverse=True)  # 按优先权降序排序
        processor.dispatchPCB(sortedList)
