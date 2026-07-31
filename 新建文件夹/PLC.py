#from gettext import npgettext
#from nis import match
import sys
import socket
import threading
import cv2

from numpy import True_, signedinteger
import config
import time
import sys, os
import datetime
import inspect
import ctypes
import random
import config
import traceback
import math
import queue
from struct import pack , unpack
import numpy as np

class PLCConnect(threading.Thread):
    def __init__(self,st_host,n_port):
        threading.Thread.__init__(self, name="PLCConnect")
        self.lock = threading.Lock()
        self.st_host = st_host
        self.n_port = n_port
        # 队列
        self.rqueue = queue.Queue()
        self.squeue = queue.Queue()
        self.sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 线程
        self.sck.bind(('192.168.3.150', 501))
        self.sck.listen(5)
        self.connection,self.address = self.sck.accept()
        self.sendthread = threading.Thread(target=self.Sender, name='PLCSender', daemon=True)
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
                        self.rqueue.put(msg)#将消息存入接收队列
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
            #if sum == 0:
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

    #识别二维码
    def jiazhua(self,state):
        config.number += 1
        if config.number >= 60000:
            config.number = 0
        buffer = pack("!HHHHHHH", 0x00AC, 0x0000, 0x0500, config.number, 0x82,4,state) #打包 大端模式
        # 合成报文
        data = []
        for a in buffer:
            data.append(a)
        #异或和校验
        sumA = 0
        for b in data:
            sumA ^= b
        data.append(sumA)
        data.append(0)
        msg = bytes(data)
        self.squeue.put(msg)
        config.log.logger.info("下发夹爪指令 ")
        while True:
            try:
                rdata = self.rqueue.get(timeout=2)
                config.log.logger.info(rdata)
            except:
                break
            # 比较功能码
            print(rdata)
            if msg[8:10] == rdata[8:10] :
                config.log.logger.info("收到PLC答复 ")
                  # ACK
            else:
                config.log.logger.info("下发夹爪指令 ")
               # self.rqueue.put(rdata)
                return False

            try:
                rdata = self.rqueue.get(timeout=5)
            except:
                break
            # 比较功能码
            print(rdata)
            if (rdata[8]<<8)+rdata[9] == 2:
                buffer = pack("!HHHHHHHHH", 0x00AC, 0x0000, 0x0500, config.number, 0x0002,6,1,2,3) #打包 大端模式
                data = []
                for a in buffer:
                   data.append(a)
                msg = bytes(data)
                self.squeue.put(msg)
                return True
            else:
                config.log.logger.info("下发夹爪指令 ")
              #  self.rqueue.put(rdata)
            return False

    #识别快速接头
    def Visual_KuaiSuJieTou(self):
        config.number += 1
        if config.number >= 60000:
            config.number = 0
        buffer = pack("!HHHHHH", 0x00AC, 0x0000, 0x0600, config.number, 0x84,1) #打包 大端模式
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
        config.log.logger.info("下发识别二维码指令 ")
        while True:
            try:
                rdata = self.rqueue.get(timeout=15)
            except:
                break
            # 比较功能码
            print(rdata)
            if msg[8:10] == rdata[8:10] and rdata[12] == 1:
                config.log.logger.info("收到视觉答复 ")
                  # ACK
            else:
                config.log.logger.info("重发识别二维码指令 ")
               # self.rqueue.put(rdata)
                return False

            try:
                rdata = self.rqueue.get(timeout=60)
            except:
                break
            # 比较功能码
            print(rdata)
            if (rdata[8]<<8)+rdata[9] == 2 and rdata[12] == 5:
                config.POS_barcode['y'] = ((rdata[14]<<8)+rdata[15])
                config.POS_barcode['z'] = ((rdata[16]<<8)+rdata[17])
                config.POS_barcode['x'] = ((rdata[18]<<8)+rdata[19])
                config.POS_barcode['v'] = ((rdata[20]<<8)+rdata[21])
                config.POS_barcode['w'] = ((rdata[22]<<8)+rdata[23])
                config.POS_barcode['u'] = ((rdata[24]<<8)+rdata[25])
                if(config.POS_barcode['x']>=0x8000):
                    config.POS_barcode['x'] -= 0x10000
                if(config.POS_barcode['y']>=0x8000):
                    config.POS_barcode['y'] -= 0x10000
                if(config.POS_barcode['z']>=0x8000):
                    config.POS_barcode['z'] -= 0x10000
                if(config.POS_barcode['u']>=0x8000):
                    config.POS_barcode['u'] -= 0x10000
                if(config.POS_barcode['v']>=0x8000):
                    config.POS_barcode['v'] -= 0x10000
                if(config.POS_barcode['w']>=0x8000):
                    config.POS_barcode['w'] -= 0x10000
                config.log.logger.info("收到二维码坐标 ")
                return True
            else:
                config.log.logger.info("重发识别二维码指令 ")
              #  self.rqueue.put(rdata)
            return False

    #识别水带接头
    def Visual_ShuDai(self):
        config.number += 1
        if config.number >= 60000:
            config.number = 0
        buffer = pack("!HHHHHH", 0x00AC, 0x0000, 0x0600, config.number, 0x83,1) #打包 大端模式
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
        config.log.logger.info("下发识别二维码指令 ")
        while True:
            try:
                rdata = self.rqueue.get(timeout=15)
            except:
                break
            # 比较功能码
            print(rdata)
            if msg[8:10] == rdata[8:10] and rdata[12] == 1:
                config.log.logger.info("收到视觉答复 ")
                  # ACK
            else:
                config.log.logger.info("重发识别二维码指令 ")
               # self.rqueue.put(rdata)
                return False

            try:
                rdata = self.rqueue.get(timeout=60)
            except:
                break
            # 比较功能码
            print(rdata)
            if (rdata[8]<<8)+rdata[9] == 2 and rdata[12] == 4:
                config.POS_barcode['y'] = ((rdata[14]<<8)+rdata[15])
                config.POS_barcode['x'] = ((rdata[16]<<8)+rdata[17])
                config.POS_barcode['z'] = ((rdata[18]<<8)+rdata[19])
                config.POS_barcode['u'] = ((rdata[20]<<8)+rdata[21])
                if(config.POS_barcode['x']>=0x8000):
                    config.POS_barcode['x'] -= 0x10000
                if(config.POS_barcode['y']>=0x8000):
                    config.POS_barcode['y'] -= 0x10000
                if(config.POS_barcode['z']>=0x8000):
                    config.POS_barcode['z'] -= 0x10000
                if(config.POS_barcode['u']>=0x8000):
                    config.POS_barcode['u'] -= 0x10000
                config.log.logger.info("收到二维码坐标 ")
                return True
            else:
                config.log.logger.info("重发识别二维码指令 ")
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

