from flask import Flask, request
from proc import *
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/os/get_PCB_list', methods=['GET'])
def getPCBList():
    print('所有进程：' + str(pcbQueue.toJson()))
    return pcbQueue.toJson(), 200


@app.route('/os/create_PCB', methods=['POST'])
def createPCB():
    # 创建进程
    form = request.get_json(silent=True)
    print('创建进程表单：' + str(form))
    pid = pcbQueue.getNextPID()
    time = int(form['form']['time'])
    ram = int(form['form']['ram'])
    priority = int(form['form']['priority'])
    prop_str = form['form']['property']
    precursor_list = form['form']['precursor']

    if prop_str == '0':
        prop = Property.INDEPENDENT
    elif prop_str == '1':
        prop = Property.SYNCHRONIZED
    else:
        return {'errMsg': 'PCB进程创建错误！'}, 400
    precursor = set(precursor_list)
    new_pcb = PCB(pid, time, ram, priority, prop, precursor)
    print('创建进程：' + str(new_pcb.toJson()))
    pcbQueue.append(new_pcb)
    print('所有进程：' + str(pcbQueue.toJson()))

    # 检查内存空间，主存空间分配，决定进程状态（后备队列/进入内存）
    isAssignable, partitionNum = mainMemory.checkAssignable(new_pcb)
    if isAssignable:
        mainMemory.insertPCB(new_pcb, partitionNum)
        # 分配内存和处理机
        mainMemory.dispatchProcessor(pcbQueue, processor)
    else:
        backupQueue.appendPCB(new_pcb)
    return pcbQueue.toJson(), 200


@app.route('/os/get_main_memory')
def getMainMemory():
    print('内存：'+str(mainMemory.toJson()))
    return mainMemory.toJson(), 200


@app.route('/os/get_processors')
def getProcessors():
    print('处理机：' + str(processor.toJson()))
    return processor.toJson(), 200


@app.route('/os/get_backup_queue')
def getBackupQueue():
    print('后备队列：' + str(backupQueue.toJson()))
    return backupQueue.toJson(), 200


@app.route('/os/get_hanging_queue')
def getHangingQueue():
    print('挂起队列：' + str(hangingQueue.toJson()))
    return hangingQueue.toJson(), 200


@app.route('/os/hang_PCB_list', methods=['POST'])
def hangPCB():
    form = request.get_json(silent=True)
    print('挂起进程表单：' + str(form))
    hangPCBList = form['form']
    for pid in hangPCBList:
        pcb = pcbQueue.getPCBByPID(pid)
        if pcb.getState() in [PCBState.ACTIVE_READY, PCBState.RUNNING]:
            # 内存中
            mainMemory.removePCB(pcb, processor)
            mainMemory.dispatchProcessor(pcbQueue, processor)  # 分配内存和处理机
        if pcb.getState() == PCBState.STATIC_READY:
            # 后备队列中
            backupQueue.removePCB(pcb)
        hangingQueue.appendPCB(pcb)
    print('所有进程：' + str(pcbQueue.toJson()))
    return pcbQueue.toJson(), 200


@app.route('/os/unhang_PCB_list', methods=['POST'])
def unhangPCB():
    form = request.get_json(silent=True)
    print('解挂进程表单：' + str(form))
    unhangPCBList = form['form']
    for pid in unhangPCBList:
        pcb = pcbQueue.getPCBByPID(pid)
        assert pcb.getState() == PCBState.SUSPENDING, '非挂起进程无法解挂'
        hangingQueue.removePCB(pcb)
        # 检查内存空间，主存空间分配，决定进程状态（后备队列/进入内存）
        isAssignable, partitionNum = mainMemory.checkAssignable(pcb)
        if isAssignable:
            mainMemory.insertPCB(pcb, partitionNum)
            # 分配内存和处理机
            mainMemory.dispatchProcessor(pcbQueue, processor)
        else:
            backupQueue.appendPCB(pcb)
    print('所有进程：' + str(pcbQueue.toJson()))
    return pcbQueue.toJson(), 200


@app.route('/os/run')
def run():
    isProcessable = mainMemory.checkProcessable(pcbQueue, processor)
    if not isProcessable:
        return {'errMsg': '无可运行程序，请手动检查！'}, 400
    mainMemory.process(pcbQueue, processor)
    pid = backupQueue.autoRemove(pcbQueue, mainMemory, processor)
    print('所有进程：' + str(pcbQueue.toJson()))
    return pcbQueue.toJson(), 200


if __name__ == '__main__':
    app.run(debug=True)
