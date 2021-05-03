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


class PartitionState(Enum):
    UNASSIGNED = 0
    ASSIGNED = 1
    OS_ASSIGNED = 2
