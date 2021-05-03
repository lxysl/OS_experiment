from proc.EnumClass import PCBState, Property


class PCB:
    def __init__(self, pid: int, time: int, ram: int, priority: int, prop: Property, precursor: set,
                 state=PCBState.CREATE):
        assert pid >= 0 and time >= 0 and ram >= 0 and priority >= 0, 'PCB属性错误！'
        self.__pid = pid
        self.__time = time
        self.__ram = ram
        self.__priority = priority
        self.__state = state
        self.__prop = prop
        self.__precursor = precursor
        self.__successor = set()

    def getPID(self):
        return self.__pid

    def getRam(self):
        return self.__ram

    def getState(self):
        return self.__state

    def getPriority(self):
        return self.__priority

    def getProperty(self):
        return self.__priority

    def getPrecursor(self):
        return self.__precursor

    def addSuccessor(self, successor: set):
        for i in successor:
            self.__successor.add(i)

    def setState(self, new_state: PCBState):
        self.__state = new_state

    def process(self):
        self.__time -= 1
        if self.__time == 0:
            self.__state = PCBState.EXIT
            return True  # 进程结束
        return False
