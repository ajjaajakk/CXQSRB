from array import typecodes
import socket
from struct import pack
import threading
from tkinter import Button
from typing import Counter, Type

import config
import time
import traceback
import queue
import json
import re
import sys
from datetime import datetime

#RCS通信收发类
class RCSConnect(threading.Thread):
    def __init__(self,st_host,n_port,count):
        threading.Thread.__init__(self, name="RCSConnect")
        self.lock = threading.Lock()
        self.st_host = st_host
        self.n_port = n_port
        self.count = count
        self.sender = "UNB"
        self.senderID = "1#"
        self.recipient = "RCS"
        self.recipientID = "1#"
        self.equipmentName = ""
        self.equipmentCode = ""
        self.softwareVersion = ""
        self.date = ""
        self.function = ""
        self.businessList = ""
        self.heartbeatCycle = 3
        self.exceptionReportingCycle = 3
        self.calibrationCycle=72
        self.currentBusinessList = []
        self.palletInformation = []
        self.buffInformation = []
        self.CurrentStatus = "Idle"

        # 发送接收数据队列    
        self.feedbackResponseQueue = queue.Queue()#反馈队列
        self.abnormalResponseQueue = queue.Queue()#异常队列
        self.registrationlResponseQueue = queue.Queue()#注册队列
        self.reportProgressResponseQueue = queue.Queue()#进度上报

        self.unpackingSpoolQueue = queue.Queue()  
        self.E_StopQueue = queue.Queue() 
        self.continueQueue = queue.Queue()
        self.unboxQueue = queue.Queue()   
        self.unpackingCartonsQueue = queue.Queue()  
        self.palletizingGreyFabricQueue = queue.Queue()
        self.hangingYarnQueue = queue.Queue()
        self.calibrationQueue = queue.Queue()
        self.squeue = queue.Queue()
        self.sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.NewspaperCollection = []
        self.NewspaperCollection.append({'type':"heartbeat",'msg':"",'button':True,'lastTime': datetime.now(),'cycle':self.heartbeatCycle})
        self.NewspaperCollection.append({'type':"abnormal",'msg':"",'button':False,'lastTime': datetime.now(),'cycle':self.exceptionReportingCycle})
        self.NewspaperCollection.append({'type':"registrationl",'msg':"",'button':False,'lastTime': datetime.now(),'cycle':self.exceptionReportingCycle})
        self.NewspaperCollection.append({'type':"reportProgress",'msg':"",'button':False,'lastTime': datetime.now(),'cycle':self.exceptionReportingCycle})
        self.NewspaperCollection.append({'type':"feedback",'msg':"",'button':False,'lastTime': datetime.now(),'cycle':self.exceptionReportingCycle})
        self.NewspaperCollection.append({'type':"continueFeedback",'msg':"",'button':False,'lastTime': datetime.now(),'cycle':self.exceptionReportingCycle})
        self.NewspaperCollection.append({'type':"E_StopFeedback",'msg':"",'button':False,'lastTime': datetime.now(),'cycle':self.exceptionReportingCycle})
        self.NewspaperCollection.append({'type':"calibrationFeedback",'msg':"",'button':False,'lastTime': datetime.now(),'cycle':self.exceptionReportingCycle})
        self.NewspaperCollection.append({'type':"selfCheckFeedback",'msg':"",'button':False,'lastTime': datetime.now(),'cycle':self.exceptionReportingCycle})
        # 发送线程
        self.sendthread = threading.Thread(target=self.Sender, name='RCSSender', daemon=True)
        self.Reportingthread = threading.Thread(target=self.Reporting, name='RCSReporting', daemon=True)
        self.state = threading.Condition()
        self.sendPaused = True
        self.rTimeErr = 0
    # 主线程，接收解析
    def run(self):
        # 启动发送线程
        self.sendthread.start()
        self.Reportingthread.start()
        self.doConnect()
        while True:
            try:
                data = self.sck.recv(1024)#接收数据
                if len(data) :
                    self.rTimeErr = 0
                    self.ParsePackage(data)
                    config.log.logger.info("recvice:{}".format(data))
            except OSError:
                traceback.print_exc()
                self.threadPause()
                time.sleep(2)
                config.log.logger.info('RCS connect error, doing connect in 2s ....')
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
                    
    # 重连
    def doConnect(self):
        while True:
            try: 
                #self.sck.settimeout(1)
                self.sck.connect((self.st_host, self.n_port))
                self.threadResume()
                time.sleep(1)
                config.log.logger.info('connect to RCS {}:{}'.format(self.st_host,self.n_port))
                break
            except ConnectionRefusedError:
                config.log.logger.info('RCS refused or not started, reconnect to RCS in 3s ...')
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
        if self.rTimeErr >= 3:
            self.threadPause()
            time.sleep(4)
            self.rTimeErr = 0
            self.sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.doConnect()

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
                packages = json.loads(msg)
                if packages['type'] != "heartbeat":
                    config.log.logger.info("send:{}".format(msg))                 
                self.sck.send(msg)#发送数据
                # 限流                   
                time.sleep(0.01)       
            except OSError:
                traceback.print_exc()
                self.threadPause()
            except Exception as e:
                config.log.logger.info('other error occur:{}'.format(str(e)))
                traceback.print_exc()
                self.threadPause()
    def Reporting(self):
        while True:
            try:
                if self.sendPaused == False:
                    self.periodicReporting()      
                time.sleep(0.01)       
            except Exception as e:
                config.log.logger.info('other error occur:{}'.format(str(e)))
    # 挂起线程
    def threadPause(self):
        with self.state:
            self.sendPaused = True

    def changeAttribute(self,type_Value,button):
        for item in self.NewspaperCollection:
            if item['type'] == type_Value:
                item['button'] = button
    
    def periodicReporting(self):
        current_time = datetime.now()
        formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
        for item in self.NewspaperCollection:
            ts = current_time - item['lastTime']
            if item['button'] == True and ts.seconds >=item['cycle']:
                item['lastTime'] = current_time
                if item['type'] == "heartbeat": 
                    item['msg'] = self.Heartbeat()
                item['msg']['sendTime'] = formatted_time
                json_data = json.dumps(item['msg'])
                self.squeue.put(bytes(json_data, encoding='utf8'))

    # 接收数据解析
    def ParsePackage(self, data):
        current_time = datetime.now()
        formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
        try:
            packages = json.loads(data)
            if packages['recipient'] == self.sender and packages['recipientID'] == self.senderID :
                if 'type'in packages and 'typeID'in packages:     
                    if packages['type'] == 'response': 
                        if packages['typeID'] ==  "6":
                            self.registrationlResponseQueue.put(packages)
                        if packages['typeID'] ==  "7":
                            self.reportProgressResponseQueue.put(packages) 
                        if packages['typeID'] ==  "10":
                            self.abnormalResponseQueue.put(packages)
                        if packages['typeID'] ==  "11" and packages['result'] ==  "true":
                            #self.feedbackResponseQueue.put(packages)
                            self.changeAttribute("feedback",False)
                    else:
                        if packages['type'] == 'cancelTask': 
                            self.cancelTaskQueue.put(packages)
                        if packages['type'] == 'taskStart':
                            if self.CurrentStatus == "Idle": 
                                self.CurrentStatus = "Busy"
                                self.unpackingSpoolQueue.put(packages)
                                self.Response(packages['typeID'], packages['number'],"true", [], formatted_time)
                            else:
                                self.Response(packages['typeID'], packages['number'],"true", [1], formatted_time)
                        if packages['type'] == 'E-Stop': 
                            self.E_StopQueue.put(packages)
                        if packages['type'] == 'continue':  
                            self.continueQueue.put(packages) 
                        if packages['type'] == 'unbox':  
                            if self.CurrentStatus == "Idle": 
                                self.CurrentStatus = "Busy"
                                self.unboxQueue.put(packages)
                                self.Response(packages['typeID'], packages['number'],"true", [], formatted_time)
                            else:
                                self.Response(packages['typeID'], packages['number'],"true", [1], formatted_time)
                            
                        if packages['type'] == 'unpackingCartons': 
                            if self.CurrentStatus == "Idle": 
                                self.CurrentStatus = "Busy"
                                self.unpackingCartonsQueue.put(packages)
                                self.Response(packages['typeID'], packages['number'],"true", [], formatted_time)
                            else:
                                self.Response(packages['typeID'], packages['number'],"true", [1], formatted_time)                            
                            
                        if packages['type'] == 'palletizingGreyFabric':  
                            if self.CurrentStatus == "Idle": 
                                self.CurrentStatus = "Busy"
                                self.palletizingGreyFabricQueue.put(packages)
                                self.Response(packages['typeID'], packages['number'],"true", [], formatted_time)
                            else:
                                self.Response(packages['typeID'], packages['number'],"true", [1], formatted_time)   
                            
                        if packages['type'] == 'calibration':  
                            self.calibrationQueue.put(packages) 
            else :  
                return False
        except json.JSONDecodeError:
            print("字符串不是有效的JSON格式")

    #注册信息上报data_json构造
    def get_REG_data(self):
       get_REG_data_Templates = {
            "name":self.equipmentName,
            "equipmentCode": self.equipmentCode,
            "softwareVersion":self.softwareVersion,
            "date":self.date,
            "funtion":self.function,
            "businessList":self.businessList,
            "heartbeatCycle":self.heartbeatCycle,
            "exceptionReportingCycle":self.exceptionReportingCycle,
            "calibrationCycle":self.calibrationCycle,
            "currentBusinessList":self.currentBusinessList,
            "palletInformation":self.palletInformation,
            "buffInformation":self.buffInformation,
            }
       return get_REG_data_Templates
    #进度上报data构造函数
    def get_REP_data(progress_Value,describe_Value,buffInformation_Value):
        get_REP_data_Templates = {
            "progress": progress_Value,
            "describe":describe_Value,
            "buffInformation":buffInformation_Value
            }
    #校准data构造
    def get_CAL_data(result_Value,codeList_Value):
        get_CAL_data_Templates = {
            "result": result_Value,
            "codeList":codeList_Value,
            }
        return get_CAL_data_Templates
    #自检反馈data构造
    def get_SCF_data(result_Value,codeLit_Value):
        get_SCF_data_Templates = {
               "result": result_Value,
               "codeList":codeLit_Value
            }
        return get_SCF_data_Templates
    #拆大版任务反馈data构造
    def get_UPSF_data(result_Value,codeList_Value,count_Value,palletInformation):
        get_UPSF_data_Templates = {
            "result": result_Value,
            "codeList":codeList_Value,
            "count":count_Value,
            "palletInformation":palletInformation
        }
        return get_UPSF_data_Templates

    #停止反馈data构造
    def get_ESPF_data(result_Value,codeList_Value):
        get_ESPF_data_Templates = { 
            "result": result_Value,
            "codeList":codeList_Value
            }
        return get_ESPF_data_Templates
    #继续当前任务反馈
    def get_CONF_data(result_Value,codeList_Value):
        get_CONF_data_Templates = { 
            "result": result_Value,
            "codeList":codeList_Value
            }
        return get_CONF_data_Templates
    #拆箱取纱任务反馈data构造
    def get_UNBF_data(result_Value,codeList_Value,count_Value,palletInformation_Value):
        get_UNBF_data_Templates = { 
            "result": result_Value,
            "codeList":codeList_Value,
            "count":count_Value,
            "palletInformation":palletInformation_Value
    }
        return get_UNBF_data_Templates
    #纸箱拆垛任务反馈data构造
    def get_UNCF_data(result_Value,codeList_Value,count_Value,palletInformation_Value):
        get_UNCF_data_Templates = { 
            "result": result_Value,
            "codeList":codeList_Value,
            "count":count_Value,
            "palletInformation":palletInformation_Value
    }
        return get_UNCF_data_Templates
    #胚布码垛反馈data构造(PGFF)
    def get_PGFF_data(result_Value,codeList_Value,count_Value,palletInformation_Value,buffInformation_Value):
        get_PGFF_data_Templates = { 
            "result": result_Value,
            "codeList":codeList_Value,
            "count": count_Value,
            "palletInformation":palletInformation_Value,
            "buffInformation":buffInformation_Value
            }
        return get_PGFF_data_Templates

    #上位机响应RCS
    def Response(self,typeID_Value, number_Value, result_Value, codeList_Value, sendTime_Value):   
        Templates = {  
            "sender": self.sender,  
            "senderID": self.senderID,  
            "recipient": self.recipient,  
            "recipientID": self.recipientID,  
            "type": "response",
            "typeID": typeID_Value,
            "number": number_Value,  
            "result": result_Value,  
            "codeList": codeList_Value,  
            "sendTime": sendTime_Value  
        }
        json_data = json.dumps(Templates)
        self.squeue.put(bytes(json_data, encoding='utf8'))
        return Templates  
    #任务反馈
    def Task_feedback(self,type_Value,typeID_Value,number_Value,data_Value,sendTime_Value):
        Templates={
            "sender":self.sender,
            "senderID":self.senderID,
            "recipient":self.recipient,
            "recipientID":self.recipientID,
            "type":type_Value,
            "typeID":typeID_Value,
            "number":number_Value,
            "data":data_Value,
            "sendTime":sendTime_Value
            }
        return Templates
    #心跳
    def Heartbeat(self):
        current_time = datetime.now()
        formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
        Templates={
            "sender":self.sender,
            "senderID":self.senderID,
            "recipient":self.recipient,
            "recipientID":self.recipientID,
            "type":"heartbeat",
            "typeID":"5",
            "currentStatus":self.CurrentStatus,
            "sendTime":formatted_time
            }
        return Templates

    #注册信息上报
    def Registration(self,type_in_number,data):
        current_time = datetime.now()
        formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
        Templates={
            "sender":self.sender,
            "senderID":self.senderID,
            "recipient":self.recipient,
            "recipientID":self.recipientID,
            "type":type,
            "number":self.Serial_number_structure(type_in_number),
            "data":"***",
            "sendTime":formatted_time
            }
        return Templates

    #进度上报
    def reportProgress(self,type_Value,typeID_Value,data):
        current_time = datetime.now()
        formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
        Templates={
            "sender":self.sender,
            "senderID":self.senderID,
            "recipient":self.recipient,
            "recipientID":self.recipientID,
            "type":type_Value,
            "typeID":"reportProgress",
            "number":typeID_Value,
            "data":data,
            "sendTime":formatted_time
            }
        json_data = json.dumps(Templates)
        self.squeue.put(bytes(json_data, encoding='utf8'))
        return

    #异常上报
    def abnormal(self,type_Value,typeID_Value,number_Value,data):
        current_time = datetime.now()
        formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
        Templates={
            "sender":self.sender,
            "senderID":self.senderID,
            "recipient":self.recipient,
            "recipientID":self.recipientID,
            "type":type_Value,
            "typeID":typeID_Value,
            "number":number_Value,
            "data":data,
            "sendTime":formatted_time
            }
        return Templates


    #拆大版任务反馈
    def unpackingSpoolFeedback(self,link):
        number_Value =  link['number']
        data_Value = link['data']
        current_time = datetime.now()
        formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
        msg = self.Task_feedback(link['type'],link['typeID'],number_Value,data_Value,formatted_time)
        json_data = json.dumps(msg)

        for item in self.NewspaperCollection:
            if item['type'] == "feedback": 
                item['msg'] = msg
                item['button'] = True
                item['lastTime'] = current_time
                json_data = json.dumps(item['msg'])
                self.squeue.put(bytes(json_data, encoding='utf8'))
        self.unpackingSpoolQueue.queue.clear()
        return True

     #任务反馈
    def feedback(self,link):
        number_Value =  link['number']
        data_Value = link['data']
        current_time = datetime.now()
        formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
        msg = self.Task_feedback(link['type'],link['typeID'],number_Value,data_Value,formatted_time)
        json_data = json.dumps(msg)

        for item in self.NewspaperCollection:
            if item['type'] == link['buttonName']: 
                item['msg'] = msg
                item['button'] = True
                item['lastTime'] = current_time
                json_data = json.dumps(item['msg'])
                self.squeue.put(bytes(json_data, encoding='utf8'))
        self.unpackingSpoolQueue.queue.clear()            
        return True

           

     #构造可以自增长的流水号函数
    def increment(self):  
        count_int = int(self.count)
        count_int += 1  
        count_int %= 1000000  
        # 将整数转换回六位数的字符串形式  
        count = format(count_int, '06d')
        return count  
     #业务流水构造
    def Serial_number_structure(self,type_Value):
         current_time = datetime.now()
         formatted_time = current_time.strftime('%Y%m%d')
         Temp="VGR_"+type_Value+"_"+formatted_time+"_"+self.increment()
         return Temp
     
    def get_palletInformation(self,location_Value, number_Value,fution_Value,state_Value,count_Value,Lock_Value):
         Temp={
             'location' :location_Value,
             'number':number_Value,
             'fuction':fution_Value,
             'state':state_Value,
             'count':count_Value,
             'Lock':Lock_Value
             }
         return Temp
     #buffInformation的构造函数
    def get_buffInformation(self,location_Value, number_Value,fution_Value,stateList_Value,countList_Value,Lock_Value):
         Temp={
             'location' :location_Value,
             'number':number_Value,
             'fuction':fution_Value,
             'stateList':stateList_Value,
             'countList':countList_Value,
             'Lock':Lock_Value
             }
         return Temp   
    






