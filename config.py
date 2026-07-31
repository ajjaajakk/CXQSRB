
import yaml
import random
from Management import ManagementConnect
from ScaraDriver import *
from SetLink import *
import logging
from logging import handlers
import os
import time
from PLC import PLCConnect
from db import Database
from RCS import RCSConnect
import numpy as np
#import Visual
"""
函数名：sys_stats()  
系统运行状态机
"""
def sys_state():

    # 报文参数
    global number
    global Heartbeat
    global HeartTime
    global spindle_od
    global spindle_id
          
    spindle_od = 200
    spindle_id = 65

    number = random.randint(0,65535)       # 包号
    Heartbeat = True      # 发送心跳
    HeartTime = 0          # 心跳计数器
"""
函数名：get_yaml_load()
功能  加载yaml文件
"""
def get_yaml_load(filename):
    with open(filename,'r', encoding='utf-8') as fp:
        file_data = fp.read()
        fp.close()
        data = yaml.load(file_data, Loader=yaml.FullLoader)
        print(data)
        return data

"""
函数名：reparam()
功能  获取参数列表
"""
def reparam():
    global RCSServerHost, RCSServerPort
    global ServerHost, ServerPort
    global ScaraHost, ScaraPort
    global RobotStatus#机器人状态
    global HeartbeatCycle, DEBUG, CHECK_LIMIT, CUT_ORDER
    global speed#全局速度
    global SLOW_SPEED#搬运纸箱/纱锭的慢速

    try:
        params = get_yaml_load('params.yaml')
        DEBUG = params['DEBUG']
        CHECK_LIMIT = params['CHECK_LIMIT']
        CUT_ORDER = params.get('CUT_ORDER', 'right_first')  # 默认先右后左
        RCSServerHost = params['RcstcpServer']['host']#RCSIP
        RCSServerPort = params['RcstcpServer']['port']#RCS端口


        ServerHost = params['tcpServer']['host']#上位机IP
        ServerPort = params['tcpServer']['port']#上位机端口
        HeartbeatCycle = params['tcpServer']['heartbeat']

        ScaraHost = params['SCARAServer']['host']#机械臂IP
        ScaraPort = params['SCARAServer']['port']#机械臂端口
        speed = params['SCARAServer']['speed']#全局速度
        SLOW_SPEED = params['SCARAServer']['SLOW_SPEED']#搬运纸箱/纱锭的慢速
        Palletiz = [0,0,0,0,0,0,0,0,0]
        RobotStatus = [params['Information']['softwareversion']]#软件版本
        RobotStatus.append(0)
        RobotStatus.append(0)
        RobotStatus.append(0)
        RobotStatus.append(0)
        RobotStatus.append(Palletiz)
        RobotStatus.append(0)
        print(RobotStatus)
        print(speed)
    except  Exception as e:
        print("读取参数失败，请检查配置文件" + str(e.args))

"""
函数名：scaraStart()
功能  启动机械臂线程
"""
def scaraStart():
    
    global rTime#接收消息延时
    global currentPos#当前坐标
    global links#指令集
    global setLinks#指令集操作
    global scara#机械臂通信
    global rTimeErr#超时计数
    global recvTag#接收标志
    global manageConn
    global action#机械臂动作
    global POS_barcode
    global plc
    global vis
    global circles
    global circle
    global circles2
    global hight
    global box
    global notice1  #翻页1
    global notice2  #翻页2
    global notice3  #翻页3
    global notice4  #翻页4
    global line_box
    global database
    global point_box
    global grab
    global putPos
    global palletcenter
    global currentNumber
    global rcs
    global vectorA
    global carton_numder
    global circles_identify_count  # 纱锭识别次数计数器
    global spindlesCnt  # 期望纱锭数量
    global areaLength
    global areaWidth
    global temp_putPos
    global spindleHeight
    global placement_step
    global pallet_recog_cam_pos
    global pallet_recog_cam_euler
    global cam_pos_left
    global cam_euler_left
    global cam_pos_right
    global cam_euler_right
    global left_positions
    global right_positions
    global jiehao
    global putPos_index
    global pallet_recog_cam_height
    global fznumber
    global camera_offline
    
    jiehao = False
    camera_offline = False
    
    rTime = 5
    rTimeErr = 0
    currentPos = {'x':0,'y':0,'z':0,'u':0,'v':0,'w':0,'ID':0}
    links = list()
    setLinks=SetLinks()
    scara = SCARAConnect(ScaraHost,ScaraPort)
    rcs = RCSConnect(RCSServerHost,RCSServerPort,"000000")
    manageConn = ManagementConnect(config.ServerHost, config.ServerPort)
    database = Database('localhost',3306, 'root', 'JYZN_2331_agv', 'cxqs')
    currentNumber = ""
    #plc = PLCConnect(config.ServerHost, config.ServerPort)
    box = []
    line_box = []
    circles = []
    circle={'x':0,'y':0,'z':0} 
    grab = {'x':0,'y':0,'z':0,'w':0}
    palletcenter = {'x':0,'y':0,'z':0,'w':0}
    line_box = []
    circles2 = []
    putPos = []
    temp_putPos = []
    hight = 0
    spindleHeight = 400
    placement_step = 0
    pallet_recog_cam_pos = np.array([0, 0, 0])
    pallet_recog_cam_euler = {'u': 0, 'v': 0, 'w': 0}
    cam_pos_left = np.array([0, 0, 0])
    cam_euler_left = {'u': 0, 'v': 0, 'w': 0}
    cam_pos_right = np.array([0, 0, 0])
    cam_euler_right = {'u': 0, 'v': 0, 'w': 0}
    left_positions = []
    right_positions = []
    putPos_index = 0
    pallet_recog_cam_height = 0
    fznumber = 1
    config.boxfull = True
    
    recvTag = 0
    action = 0    #99999，0自己启动
    POS_barcode = {'x':0,'y':0,'z':0,'u':0,'v':0,'w':0}
    vectorA = np.array([[ 1.004,  0.016,  0.029], [-0.02 ,  1.006, -0.008],[-0.033,  0,  1.01 ]])
    carton_numder = 1
    circles_identify_count = 0  # 初始化识别次数为0
    spindlesCnt = 6  # 期望纱锭数量
    areaLength = 300  # 区域长度
    areaWidth = 300  # 区域宽度
    notice1 = 0
    notice2 = 0
    notice3 = 0
    notice4 = 0


class Logger(object):
    level_relations = {
        'debug':logging.DEBUG,
        'info':logging.INFO,
        'warning':logging.WARNING,
        'error':logging.ERROR,
        'crit':logging.CRITICAL
    }#日志级别关系映射

    def __init__(self,filename,level='info',when='D',backCount=3,fmt='【%(asctime)s】  %(message)s'):#- %(pathname)s[line:%(lineno)d] - %(levelname)s:
        self.logger = logging.getLogger(filename)
        format_str = logging.Formatter(fmt)#设置日志格式
        self.logger.setLevel(self.level_relations.get(level))#设置日志级别
        sh = logging.StreamHandler()#往屏幕上输出
        sh.setFormatter(format_str) #设置屏幕上显示的格式
        th = handlers.TimedRotatingFileHandler(filename=filename,when=when,backupCount=backCount,encoding='utf-8')#往文件里写入#指定间隔时间自动生成文件的处理器
        #实例化TimedRotatingFileHandler
        #interval是时间间隔，backupCount是备份文件的个数，如果超过这个个数，就会自动删除，when是间隔的时间单位，单位有以下几种：
        # S 秒
        # M 分
        # H 小时、
        # D 天、
        # W 每星期（interval==0时代表星期一）
        # midnight 每天凌晨
        th.setFormatter(format_str)#设置文件里写入的格式
        self.logger.addHandler(sh) #把对象加到logger里
        self.logger.addHandler(th)

def loginit():
    global log
    basedir = os.path.abspath(os.path.dirname(__file__))
    log_path = os.path.join(basedir, 'logs' )  # 日志根目录 ../logs/
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    log_filename = time.strftime("%F") + '.log'
    log_name = os.path.join(log_path,log_filename)
    log = Logger(log_name,level='debug')
