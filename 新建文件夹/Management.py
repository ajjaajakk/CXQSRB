#from gettext import npgettext
#from nis import match

import socket
import threading

import config
import time

import config
import traceback
import math
import queue
from struct import pack , unpack
import numpy as np

class ManagementConnect(threading.Thread):
    def __init__(self,st_host,n_port):
        threading.Thread.__init__(self, name="ManagementConnect")
        self.lock = threading.Lock()
        self.st_host = st_host
        self.n_port = n_port
        # 队列
        self.r0x81queue = queue.Queue()
        self.r0x82queue = queue.Queue()
        self.r0x83queue = queue.Queue()
        self.r0x84queue = queue.Queue()
        self.r0x85queue = queue.Queue()
        self.r0x86queue = queue.Queue()
        self.r0x87queue = queue.Queue()
        self.r0x88queue = queue.Queue()
        self.r0x89queue = queue.Queue()
        self.r0x8Aqueue = queue.Queue()
        self.r0x8Bqueue = queue.Queue()
        self.r0x8Cqueue = queue.Queue()
        self.r0x8Dqueue = queue.Queue()
        self.r0x8Equeue = queue.Queue()
        self.r0x02_01queue = queue.Queue()
        self.r0x02_02queue = queue.Queue()
        self.r0x02_03queue = queue.Queue()
        self.r0x02_04queue = queue.Queue()
        self.r0x02_05queue = queue.Queue()
        self.r0x02_06queue = queue.Queue()
        self.r0x02_07queue = queue.Queue()
        self.r0x02_08queue = queue.Queue()
        self.r0x02_09queue = queue.Queue()
        self.r0x02_0Aqueue = queue.Queue()
        self.r0x02_0Bqueue = queue.Queue()
        self.r0x02_0Cqueue = queue.Queue()
        self.r0x02_0Dqueue = queue.Queue()
        self.r0x02_0Equeue = queue.Queue()
        self.squeue = queue.Queue()
        self.sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 线程
        self.sck.bind(('127.0.0.1', 3001))
        self.sck.listen(5)
        self.connection,self.address = self.sck.accept()
        self.sendthread = threading.Thread(target=self.Sender, name='ManagementSender', daemon=True)
        self.state = threading.Condition()
        self.sendPaused = True

    def run(self):
        # 启动
        self.sendthread.start()               
        while True:
            try:
                # wait recv
                self.connection.settimeout(300)
                data = self.connection.recv(1024)
                if len(data) :
                    packages = self.ParsePackage(data)#数据包解析
                    for msg in packages:
                        if  msg[8:10] != 0x00:
                            self.PutMsg(msg)
                       # self.rqueue.put(msg)#将消息存入接收队列
            except OSError:
                traceback.print_exc()
                self.threadPause()
                self.connection.close()
                time.sleep(1)
                self.connection,self.address = self.sck.accept()  
            except Exception as e:
                print('other error occur:{}'.format(str(e)))
                traceback.print_exc()
                self.threadPause()
                self.connection.close()
                time.sleep(1)
                self.connection,self.address = self.sck.accept()  
    def PutMsg(self,msg):
        if (msg[8]<<8)+msg[9] == 0x81:
            self.r0x81queue.put(msg)
        if (msg[8]<<8)+msg[9] == 0x82:
            self.r0x82queue.put(msg)
        if (msg[8]<<8)+msg[9] == 0x83:
            self.r0x83queue.put(msg)
        if (msg[8]<<8)+msg[9] == 0x84:
            self.r0x84queue.put(msg)
        if (msg[8]<<8)+msg[9] == 0x85:
            self.r0x85queue.put(msg)
        if (msg[8]<<8)+msg[9] == 0x86:
            self.r0x86queue.put(msg)
        if (msg[8]<<8)+msg[9] == 0x87:
            self.r0x87queue.put(msg)
        if (msg[8]<<8)+msg[9] == 0x88:
            self.r0x88queue.put(msg)
        if (msg[8]<<8)+msg[9] == 0x89:
            self.r0x89queue.put(msg)
        if (msg[8]<<8)+msg[9] == 0x8A:
            self.r0x8Aqueue.put(msg)
        if (msg[8]<<8)+msg[9] == 0x8B:
            self.r0x8Bqueue.put(msg)
        if (msg[8]<<8)+msg[9] == 0x8C:
            self.r0x8Cqueue.put(msg)
        if (msg[8]<<8)+msg[9] == 0x8D:
            self.r0x8Dqueue.put(msg)
        if (msg[8]<<8)+msg[9] == 0x8E:
            self.r0x8Equeue.put(msg)
        if (msg[8]<<8)+msg[9] == 0x02:
            if msg[12] == 0x01:
                self.r0x02_01queue.put(msg)
            if msg[12] == 0x02:
                self.r0x02_02queue.put(msg)
            if msg[12] == 0x03:
                self.r0x02_03queue.put(msg)
            if msg[12] == 0x04:
                self.r0x02_04queue.put(msg)
            if msg[12] == 0x05:
                self.r0x02_05queue.put(msg)
            if msg[12] == 0x06:
                self.r0x02_06queue.put(msg)
            if msg[12] == 0x07:
                self.r0x02_07queue.put(msg)
            if msg[12] == 0x08:
                self.r0x02_08queue.put(msg)
            if msg[12] == 0x09:
                self.r0x02_09queue.put(msg)
            if msg[12] == 0x0A:
                self.r0x02_0Aqueue.put(msg)
            if msg[12] == 0x0B:
                self.r0x02_0Bqueue.put(msg)
            if msg[12] == 0x0C:
                self.r0x02_0Cqueue.put(msg)
            if msg[12] == 0x0D:
                self.r0x02_0Dqueue.put(msg)
            if msg[12] == 0x0E:
                self.r0x02_0Equeue.put(msg)
    # 接收数据解析
    def ParsePackage(self, data):
        packages = []
        while len(data):
            start = data.find(b'\xAC')
            if start < 0:
                break
            if start > 0:
                data = data[start-1:]
            length = int.from_bytes(data[10:12], byteorder='big', signed=False)
            msg = data[:12+length]
            sum = 0
            print(msg)
            for b in msg:
                sum ^= b
            if sum == 0:
                packages.append(msg)
            data = data[12+length:]
        return packages

    def Sender(self):
        while True:
            try:
                msg = self.squeue.get()
                self.connection.send(msg)
            except OSError:
                traceback.print_exc()
                self.threadPause()
            except Exception as e:
                print('other error occur:{}'.format(str(e)))
                traceback.print_exc()
                self.threadPause()

    def threadResume(self):
        with self.state:
            self.sendPaused = False
            self.state.notify()

    def threadPause(self):
        with self.state:
            self.sendPaused = True

    def SyntheticMessage(self,buf):
        # 合成报文
        data = []
        for a in buf:
            data.append(a)
        #异或和校验
        sumA = 0
        for b in data:
            sumA ^= b
        data.append(sumA)
        msg = bytes(data)
        return msg

    def Heartbeat(self):
        config.number += 1
        if config.number >= 60000:
            config.number = 0
        buffer = pack("!HHHHHH", 0x00AC, 0x0600, 0, config.number, 0, 1) #打包 大端模式
        # 合成报文
        data = []
        for a in buffer:
            data.append(a)
        #异或和校验
        sumA = 0
        for b in data:
            sumA ^= b
        data.append(sumA)
        msg = bytes(data)
        self.squeue.put(msg)



    #识别箱体
    def Visual_box_postion(self):
        config.number += 1
        if config.number >= 60000:
            config.number = 0
        buffer = pack("!HHHHHH", 0x00AC, 0x0000, 0x0600, config.number, 0x82,1) #打包 大端模式
        msg = self.SyntheticMessage(buffer)
        self.r0x82queue.queue.clear()
        self.squeue.put(msg)
        config.log.logger.info("下发箱体识别指令 ")
        while True:
            try:
                rdata = self.r0x82queue.get(timeout=15)
                config.log.logger.info(rdata)
            except:
                break
            # 比较功能码
            print(rdata)
            if msg[8:10] == rdata[8:10] and rdata[12] == 1:
                Network,souse,targit,number,function,lenth,ack,orsum=unpack('!HHHHHHBB',rdata)
                config.log.logger.info("收到视觉答复 ")
                  # ACK
            else:
                config.log.logger.info("重发箱体识别指令 ")
               # self.rqueue.put(rdata)
                return False

            try:
                self.r0x02_02queue.queue.clear()
                rdata = self.r0x02_02queue.get(timeout=60)
            except:
                break
            # 比较功能码
            print(rdata)
            if (rdata[8]<<8)+rdata[9] == 2 and rdata[12] == 2:
                Network,souse,targit,number,function,lenth,addr,ack,num,pos1_x,pos1_y,pos1_z,pos2_x,pos2_y,pos2_z,pos3_x,pos3_y,pos3_z,pos4_x,pos4_y,pos4_z,orsum=unpack('!HHHHHHBBBhhhhhhhhhhhhB',rdata)
                if ack == 1:
                    config.box.append({'x': pos1_x/10,'y':pos1_y/10,'z':pos1_z/10})
                    config.box.append({'x': pos2_x/10,'y':pos2_y/10,'z':pos2_z/10})
                    config.box.append({'x': pos3_x/10,'y':pos3_y/10,'z':pos3_z/10})
                    config.box.append({'x': pos4_x/10,'y':pos4_y/10,'z':pos4_z/10})
                buffer = pack("!HHHHHHBB", 0x00AC, 0x0000, 0x0600, config.number, 0x02,3,0x02,0x01) #打包 大端模式
                msg = self.SyntheticMessage(buffer)
                self.squeue.put(msg)
                return True
            else:
                config.log.logger.info("重发识别箱体指令 ")
              #  self.rqueue.put(rdata)
            return False

    #识别缝隙
    def Visual_spindle_pos(self):
        config.number += 1
        if config.number >= 60000:
            config.number = 0
        buffer = pack("!HHHHHH", 0x00AC, 0x0000, 0x0600, config.number, 0x83,1) #打包 大端模式
        msg = self.SyntheticMessage(buffer)
        self.r0x83queue.queue.clear()
        self.squeue.put(msg)
        config.log.logger.info("下发缝隙识别指令 ")
        while True:
            try:
                rdata = self.r0x83queue.get(timeout=15)
                config.log.logger.info(rdata)
            except:
                break
            print(rdata)
            if msg[8:10] == rdata[8:10] and rdata[12] == 1:
                Network,souse,targit,number,function,lenth,ack,orsum=unpack('!HHHHHHBB',rdata)
                config.log.logger.info("收到视觉答复 ")
            else:
                config.log.logger.info("重发缝隙识别指令 ")
                return False

            try:
                self.r0x02_03queue.queue.clear()
                rdata = self.r0x02_03queue.get(timeout=60)
            except:
                break
            print(rdata)
            if (rdata[8]<<8)+rdata[9] == 2 and rdata[12] == 3:
                Network,souse,targit,number,function,lenth,addr,ack,num,pos1_x,pos1_y,pos1_z,pos2_x,pos2_y,pos2_z,orsum=unpack('!HHHHHHBBBhhhhhhB',rdata)
                if ack == 1:
                    config.line_box.append({'x': pos1_x/10,'y':pos1_y/10,'z':pos1_z/10})
                    config.line_box.append({'x': pos2_x/10,'y':pos2_y/10,'z':pos2_z/10})
                buffer = pack("!HHHHHHBB", 0x00AC, 0x0000, 0x0600, config.number, 0x02,3,0x03,0x01) #打包 大端模式
                msg = self.SyntheticMessage(buffer)
                return True
            else:
                config.log.logger.info("重发识别缝隙指令 ")
              #  self.rqueue.put(rdata)
            return False

        #识别缝隙偏移
    def Visual_spindle_pos2(self,link):
        config.number += 1
        if config.number >= 60000:
            config.number = 0
        buffer = pack("!HHHHHHB", 0x00AC, 0x0000, 0x0600, config.number, 0x84,2,link['dir']) #打包 大端模式
        msg = self.SyntheticMessage(buffer)
        self.r0x84queue.queue.clear()
        self.squeue.put(msg)
        config.log.logger.info("下发缝隙识别指令 ")
        while True:
            try:
                rdata = self.r0x84queue.get(timeout=15)
                config.log.logger.info(rdata)
            except:
                break
            print(rdata)
            if msg[8:10] == rdata[8:10] and rdata[12] == 1:
                Network,souse,targit,number,function,lenth,ack,orsum=unpack('!HHHHHHBB',rdata)
                config.log.logger.info("收到视觉答复 ")
            else:
                config.log.logger.info("重发缝隙识别指令 ")
                return False

            try:
                self.r0x02_04queue.queue.clear()
                rdata = self.r0x02_04queue.get(timeout=60)
            except:
                break
            print(rdata)
            if (rdata[8]<<8)+rdata[9] == 2 and rdata[12] == 4:
                unpackDate=unpack('!HHHHHHBBBBhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhB',rdata)
                if unpackDate[7] == 1:
                    config.circles = []
                    for i in range (0,20):
                        config.line_box.append({'x':unpackDate[10+3*i]/10,'y':unpackDate[11+3*i]/10,'z':unpackDate[12+3*i]/10,'angle':0,'code':unpackDate[9]})
                buffer = pack("!HHHHHHBB", 0x00AC, 0x0000, 0x0600, config.number, 0x02,3,0x04,0x01) #打包 大端模式
                msg = self.SyntheticMessage(buffer)
                return True
            else:
                config.log.logger.info("重发缝隙识别指令 ")
              #  self.rqueue.put(rdata)
            return False

        #识别全局纱锭
    def getAllSpindlePostion(self):
        config.number += 1
        if config.number >= 60000:
            config.number = 0
        buffer = pack("!HHHHHHHH", 0x00AC, 0x0000, 0x0600, config.number, 0x85,5,int(config.spindle_od),int(config.spindle_id)) #打包 大端模式
        msg = self.SyntheticMessage(buffer)
        self.r0x85queue.queue.clear()
        self.squeue.put(msg)
        config.log.logger.info("下发全局纱锭识别指令 ")
        while True:
            try:
                rdata = self.r0x85queue.get(timeout=15)
                config.log.logger.info(rdata)
            except:
                break
            print(rdata)
            if msg[8:10] == rdata[8:10] and rdata[12] == 1:
                Network,souse,targit,number,function,lenth,ack,orsum=unpack('!HHHHHHBB',rdata)
                config.log.logger.info("收到视觉答复 ")
            else:
                config.log.logger.info("重发全局纱锭识别指令 ")
                return False

            try:
                self.r0x02_05queue.queue.clear()
                rdata = self.r0x02_05queue.get(timeout=60)
            except:
                break
            print(rdata)
            if (rdata[8]<<8)+rdata[9] == 2 and rdata[12] == 5:
                #Network,souse,targit,number,function,lenth,addr,ack,num,num1,x1,y1,z1,x2,y2,z2,x3,y3,z3,x4,y4,z4,x5,y5,z5,x6,y6,z6,x7,y7,z7,x8,y8,z8,x9,y9,z9,x10,y10,z10,x11,y11,z11,x12,y12,z12,orsum=unpack('!HHHHHHBBBBhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhB',rdata)
                #if ack == 1:
                #    config.circles.append({'x': x1/10,'y':y1/10,'z':z1/10,'angle':0})
                #    config.circles.append({'x': x2/10,'y':y2/10,'z':z2/10,'angle':0})
                #    config.circles.append({'x': x3/10,'y':y3/10,'z':z3/10,'angle':0})
                #    config.circles.append({'x': x4/10,'y':y4/10,'z':z4/10,'angle':0})
                #    config.circles.append({'x': x5/10,'y':y5/10,'z':z5/10,'angle':0})
                #    config.circles.append({'x': x6/10,'y':y6/10,'z':z6/10,'angle':0})
                #    config.circles.append({'x': x7/10,'y':y7/10,'z':z7/10,'angle':0})
                #    config.circles.append({'x': x8/10,'y':y8/10,'z':z8/10,'angle':0})0
                #    config.circles.append({'x': x9/10,'y':y9/10,'z':z9/10,'angle':0})
                #    config.circles.append({'x': x10/10,'y':y10/10,'z':z10/10,'angle':0})
                #    config.circles.append({'x': x11/10,'y':y11/10,'z':z11/10,'angle':0})
                #    config.circles.append({'x': x12/10,'y':y12/10,'z':z12/10,'angle':0})
                unpackDate=unpack('!HHHHHHBBBBhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhB',rdata)
                if unpackDate[7] == 1:
                    config.circles = []
                    for i in range (0,unpackDate[9]):
                        config.circles.append({'x':unpackDate[10+3*i]/10,'y':unpackDate[11+3*i]/10,'z':unpackDate[12+3*i]/10,'angle':0})
                buffer = pack("!HHHHHHBB", 0x00AC, 0x0000, 0x0600, config.number, 0x02,3,0x05,0x01) #打包 大端模式
                msg = self.SyntheticMessage(buffer)
                return True
            else:
                config.log.logger.info("重发全局纱锭识别指令 ")
              #  self.rqueue.put(rdata)
            return False     
        #识别单个纱锭
    def getSingleSpindlePostion(self):
        config.number += 1
        if config.number >= 60000:
            config.number = 0
        buffer = pack("!HHHHHHHH", 0x00AC, 0x0000, 0x0600, config.number, 0x86,5,int(config.spindle_od),int(config.spindle_id)) #打包 大端模式
        msg = self.SyntheticMessage(buffer)
        self.r0x86queue.queue.clear()
        self.squeue.put(msg)
        config.log.logger.info("下发单个纱锭识别指令 ")
        while True:
            try:
                rdata = self.r0x86queue.get(timeout=15)
                config.log.logger.info(rdata)
            except:
                break
            print(rdata)
            if msg[8:10] == rdata[8:10] and rdata[12] == 1:
                Network,souse,targit,number,function,lenth,ack,orsum=unpack('!HHHHHHBB',rdata)
                config.log.logger.info("收到视觉答复 ")
            else:
                config.log.logger.info("重发全局纱锭识别指令 ")
                return False

            try:
                self.r0x02_06queue.queue.clear()
                rdata = self.r0x02_06queue.get(timeout=60)
            except:
                break
            print(rdata)
            if (rdata[8]<<8)+rdata[9] == 2 and rdata[12] == 6:
                Network,souse,targit,number,function,lenth,addr,ack,num,x1,y1,z1,orsum=unpack('!HHHHHHBBBhhhB',rdata)
                if ack == 1:
                    config.circle ={'x': x1/10,'y':y1/10,'z':z1/10}

                buffer = pack("!HHHHHHBB", 0x00AC, 0x0000, 0x0600, config.number, 0x02,3,0x06,0x01) #打包 大端模式
                msg = self.SyntheticMessage(buffer)
                return True
            else:
                config.log.logger.info("重发单个纱锭识别指令 ")
              #  self.rqueue.put(rdata)
            return False 
    def getPalletCenterPostion(self,link):#托盘中心识别
        config.number += 1
        if config.number >= 60000:
            config.number = 0
        buffer = pack("!HHHHHH", 0x00AC, 0x0000, 0x0600, config.number, 0x89,1) #打包 大端模式
        msg = self.SyntheticMessage(buffer)
        self.r0x89queue.queue.clear()
        self.squeue.put(msg)
        config.log.logger.info("下发托盘中心识别指令 ")
        while True:
            try:
                rdata = self.r0x89queue.get(timeout=15)
                config.log.logger.info(rdata)
            except:
                break
            print(rdata)
            if msg[8:10] == rdata[8:10] and rdata[12] == 1:
                Network,souse,targit,number,function,lenth,ack,orsum=unpack('!HHHHHHBB',rdata)
                config.log.logger.info("收到视觉答复 ")
            else:
                config.log.logger.info("重发托盘中心识别指令 ")
                return False

            try:
                self.r0x02_0Bqueue.queue.clear()
                rdata = self.r0x02_0Bqueue.get(timeout=60)
            except:
                break
            print(rdata)
            if (rdata[8]<<8)+rdata[9] == 2 and rdata[12] == 0x09:
                #Network,souse,targit,number,function,lenth,addr,ack,code,num,x1,y1,z1,x2,y2,z2,orsum=unpack('!HHHHHHBBBBhhhhhhB',rdata)
                unpackDate=unpack('!HHHHHHBBBhhhhB',rdata)
                if unpackDate[7] == 1:
                    config.palletcenter = {'x':unpackDate[10]/10,'y':unpackDate[11]/10,'z':unpackDate[12]/10,'w':unpackDate[13]/10}
                buffer = pack("!HHHHHHBB", 0x00AC, 0x0000, 0x0600, config.number, 0x02,3,0x09,0x01) #打包 大端模式
                msg = self.SyntheticMessage(buffer)
                return True
            else:
                config.log.logger.info("重发托盘中心识别指令")
              #  self.rqueue.put(rdata)
            return False  
    def getPutPostion(self,link):
        config.number += 1
        if config.number >= 60000:
            config.number = 0
        buffer = pack("!HHHHHHH", 0x00AC, 0x0000, 0x0600, config.number, 0x8B,3,int(config.spindle_od)) #打包 大端模式
        msg = self.SyntheticMessage(buffer)
        self.r0x8Bqueue.queue.clear()
        self.squeue.put(msg)
        config.log.logger.info("下发放置位置识别指令 ")
        while True:
            try:
                rdata = self.r0x8Bqueue.get(timeout=15)
                config.log.logger.info(rdata)
            except:
                break
            print(rdata)
            if msg[8:10] == rdata[8:10] and rdata[12] == 1:
                Network,souse,targit,number,function,lenth,ack,orsum=unpack('!HHHHHHBB',rdata)
                config.log.logger.info("收到视觉答复 ")
            else:
                config.log.logger.info("重发放置位置识别指令 ")
                return False
            try:
                self.r0x02_0Bqueue.queue.clear()
                rdata = self.r0x02_0Bqueue.get(timeout=60)
            except:
                break
            print(rdata)
            if (rdata[8]<<8)+rdata[9] == 2 and rdata[12] == 0x0B:
                #Network,souse,targit,number,function,lenth,addr,ack,code,num,x1,y1,z1,x2,y2,z2,orsum=unpack('!HHHHHHBBBBhhhhhhB',rdata)
                unpackDate=unpack('!HHHHHHBBBBhhhhhhhhhhhhhhhhhhB',rdata)
                if unpackDate[7] == 1:
                    config.putPos = []
                    for i in range (0,unpackDate[9]):
                        config.putPos.append(np.array([unpackDate[10+3*i]/10,unpackDate[11+3*i]/10,unpackDate[12+3*i]]/10))
                buffer = pack("!HHHHHHBB", 0x00AC, 0x0000, 0x0600, config.number, 0x02,3,0x0B,0x01) #打包 大端模式
                msg = self.SyntheticMessage(buffer)
                return True
            else:
                config.log.logger.info("重发放置位置识别指令")
              #  self.rqueue.put(rdata)
            return False   
        
    def getBoxLeafPostion(self,link):#识别2，3页坐标
        config.number += 1
        if config.number >= 60000:
            config.number = 0
        buffer = pack("!HHHHHHHHBB", 0x00AC, 0x0000, 0x0600, config.number, 0x8C,7,int(link['length']),int(link['width']),int(link['type1']),int(link['rule'])) #打包 大端模式
        msg = self.SyntheticMessage(buffer)
        self.r0x8Cqueue.queue.clear()
        self.squeue.put(msg)
        config.log.logger.info("下发翻页识别指令 ")
        while True:
            try:
                rdata = self.r0x8Cqueue.get(timeout=15)
                config.log.logger.info(rdata)
            except:
                break
            print(rdata)
            if msg[8:10] == rdata[8:10] and rdata[12] == 1:
                Network,souse,targit,number,function,lenth,ack,orsum=unpack('!HHHHHHBB',rdata)
                config.log.logger.info("收到视觉答复 ")
            else:
                config.log.logger.info("重发翻页识别指令 ")
                return False

            try:
                self.r0x02_0Cqueue.queue.clear()
                rdata = self.r0x02_0Cqueue.get(timeout=60)
            except:
                break
            print(rdata)
            if (rdata[8]<<8)+rdata[9] == 2 and rdata[12] == 0x0C and rdata[13] == 0x01:
                unpackDate=unpack('!HHHHHHBBBBBBBBBBBhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhB',rdata)
                #Network,souse,targit,number,function,lenth,addr,ack,code,num,notice1,notice2,notice3,notice4,x1,y1,z1,x2,y2,z2,x3,y3,z3,x4,y4,z4,orsum=unpack('!HHHHHHBBBBBBBBhhhhhhhhB',rdata)
                if rdata[14] == 0:
                    config.notice1 = unpackDate[13]
                    config.notice2 = unpackDate[14]
                    config.notice3 = unpackDate[15]
                    config.notice4 = unpackDate[16]
                    config.point = []
                    for i in range (0,4):
                        pointList = []
                        pointList.append(np.array([unpackDate[17+i*9]/10,unpackDate[18+i*9]/10,unpackDate[19+i*9]/10]))
                        pointList.append(np.array([unpackDate[20+i*9]/10,unpackDate[21+i*9]/10,unpackDate[22+i*9]/10]))
                        pointList.append(np.array([unpackDate[23+i*9]/10,unpackDate[24+i*9]/10,unpackDate[25+i*9]/10]))
                        config.point.append(pointList)

                    buffer = pack("!HHHHHHBB", 0x00AC, 0x0000, 0x0600, config.number, 0x02,3,0x0C,0x01) #打包 大端模式
                    msg = self.SyntheticMessage(buffer)
                    return True
                else:
                    config.log.logger.info("重发翻页识别指令")
                    return False   
            else:
                config.log.logger.info("重发翻页识别指令")
              #  self.rqueue.put(rdata)
            return False   
        
    def getGrabPostion(self,link):
        config.number += 1
        if config.number >= 60000:
            config.number = 0
        buffer = pack("!HHHHHHHH", 0x00AC, 0x0000, 0x0600, config.number, 0x8D,5,int(link['length']),int(link['width'])) #打包 大端模式
        msg = self.SyntheticMessage(buffer)
        self.r0x8Dqueue.queue.clear()
        self.squeue.put(msg)
        config.log.logger.info("下发抓箱识别指令 ")
        while True:
            try:
                rdata = self.r0x8Dqueue.get(timeout=15)
                config.log.logger.info(rdata)
            except:
                break
            print(rdata)
            if msg[8:10] == rdata[8:10] and rdata[12] == 1:
                Network,souse,targit,number,function,lenth,ack,orsum=unpack('!HHHHHHBB',rdata)
                config.log.logger.info("收到视觉答复 ")
            else:
                config.log.logger.info("重发抓箱识别指令 ")
                return False
            try:
                self.r0x02_0Dqueue.queue.clear()
                rdata = self.r0x02_0Dqueue.get(timeout=60)
            except:
                break
            print(rdata)
            if (rdata[8]<<8)+rdata[9] == 2 and rdata[12] == 0x0D:
                Network,souse,targit,number,function,lenth,addr,ack,code,x1,y1,z1,w1,orsum=unpack('!HHHHHHBBBhhhhB',rdata)
                if ack == 1:
                    config.grab = {'x': x1/10,'y':y1/10,'z':z1/10,'w':w1/10}

                buffer = pack("!HHHHHHBB", 0x00AC, 0x0000, 0x0600, config.number, 0x02,3,0x0D,0x01) #打包 大端模式
                msg = self.SyntheticMessage(buffer)
                return True
            else:
                config.log.logger.info("重发抓箱识别指令")
              #  self.rqueue.put(rdata)
            return False        

    def getBarcodePostion(self,link):
        config.number += 1
        if config.number >= 60000:
            config.number = 0
        buffer = pack("!HHHHHHHH", 0x00AC, 0x0000, 0x0600, config.number, 0x8E,5,int(link['ID']),int(link['length'])) #打包 大端模式
        msg = self.SyntheticMessage(buffer)
        self.r0x8Equeue.queue.clear()
        self.squeue.put(msg)
        config.log.logger.info("下发二维码识别指令 ")
        while True:
            try:
                rdata = self.r0x8Equeue.get(timeout=15)
                config.log.logger.info(rdata)
            except:
                break
            print(rdata)
            if msg[8:10] == rdata[8:10] and rdata[12] == 1:
                Network,souse,targit,number,function,lenth,ack,orsum=unpack('!HHHHHHBB',rdata)
                config.log.logger.info("收到视觉答复 ")
            else:
                config.log.logger.info("重发二维码识别指令 ")
                return False

            try:
                self.r0x02_0Equeue.queue.clear()
                rdata = self.r0x02_0Equeue.get(timeout=60)
            except:
                break
            print(rdata)
            if (rdata[8]<<8)+rdata[9] == 2 and rdata[12] == 0x0E:
                Network,souse,targit,number,function,lenth,addr,ack,code,x1,y1,z1,px,py,orsum=unpack('!HHHHHHBBBhhhhhB',rdata)
                if ack == 1:
                    config.POS_barcode = {'x': x1/10,'y':y1/10,'z':z1/10,'u':px,'v':py,'w':0}

                buffer = pack("!HHHHHHBB", 0x00AC, 0x0000, 0x0600, config.number, 0x02,3,0x0E,0x01) #打包 大端模式
                msg = self.SyntheticMessage(buffer)
                return True
            else:
                config.log.logger.info("重发二维码识别指令")
              #  self.rqueue.put(rdata)
            return False      
        
    def putVis(self):
        config.number += 1
        if config.number >= 60000:
            config.number = 0
        buffer = pack("!HHHHHH", 0x00AC, 0x0000, 0x0600, config.number, 0x8A,1) #打包 大端模式
        msg = self.SyntheticMessage(buffer)
        self.r0x8Aqueue.queue.clear()
        self.squeue.put(msg)
        config.log.logger.info("下发放置位置识别指令 ")
        while True:
            try:
                rdata = self.r0x8Aqueue.get(timeout=15)
                config.log.logger.info(rdata)
            except:
                break
            print(rdata)
            if msg[8:10] == rdata[8:10] and rdata[12] == 1:
                Network,souse,targit,number,function,lenth,ack,orsum=unpack('!HHHHHHBB',rdata)
                config.log.logger.info("收到视觉答复 ")
            else:
                config.log.logger.info("重发放置识别指令 ")
                return False

            try:
                self.r0x02_0Aqueue.queue.clear()
                rdata = self.r0x02_0Aqueue.get(timeout=60)
            except:
                break
            print(rdata)
            if (rdata[8]<<8)+rdata[9] == 2 and rdata[12] ==0X0A:
                Network,souse,targit,number,function,lenth,addr,ack,num,higcount,orsum=unpack('!HHHHHHBBBhB',rdata)
                if ack == 1:
                    config.hight = higcount

                buffer = pack("!HHHHHHBB", 0x00AC, 0x0000, 0x0600, config.number, 0x02,3,0x0A,0x01) #打包 大端模式
                msg = self.SyntheticMessage(buffer)
                return True
            else:
                config.log.logger.info("重发放置识别指令 ")
              #  self.rqueue.put(rdata)
            return False 
    def revolve(self,euler,vector):
        vector2 =vector.T
        u = euler['u'] / 180 * math.pi
        v = euler['v'] / 180 * math.pi
        w = euler['w'] / 180 * math.pi

        a = np.array([[1,0,0],[0,math.cos(u),-math.sin(u)],[0,math.sin(u),math.cos(u)]])
        b = np.array([[math.cos(v),0,math.sin(v)],[0,1,0],[-math.sin(v),0,math.cos(v)]])
        c = np.array([[math.cos(w),-math.sin(w),0],[math.sin(w),math.cos(w),0],[0,0,1]])

        d = np.dot(c, b)
        d = np.dot(d, a)
        e = d@vector2
     
        return e.T

