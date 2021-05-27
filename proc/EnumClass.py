from enum import Enum


class PCBState(Enum):
    CREATE = 0
    ACTIVE_READY = 1
    STATIC_READY = 2
    RUNNING = 3
    SUSPENDING = 4
    EXIT = 5


class Property(Enum):
    INDEPENDENT = 0
    SYNCHRONIZED = 1


class MemoryBlockState(Enum):
    UNASSIGNED = 0
    ASSIGNED = 1
    OS_ASSIGNED = 2


PCBStateDict = {
    'CREATE': '进程创建',
    'ACTIVE_READY': '活动就绪',
    'STATIC_READY': '静止就绪',
    'RUNNING': '进程运行',
    'SUSPENDING': '进程挂起',
    'EXIT': '进程结束'
}

PropertyDict = {
    'INDEPENDENT': '独立进程',
    'SYNCHRONIZED': '同步进程'
}

MemoryBlockStateDict = {
    'UNASSIGNED': '未分配',
    'ASSIGNED': '已分配',
    'OS_ASSIGNED': '操作系统',
}