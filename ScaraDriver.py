
import socket
import threading
import config
import time

import traceback

import queue
import json
import re
#机械臂通信收发类
class SCARAConnect(threading.Thread):
    def __init__(self,st_host,n_port):
        threading.Thread.__init__(self, name="SCARAConnect")
        self.lock = threading.Lock()
        self.st_host = st_host
        self.n_port = n_port
        # 发送接收数据队列
        self.rqueueGetPostion = queue.Queue()
        self.rqueueModifyOutput = queue.Queue()
        self.rqueueRewriteDataList = queue.Queue()
        self.rqueueSetSpeed = queue.Queue()
        self.rqueueStartButton = queue.Queue()
        self.rqueueStopButton = queue.Queue()
        self.rqueueActionStop = queue.Queue()
        self.rqueueModifyCounter = queue.Queue()

        self.squeue = queue.Queue()
        self.sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 发送线程
        self.sendthread = threading.Thread(target=self.Sender, name='SCARASender', daemon=True)
        self.state = threading.Condition()
        self.sendPaused = True

    # 主线程，接收解析
    def run(self):
        # 启动发送线程
        self.sendthread.start()
        self.doConnect()
        while True:
            try:
                # wait recv
                data = self.sck.recv(1024)#接收数据
                if len(data) :
                # if isinstance(data, bytes) and len(data) > 0:
                    config.rTimeErr = 0
                    config.recvTag = 1
                    self.ParsePackage(data)
                    
            except OSError:
                traceback.print_exc()
                self.threadPause()
                time.sleep(2)
                config.log.logger.info('SCARA connect error, doing connect in 2s ....')
                self.sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.doConnect()
            except Exception as e:
                config.log.logger.info('other error occur:{}'.format(str(e)))
                traceback.print_exc()
                self.threadPause()
                time.sleep(4)
                if self.sck._closed:
                    self.sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.doConnect()
                #if self.sck._closed:
                    

    # 重连
    def doConnect(self):
        while True:
            try:
                #self.sck.settimeout(1)
                self.sck.connect((self.st_host, self.n_port))
                self.threadResume()
                time.sleep(1)
                config.log.logger.info('connect to SCARA {}:{}'.format(self.st_host,self.n_port))
                break
            except ConnectionRefusedError:
                config.log.logger.info('SCARA refused or not started, reconnect to SCARA in 3s ...')
                time.sleep(3)

            except Exception as e:
                traceback.print_exc()
                config.log.logger.info('do connect error:{}'.format(str(e)))
                time.sleep(5)

    # 恢复线程运行
    def threadResume(self):
        with self.state:
            self.sendPaused = False
            self.state.notify()

    # 超时判断
    def TimeErr(self):
        if config.rTimeErr >= 3:
            self.threadPause()
            time.sleep(4)
            config.rTimeErr = 0
            self.sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.doConnect()

    # 接收数据解析
    def ParsePackage(self, data):
        # 数据转成json格式
        pattern = r'({.*?})'
        r1 = re.findall(pattern,str(data))
        for i in r1:
            packages = json.loads(i)
            if "cmdReply" in packages:
                #设置中间变量M0
                if packages["cmdReply"] == ['modifyOutput', 'ok']:
                    self.rqueueModifyOutput.put(packages)
                #下发坐标
                if packages["cmdReply"] == ['rewriteDataList', 'ok']:
                    self.rqueueRewriteDataList.put(packages)
                #设置速度
                if packages["cmdReply"] == ['modifyGSPD', 'ok']:
                    self.rqueueSetSpeed.put(packages)
                #启动机械臂
                if packages["cmdReply"] == ['startButton', 'ok']:
                    self.rqueueStartButton.put(packages)
                #停止机械臂
                if packages["cmdReply"] == ['stopButton', 'ok']:
                    self.rqueueStopButton.put(packages)
                #停止机械臂2
                if packages["cmdReply"] == ['actionStop', 'ok']:
                    self.rqueueActionStop.put(packages)
                if packages["cmdReply"] == ['modifyCounter', 'ok']:
                    self.rqueueModifyCounter.put(packages)

            elif "cmdType" in packages:
                # 获取当前点位
                if packages["cmdType"] == 'query':
                    self.rqueueGetPostion.put(packages)


    # 发送线程
    def Sender(self):
        while True:
            self.TimeErr()
            # wait for resume

            with self.state:
                if self.sendPaused:
                    self.state.wait()
            try:
                msg = self.squeue.get()
                if 'queryAddr' not in str(msg):
                    config.log.logger.info("send:{}".format(msg))                 
                self.sck.send(msg)#发送数据
                # 限流
                for j in range(0,3):
                    for i in range(0,100):                    
                        if config.recvTag == 1:
                            break;
                        time.sleep(0.01) 
                    if config.recvTag == 1:
                            break;  
                    else:
                        if 'queryAddr' not in str(msg):
                            config.log.logger.info("send:{}".format(msg))   
                        self.sck.send(msg)

                if config.recvTag ==1:                   
                    time.sleep(0.1)   
                config.recvTag = 0    
            except OSError:
                traceback.print_exc()
                self.threadPause()
            except Exception as e:
                config.log.logger.info('other error occur:{}'.format(str(e)))
                traceback.print_exc()
                self.threadPause()

    # 挂起线程
    def threadPause(self):
        with self.state:
            self.sendPaused = True


    #获取当前坐标和计数器信息
    def GetPostion(self):
         #{"dsID":"HCRemoteMonitor","cmdType":"query","queryAddr":["world-0","world-1","world-2","world-3","world-4","world-5","counter-0"]}
         msg = b"{\"dsID\":\"HCRemoteMonitor\",\"cmdType\":\"query\",\"queryAddr\":[\"world-0\",\"world-1\",\"world-2\",\"world-3\",\"world-4\",\"world-5\",\"counter-0\"]}"
         self.rqueueGetPostion.queue.clear()
         self.squeue.put(msg)
         
         while True:
            try:
                # wait Response config.r_time
                data = self.rqueueGetPostion.get(timeout=config.rTime)
            except Exception as e:
                config.log.logger.info('GetPostion error:{}'.format(str(e)))
                config.rTimeErr += 1
                break
            # 检查内容
            #{'dsID':'HCRemoteMonitor','cmdType':'queryEcho','queryData':['-1200','-1650','500','-90','0','-90','???[0][T:20][C:0]']}
            #config.log.logger.info('recv data:{}'.format(data))
            config.currentPos['x'] = float(data['queryData'][0])
            config.currentPos['y'] = float(data['queryData'][1])
            config.currentPos['z'] = float(data['queryData'][2])
            config.currentPos['u'] = float(data['queryData'][3])
            config.currentPos['v'] = float(data['queryData'][4])
            config.currentPos['w'] = float(data['queryData'][5])
            config.currentPos['ID'] = float(data['queryData'][6][2])
            return True
         return False

    #设置中间变量M0
    def modifyOutput(self,register):
        #{"dsID":"HCRemoteMonitor","cmdType":"command","cmdData":["modifyOutput","0","0","0"]}
        msg = "{\"dsID\":\"HCRemoteMonitor\",\"cmdType\":\"command\",\"cmdData\":[\"modifyOutput\",\"" + str(register["borad"]) + "\",\"" + str(register["point"]) + "\",\"" + str(register["funtion"])+"\"]}"
        self.rqueueModifyOutput.queue.clear()
        self.squeue.put(bytes(msg, encoding='utf8'))
        
        while True:
            try:
                # wait Response config.r_time
                data = self.rqueueModifyOutput.get(timeout=config.rTime)
            except Exception as e:
                config.log.logger.info('modifyOutput error:{}'.format(str(e)))
                config.rTimeErr += 1
                break
            # 检查内容
            #{'dsID':'HCRemoteMonitor','cmdType':'cmdEcho','cmdReply':['modifyOutput','ok']}
            config.log.logger.info('recv data:{}'.format(data))
            return True
        return False

    #下发坐标
    def rewriteDataList(self,pos):
        #{"dsID":"HCRemoteMonitor","cmdType":"command","cmdData":["rewriteDataList","0","6","0","0000","0000","0000","0000","0000","0000"]}
        msg = "{\"dsID\":\"HCRemoteMonitor\",\"cmdType\":\"command\",\"cmdData\":[\"rewriteDataList\",\"" + str(pos["addr"]) + "\",\"6\",\"0\""
        msg += ",\"" + str(pos['x'] * 1000) + "\""
        msg += ",\"" + str(pos['y'] * 1000) + "\""
        msg += ",\"" + str(pos['z'] * 1000) + "\""
        msg += ",\"" + str(pos['u'] * 1000) + "\""
        msg += ",\"" + str(pos['v'] * 1000) + "\""
        msg += ",\"" + str(pos['w'] * 1000) + "\""
        msg += "]}"
        self.rqueueRewriteDataList.queue.clear()
        self.squeue.put(bytes(msg, encoding='utf8'))

        while True:
            try:
                # wait Response config.r_time
                data = self.rqueueRewriteDataList.get(timeout=config.rTime)
            except Exception as e:
                config.log.logger.info('rewriteDataList error:{}'.format(str(e)))
                config.rTimeErr += 1
                break
            # 检查内容
            #{'dsID':'HCRemoteMonitor','cmdType':'cmdEcho','cmdReply':['rewriteDataList','ok']}
            config.log.logger.info('recv data:{}'.format(data))
            return True
        return False
    def rewriteDataListStr(self,link):
        #{"dsID":"HCRemoteMonitor","cmdType":"command","cmdData":["rewriteDataList","0","6","0","0000","0000","0000","0000","0000","0000"]}
        msg = "{\"dsID\":\"HCRemoteMonitor\",\"cmdType\":\"command\",\"cmdData\":[\"rewriteDataList\",\"" + str(link["addr"]) + "\",\"" + str(link["poslen"]) + "\",\"0"
        msg += str(link['pos'])
        msg += "\"]}"
        self.rqueueRewriteDataList.queue.clear()
        self.squeue.put(bytes(msg, encoding='utf8'))

        while True:
            try:
                # wait Response config.r_time
                data = self.rqueueRewriteDataList.get(timeout=config.rTime)
            except Exception as e:
                config.log.logger.info('rewriteDataListStr error:{}'.format(str(e)))
                config.rTimeErr += 1
                break
            # 检查内容
            #{'dsID':'HCRemoteMonitor','cmdType':'cmdEcho','cmdReply':['rewriteDataList','ok']}
            config.log.logger.info('recv data:{}'.format(data))
            return True
        return False
    #设置速度
    def setSpeed(self,link):
        #{"dsID":"HCRemoteMonitor","cmdType":"command","cmdData":["modifyGSPD","100"]}
        msg = "{\"dsID\":\"HCRemoteMonitor\",\"cmdType\":\"command\",\"cmdData\":[\"modifyGSPD\",\"" +  str(link["speed"])  + "\"]}"
        self.rqueueSetSpeed.queue.clear()
        self.squeue.put(bytes(msg, encoding='utf8'))
        while True:
            try:
                # wait Response config.r_time
                data = self.rqueueSetSpeed.get(timeout=config.rTime)
            except Exception as e:
                config.log.logger.info('setSpeed error:{}'.format(str(e)))
                config.rTimeErr += 1
                break
            # 检查内容
            #{'dsID':'HCRemoteMonitor','cmdType':'cmdEcho','cmdReply':['modifyGSPD','ok']}
            config.log.logger.info('recv data:{}'.format(data))
            return True
        return False

    #启动机械臂
    def startButton(self):
        #{"dsID":"HCRemoteMonitor","cmdType":"command","cmdData":["startButton"]}
        msg = b"{\"dsID\":\"HCRemoteMonitor\",\"cmdType\":\"command\",\"cmdData\":[\"startButton\"]}"
        self.rqueueStartButton.queue.clear()
        self.squeue.put(msg)
        while True:
            try:
                # wait Response config.r_time
                data = self.rqueueStartButton.get(timeout=config.rTime)
            except Exception as e:
                config.log.logger.info('startButton error:{}'.format(str(e)))
                config.rTimeErr += 1
                break
            # 检查内容
            #{'dsID':'HCRemoteMonitor','cmdType':'cmdEcho','cmdReply':['startButton','ok']}
            config.log.logger.info('recv data:{}'.format(data))
            return True
        return False

    #停止机械臂
    def stopButton(self):
        #{"dsID":"HCRemoteMonitor","cmdType":"command","cmdData":["stopButton"]}
        msg = b"{\"dsID\":\"HCRemoteMonitor\",\"cmdType\":\"command\",\"cmdData\":[\"stopButton\"]}"
        self.rqueueStopButton.queue.clear()
        self.squeue.put(msg)
        while True:
            try:
                # wait Response config.r_time
                data = self.rqueueStopButton.get(timeout=config.rTime)
            except Exception as e:
                config.log.logger.info('stopButton error:{}'.format(str(e)))
                config.rTimeErr += 1
                break
            # 检查内容
            #{'dsID':'HCRemoteMonitor','cmdType':'cmdEcho','cmdReply':['stopButton','ok']}
            config.log.logger.info('recv data:{}'.format(data))
            return True
        return False
     #停止机械臂

    def modifyCounter(self,counter):
        #{"dsID":"HCRemoteMonitor","cmdType":"command","cmdData":["modifyOutput","0","0","0"]}
    #    msg = "{\"dsID\":\"HCRemoteMonitor\",\"cmdType\":\"command\",\"cmdData\":[\"modifyOutput\",\"counter-" + str(counter['number']) + "\",\"" + str(counter['value']) + "\",\"-1\"]}"
        msg = "{\"dsID\":\"HCRemoteMonitor\",\"cmdType\":\"command\",\"cmdData\":[\"modifyCounter\",\"counter-"+ str(counter['number']) + "\",\"" + str(counter['value']) + "\",\"-1\"]}"
        self.rqueueModifyCounter.queue.clear()
        self.squeue.put(bytes(msg, encoding='utf8'))
        
        while True:
            try:
                # wait Response config.r_time
                data = self.rqueueModifyCounter.get(timeout=config.rTime)
            except Exception as e:
                config.log.logger.info('modifyOutput error:{}'.format(str(e)))
                config.rTimeErr += 1
                break
            # 检查内容
            #{'dsID':'HCRemoteMonitor','cmdType':'cmdEcho','cmdReply':['modifyOutput','ok']}
            config.log.logger.info('recv data:{}'.format(data))
            return True
        return False