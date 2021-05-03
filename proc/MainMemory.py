from proc.Config import Memory, OSMemory
from proc.EnumClass import PartitionState
from proc.PCB import PCB


class MainMemory:
    def __init__(self):
        self.__readyList = []
        # 分区表[[起址, 长度, 状态], ...]
        self.__memory = [[0, OSMemory, PartitionState.OS_ASSIGNED],
                         [OSMemory, Memory - OSMemory, PartitionState.UNASSIGNED]]  # 按起始地址进行升序排序

    def checkAssignable(self, pcb: PCB):
        # 检测是否可分配空间，同时返回可分配内存空间的起始地址
        for index, partition in enumerate(self.__memory):
            if partition[2] == PartitionState.UNASSIGNED and partition[1] >= pcb.getRam():
                return True, index
        return False, -1

    def insertPCB(self, pcb: PCB, partitionNum: int):
        partition = self.__memory[partitionNum]
        pcb_ram = pcb.getRam()
        self.__readyList.append(pcb.getPID())
        if partition[1] == pcb_ram:
            # 内存长度正好相等
            partition[2] = PartitionState.ASSIGNED
        else:
            self.__memory.append([partition[0] + pcb_ram, partition[1] - pcb_ram, PartitionState.UNASSIGNED])
            partition[1] = pcb_ram
            partition[2] = PartitionState.ASSIGNED
