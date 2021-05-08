from proc.EnumClass import PCBState, Property


class PCB:
    def __init__(self, pid: int, time: int, ram: int, priority: int, prop: Property, precursor: set,
                 state=PCBState.CREATE):
        assert pid >= 0 and time >= 0 and ram >= 0 and priority >= 0, 'PCB属性错误！'
        self.__pid = pid  # 进程号
        self.__time = time  # 所需时间
        self.__ram = ram  # 所需内存空间
        self.__priority = priority  # 优先权
        self.__state = state  # 进程状态：创建、活动就绪（内存中）、静止就绪（外存中）、执行、挂起、终止
        self.__prop = prop  # 进程属性：独立进程、同步进程
        self.__precursor = precursor  # 前驱进程PID
        self.__successor = set()  # 后继进程PID集合

    def getPID(self):
        return self.__pid

    def getTime(self):
        return self.__time

    def getRam(self):
        return self.__ram

    def getState(self):
        return self.__state

    def getPriority(self):
        return self.__priority

    def getProperty(self):
        return self.__prop

    def getPrecursor(self):
        return self.__precursor

    def setState(self, new_state: PCBState):
        self.__state = new_state

    def addSuccessor(self, pid: int):
        self.__successor.add(pid)

    # def addSuccessor(self, successor: set):
    #     for i in successor:
    #         self.__successor.add(i)

    def process(self):
        self.__time -= 1
        if self.__time == 0:
            self.__state = PCBState.EXIT
            return True  # 进程结束
        else:
            self.__state = PCBState.RUNNING
            return False
