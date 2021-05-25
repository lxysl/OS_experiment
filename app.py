from flask import Flask, render_template, request, jsonify
from proc import *
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/os')
def index():
    return render_template('index.html')


@app.route('/os/get_PCB_list', methods=['GET'])
def getPCBList():
    print(pcbQueue.toJson())
    return pcbQueue.toJson(), 200


@app.route('/os/create_PCB', methods=['POST'])
def createPCB():
    # 创建进程
    form = request.get_json(silent=True)
    print(form)
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
        return {'errMsg': 'PCB进程创建错误'}, 400
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
        mainMemory.dispatchProcessor(pcbQueue, processer)
    else:
        backupQueue.appendPCB(new_pcb)
    return pcbQueue.toJson(), 200


@app.route('/os/get_main_memory')
def getMainMemory():
    return mainMemory.toJson(), 200


@app.route('/os/run')
def run():
    pass


if __name__ == '__main__':
    app.run(debug=True)
