from proc.EnumClass import *
from proc.Config import *
from proc.PCB import *
from proc.PCBQueue import *
from proc.Processor import *
from proc.MainMemory import *
from proc.BackupQueue import *
from proc.HangingQueue import *

pcbQueue = PCBQueue()
processor = Processor()
mainMemory = MainMemory()
backupQueue = BackupQueue()
hangingQueue = HangingQueue()
