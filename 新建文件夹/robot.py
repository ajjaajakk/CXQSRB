import copy
from re import L
import numpy as np
import math
from _socket import *
from threading import Thread ,Timer
import datetime
import time
import config
from datetime import datetime
from scipy import stats


"""
    获取机械臂动作步骤
    函数名：getStep()  
"""

def getStep():
    try:
        if len(config.links) == 0:
            return False
        for link in config.links:
            if link['State'] == True:
               return link
        return False
    except Exception as e:
        config.log.logger.info('SCARA Error:' + str(e.args))

"""
    函数名：SendSCARA()  
    发送指定数据和对应动作处理
"""
def SendSCARA(link):
    if link == None:
        return
    #if link == None:
    #    return
    #0计数器确认位置；1中间变量M0；2下发坐标；3下发速度；4获取当前坐标让机械臂到n托盘或n缓存区识别点；5开始；6结束；7PLC机械臂夹爪
    # 确认位置
    if link['typeID'] == 0:
        if config.scara.GetPostion():
            if config.currentPos['ID'] >= link['minID'] and config.currentPos["ID"] <= link['maxID']:
                link['State'] = False

    #中间变量M0
    if link['typeID'] == 1:
        if config.scara.modifyOutput(link):
            link['State'] = False
    #下发坐标
    if link['typeID'] == 2:
        if config.scara.rewriteDataList(link):
            link['State'] = False
    #下发速度
    if link['typeID'] == 3:
        if config.scara.setSpeed(link):
            link['State'] = False
    #获取当前坐标让机械臂到n托盘或n缓存区识别点
    if link['typeID'] == 4:
        finalLinks=[]
        if config.scara.GetPostion():
            link['State'] = False
    #开始
    if link['typeID'] == 5:
        if config.scara.startButton():
            link['State'] = False
    #结束
    if link['typeID'] == 6:
        if config.scara.stopButton():
            link['State'] = False
    #设置计数器
    if link['typeID'] == 7:
        if config.scara.modifyCounter(link):
            link['State'] = False

    if link['typeID'] == 8:
        config.log.logger.info("typeID = 8")
        if config.scara.rewriteDataListStr(link):#识别下发轨迹
            link['State'] = False

    if link['typeID'] == 9:
        if config.manageConn.Visual_box_postion():#识别箱体位置
            link['State'] = False

    if link['typeID'] == 10:
        if config.manageConn.Visual_spindle_pos():
            link['State'] = False

    if link['typeID'] == 11:
        if config.manageConn.Visual_spindle_pos2(link):#识别识别切缝
            link['State'] = False

    if link['typeID'] == 12:
        if config.manageConn.getAllSpindlePostion():#识别全局纱锭
            link['State'] = False
    if link['typeID'] == 13:
        if config.manageConn.getSingleSpindlePostion():#识别单个纱锭
            link['State'] = False
    if link['typeID'] == 14:
         if config.manageConn.putVis():#识别放置位置上是否有东西
            link['State'] = False
    if link['typeID'] == 15:
         if config.manageConn.getPutPostion(link):#识别放置位置
            link['State'] = False
    if link['typeID'] == 16:
         if config.manageConn.getBoxLeafPostion(link):#识别第二第三页
            link['State'] = False
    if link['typeID'] == 17:
         if config.manageConn.getGrabPostion(link):#识别纸箱抓取位置
            link['State'] = False
    if link['typeID'] == 18:
         if config.manageConn.getBarcodePostion(link):#识别二维码
            link['State'] = False
    if link['typeID'] == 19:
         if config.manageConn.getPalletCenterPostion():#识别托盘中心
            link['State'] = False
"""
函数名：MainRun()  
定时器主函数
"""
def MainRun():
    while True:        
        link = getStep()
        if link != False:
            SendSCARA(link)        
        time.sleep(0.01)

"""
函数名：ReplacePalletInit()  
更换托盘初始化
"""
def ReplacePalletInit(num):
    if num == 0:
        return
    
"""
函数名：SendPackage()  
发送指定数据
"""
def SendPackage():
    now =  time.time()
    if abs(now - config.HeartTime) >= config.HeartbeatCycle:
        config.HeartTime = time.time()
        config.rcs.Heartbeat()

"""
函数名：MainRunmanageConn()  
连接上位机
"""
def RCSConn():
    #global manageConn
    #manageConn = ManagementConnect(config.ServerHost, config.ServerPort)
    #config.manageConn.start()
    while True:
        time.sleep(5)
        try:
            SendPackage();
            time.sleep(0.01)
        except Exception as e:
            print("MainRun Error:" + str(e.args))




def revolve(euler,vector):
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


def rotation_matrix(euler):
    u = euler['u'] / 180 * math.pi
    v = euler['v'] / 180 * math.pi
    w = euler['w'] / 180 * math.pi

    a = np.array([[1,0,0],[0,math.cos(u),-math.sin(u)],[0,math.sin(u),math.cos(u)]])
    b = np.array([[math.cos(v),0,math.sin(v)],[0,1,0],[-math.sin(v),0,math.cos(v)]])
    c = np.array([[math.cos(w),-math.sin(w),0],[math.sin(w),math.cos(w),0],[0,0,1]])

    d = np.dot(c, b)
    d = np.dot(d, a)

    return d

def exchange3(euler_tar,vector_tar):
    JS = []
    a = np.array([169.588,0.498,494.6])#(X1ecc,-Y1ecc,Z)
    b = np.array([0,0,730.870])        #(0,0,L23)
    c = np.array([826.042,0,99.301])   #(L34b,0,L34a)
    d = np.array([164.00,0,0])         #(L56,0,0)
    d2 = np.array([0,0,164.00])        #(0,0,L56)
    P2 = vector_tar - revolve(euler_tar,d2)

    J1 = math.atan2(vector_tar[1],vector_tar[0])/math.pi*180
    return J1

def route_planning3(startPos,EndPos,hight):
    poss = []

    vector_start = np.array([startPos['x'],startPos['y'],startPos['z']])
    euler_start = {'u':startPos['u'],'v':startPos['v'],'w':startPos['w']}
    vector_end = np.array([EndPos['x'],EndPos['y'],EndPos['z']])
    euler_end = {'u':EndPos['u'],'v':EndPos['v'],'w':EndPos['w']}
    t_start = revolve(euler_start,np.array([0,0,100]))
    t_end = revolve(euler_end,np.array([0,0,100]))
    w_start = math.atan2(t_start[1],t_start[0])/math.pi*180
    w_end = math.atan2(t_end[1],t_end[0])/math.pi*180
    w_point_start = math.atan2(startPos['y'],startPos['x'])/math.pi*180
    w_point_end = math.atan2(EndPos['y'],EndPos['x'])/math.pi*180
    r_start = (startPos['x']**2+startPos['y']**2)**0.5
    r_end = (EndPos['x']**2+EndPos['y']**2)**0.5

    #point = copy.deepcopy(startPos)
    #point['z'] = hight
    #poss.append(point)

    for i in range(0,4):
        point = {'x':0,'y':0,'z':0,'u':0,'v':90,'w':0} 
        w_point = w_point_start + (w_point_end - w_point_start)/4*(i)
        r = r_start +(r_end -r_start)/4*(i)
        point['x'] = r*math.cos(w_point/180*math.pi)
        point['y'] = r*math.sin(w_point/180*math.pi)
        point['z'] = hight
        point['w'] = w_start + (w_end - w_start)/4*(i)
        if point['x'] < 650 and hight > 1100:
            hight = 1100
        poss.append(point)
        
    point = copy.deepcopy(EndPos)
    point['z'] = hight
    poss.append(point)
    poss_arm = []
    for i in poss:
        poss_arm.append({'x':int(i['x']*1000),'y':int(i['y']*1000),'z':int(i['z']*1000),'u':int(i['u']*1000),'v':int(i['v']*1000),'w':int(i['w']*1000)})
        print(i)
    
    return poss,poss_arm


def route_planning(startPos,EndPos,hight):
    poss = []

    vector_start = np.array([startPos['x'],startPos['y'],startPos['z']])
    euler_start = {'u':startPos['u'],'v':startPos['v'],'w':startPos['w']}
    vector_end = np.array([EndPos['x'],EndPos['y'],EndPos['z']])
    euler_end = {'u':EndPos['u'],'v':EndPos['v'],'w':EndPos['w']}
    t_start = revolve(euler_start,np.array([0,0,100]))
    t_end = revolve(euler_end,np.array([0,0,100]))
    w_start = math.atan2(t_start[1],t_start[0])/math.pi*180
    w_end = math.atan2(t_end[1],t_end[0])/math.pi*180
    w_point_start = math.atan2(startPos['y'],startPos['x'])/math.pi*180
    w_point_end = math.atan2(EndPos['y'],EndPos['x'])/math.pi*180
    r_start = (startPos['x']**2+startPos['y']**2)**0.5
    r_end = (EndPos['x']**2+EndPos['y']**2)**0.5

    #point = copy.deepcopy(startPos)
    #point['z'] = hight
    #poss.append(point)


    for i in range(0,6):
        point = {'x':0,'y':0,'z':0,'u':0,'v':90,'w':0} 
        w_point = w_point_start + (w_point_end - w_point_start)/6*(i)
        r = r_start +(r_end -r_start)/6*(i)
        point['x'] = r*math.cos(w_point/180*math.pi)
        point['y'] = r*math.sin(w_point/180*math.pi)
        point['z'] = hight
        point['w'] = w_start + (w_end - w_start)/6*(i)
        poss.append(point)
        
    point = copy.deepcopy(EndPos)
    point['z'] = hight
    poss.append(point)
    poss_arm = []
    for i in poss:
        poss_arm.append({'x':int(i['x']*1000),'y':int(i['y']*1000),'z':int(i['z']*1000),'u':int(i['u']*1000),'v':int(i['v']*1000),'w':int(i['w']*1000)})
        print(i)
    
    return poss,poss_arm

#视觉自检，自标定
def StarStartUpPreparation():
    action = 0
    ##1.013538046,0.014249271,0.021339918,   -0.012247965,1.017577204,-0.008829735,    -0.014586829,0.016555877,1.021206479,
    vectorA = config.vectorA
    #440.5351145	31.38990992	85.48878011

    vector1 = np.array([-91.291,  35.325, 463.056])#相机偏移
    current_time = datetime.now()
    while True: 
        current_time = datetime.now()
        if action == 0:
            if getStep() == False:
                config.setLinks.linkstar()
                action = 1
        if action == 1:
            if getStep() == False:                
                vectorStart = np.array([config.currentPos['x'],config.currentPos['y'],config.currentPos['z']])
                eulerStart = { 'u':config.currentPos['u'], 'v':config.currentPos['v'], 'w':config.currentPos['w'] }
                config.database.insert(str(current_time),0,vectorStart[0],vectorStart[1],vectorStart[2],eulerStart['u'],eulerStart['v'],eulerStart['w'])
                hight = 1000
                startPos = copy.deepcopy(config.currentPos)
                EndPos = {'x':583,'y':1101,'z':hight,'u':0,'v':90,'w':0}               
                trans,poss_arm = route_planning(startPos,EndPos,hight)
                poss = copy.deepcopy(poss_arm)
                count = len(poss_arm)
                for i in range(0,8-count):
                    poss.append(poss_arm[len(poss_arm)-1])
                config.links = config.setLinks.links_action22(poss)#回到初始点 

                action = 2
        if action == 2:
            if getStep() == False:
                poss = [] 
                vectorVisBarcode = np.array([583,1101,55])
                eulerVisBarcode = { 'u':0, 'v':90, 'w':0 }
                poss.append({'x':int(69.141*1000),'y':int(-16.940*1000),'z':int(-6.950*1000),'u':int(81.228*1000),'v':int(70.999*1000),'w':int(-64.640*1000)})
                poss.append({'x':int(vectorVisBarcode[0]*1000),'y':int(vectorVisBarcode[1]*1000),'z':int(vectorVisBarcode[2]*1000),'u':int(eulerVisBarcode['u']*1000),'v':int(eulerVisBarcode['v']*1000),'w':int(eulerVisBarcode['w']*1000)})
                config.setLinks.links_action18(poss,175,50)#识别二维码
                action = 3
        if action == 3:
            if getStep() == False:
                recvVisBarcode = revolve({'u':0, 'v':0, 'w':eulerVisBarcode['w'] },vectorA@np.array([config.POS_barcode['x'],config.POS_barcode['y'],config.POS_barcode['z']]))
                vector1_2 =  revolve(eulerVisBarcode,vector1)
                vectorPosBarcode = vectorVisBarcode + vector1_2+recvVisBarcode
                config.database.insert(str(current_time),600,config.POS_barcode['x'],config.POS_barcode['y'],config.POS_barcode['z'],vectorPosBarcode[0],vectorPosBarcode[1],vectorPosBarcode[2])
                poss = []
                vectorStart = np.array([config.currentPos['x'],config.currentPos['y'],config.currentPos['z']])
                eulerStart = { 'u':config.currentPos['u'], 'v':config.currentPos['v'], 'w':config.currentPos['w'] }
                #config.database.insert(str(current_time),0,vectorStart[0],vectorStart[1],vectorStart[2],eulerStart['u'],eulerStart['v'],eulerStart['w'])
                hight = 1000
                startPos = copy.deepcopy(config.currentPos)
                EndPos = {'x':900,'y':0,'z':hight,'u':0,'v':90,'w':0}               
                trans,poss_arm = route_planning(startPos,EndPos,hight)
                poss = copy.deepcopy(poss_arm)
                count = len(poss_arm)
                for i in range(0,8-count):
                    poss.append(poss_arm[len(poss_arm)-1])
                #config.setLinks.links_action22(poss)#回到拆箱取纱起点
                action = 4
                           
                
        if action == 4:
            if getStep() == False:
                pos_mren = []
                pos_mren.append(np.array([600,725,95]))
                pos_mren.append(np.array([350,725,95]))
                pos_mren.append(np.array([100,725,95]))
                pos_mren.append(np.array([-150,725,95]))
                pos_mren.append(np.array([-400,725,95]))
                pos_mren.append(np.array([-650,725,95]))

                pos_mren.append(np.array([600,975,95]))
                pos_mren.append(np.array([350,975,95]))
                pos_mren.append(np.array([100,975,95]))
                pos_mren.append(np.array([-150,975,95]))
                pos_mren.append(np.array([-400,975,95]))
                pos_mren.append(np.array([-650,975,95]))

                pos_mren.append(np.array([600,1225,95]))
                pos_mren.append(np.array([350,1225,95]))
                pos_mren.append(np.array([100,1225,95]))
                pos_mren.append(np.array([-150,1225,95]))
                pos_mren.append(np.array([-400,1225,95]))
                pos_mren.append(np.array([-650,1225,95]))

                pos_mren.append(np.array([600,1475,95]))
                pos_mren.append(np.array([350,1475,95]))
                pos_mren.append(np.array([100,1475,95]))
                pos_mren.append(np.array([-150,1475,95]))
                pos_mren.append(np.array([-400,1475,95]))
                pos_mren.append(np.array([-650,1475,95]))

                pos_mren.append(np.array([600,-725,103]))
                pos_mren.append(np.array([350,-725,103]))
                pos_mren.append(np.array([100,-725,103]))
                pos_mren.append(np.array([-150,-725,103]))
                pos_mren.append(np.array([-400,-725,103]))
                #pos_mren.append(np.array([-650,-725,95]))

                pos_mren.append(np.array([600,-975,103]))
                pos_mren.append(np.array([350,-975,103]))
                pos_mren.append(np.array([100,-975,103]))
                pos_mren.append(np.array([-150,-975,103]))
                pos_mren.append(np.array([-400,-975,103]))
                #pos_mren.append(np.array([-650,-975,95]))

                pos_mren.append(np.array([600,-1225,103]))
                pos_mren.append(np.array([350,-1225,103]))
                pos_mren.append(np.array([100,-1225,103]))
                pos_mren.append(np.array([-150,-1225,103]))
                pos_mren.append(np.array([-400,-1225,103]))
                #pos_mren.append(np.array([-650,-1225,95]))

                pos_mren.append(np.array([600,-1475,103]))
                pos_mren.append(np.array([350,-1475,103]))
                pos_mren.append(np.array([100,-1475,103]))
                pos_mren.append(np.array([-150,-1475,103]))
                pos_mren.append(np.array([-400,-1475,103]))
                #pos_mren.append(np.array([-650,-1475,95]))


                return pos_mren


"""
ident_point 识别点
visual_coordinate 视觉坐标
ident_euler 识别姿态
camera_T 相机偏移矩阵
函数名：获取物体的实际位置
"""
def GetRealPoint(ident_point,visual_coordinate,ident_euler,camera_T):#获取物体的实际位置
    vectorA = config.vectorA
    camera_T_R = revolve(ident_euler,camera_T)
    visual_coordinate_R = revolve({ 'u':0, 'v':0, 'w':ident_euler['w']},vectorA@visual_coordinate)   
    real_point = ident_point + camera_T_R + visual_coordinate_R 
    return copy.deepcopy(real_point)


"""
real_point 物体的实际位置
clamp_euler 夹爪夹取姿态
clamp_T 夹爪偏移矩阵
函数名：获取夹取点
"""
def GetThePinchPoint(real_point,clamp_euler,clamp_T):#获取夹取点
    clamp_T_R = revolve(clamp_euler,clamp_T)    
    clamp_point = real_point - clamp_T_R
    return copy.deepcopy(clamp_point)

"""
real_point 物体的实际点位
camera_T 相机偏移
ident_euler 二次识别时的姿态
hight 再次识别物体，相机与物体的高度
函数名：获取再次识别点
"""
def GetTwiceIdentPoint(real_point,camera_T,ident_euler,hight):#获取二次识别点位
    vectorA = config.vectorA#旋转矩阵
    vector_target = revolve({ 'u':0, 'v':0, 'w':ident_euler['w'] },vectorA@np.array([0,0,-hight]))
    camera_T_R = revolve(ident_euler,camera_T)
    twice_ident_point = real_point - vector_target - camera_T_R    
    return copy.deepcopy(twice_ident_point)

"""
carton_numder： 纸箱编码
函数名：GetParameter()  
获取箱数
"""
def GetParameter(carton_numder):
    order = []
    Longsidecoe = 0
    Shortsidecoe = 0
    rule = 0
    if carton_numder == 1:                #百宏 83/72
        spindle_od = 215
        spindle_id = 65
        Hight = 300

    if carton_numder == 2:                #百宏 55/72 
        spindle_od = 185
        spindle_id = 65
        Hight = 300

    if carton_numder == 3:                #A-21 鑫森44drex/36f             
        spindle_od = 180
        spindle_id = 65
        Hight = 317

    if carton_numder == 4:               #鑫森(环保纱) 22/24（8粒）
        spindle_od = 150
        spindle_id = 65
        Hight = 314
        Shortsidecoe = 0.5


    if carton_numder == 5:              #百宏 33/36
        spindle_od = 185
        spindle_id = 65
        Hight = 306

    if carton_numder == 7:             #鑫森 22/24    长560  宽380
        spindle_od = 145
        spindle_id = 65
        Hight = 315
        Shortsidecoe = 0.6
        order = np.array([2,5,0,1,3,4,6,7])

    if carton_numder == 8:             #百宏 110/84 
        spindle_od = 165
        spindle_id = 65
        Hight = 304

    if carton_numder == 9:             #百宏 83/36 
        spindle_od = 220
        spindle_id = 65
        Hight = 305
    
    if carton_numder == 10:             #翔鹭化纤 111/096
        spindle_od = 190
        spindle_id = 65
        Hight = 315
        Shortsidecoe = 0.6
        order = np.array([2,5,0,1,3,4,6,7])
        
    if carton_numder == 11:             #鑫森 78/48 
        spindle_od = 210
        spindle_id = 65
        Hight = 310
        
    if carton_numder == 12:             #百宏 111/144 
        spindle_od = 225
        spindle_id = 65
        Hight = 310
        
    if carton_numder == 13:               #鑫森78drex/48f DTY全消光（环保纱）
        spindle_od = 210
        spindle_id = 65
        Hight = 313
        
    if carton_numder == 14:               #A-17鑫森33/36 DTY全消光（环保纱）
        spindle_od = 170
        spindle_id = 65
        Hight = 316
        
    if carton_numder == 15:               #鑫森(环保纱) 22/24 (12粒)
        spindle_od = 150
        spindle_id = 65
        Hight = 300

    if carton_numder == 16:               #锦纶 鑫源丝 44/48 (12粒)
        spindle_od = 150
        spindle_id = 65
        Hight = 318
        Shortsidecoe = 0.33
        
    if carton_numder == 22:               #鑫森78drex/48f DTY全消光（环保纱）
        spindle_od = 140
        spindle_id = 130
        Hight = 310
        Longsidecoe = 0.22

    if carton_numder == 10000:               #A-17鑫森33/36 DTY全消光（环保纱）
        spindle_od = 205
        spindle_id = 65
        Hight = 316

    return spindle_id,spindle_od,Hight,Longsidecoe,Shortsidecoe,order,rule

"""
vector0 识别姿态
euler0 识别角度
函数名：首次识别纸箱  
"""
def IdentificationAction1(ident_point,ident_euler,hight):
    poss = []               
    #hight = 950
    startPos = copy.deepcopy(config.currentPos)
    EndPos = {'x':ident_point[0],'y':ident_point[1],'z':hight,'u':ident_euler['u'],'v':ident_euler['v'],'w':ident_euler['w']}               
    trans,poss_arm = route_planning(startPos,EndPos,hight)
    poss = copy.deepcopy(poss_arm)
    poss.append({'x':int(ident_point[0]*1000),'y':int(ident_point[1]*1000),'z':int(ident_point[2]*1000),'u':int(ident_euler['u']*1000),'v':int(ident_euler['v']*1000),'w':int(ident_euler['w']*1000)}) 
    if config.currentPos['ID'] == 4:
        links = config.setLinks.links_action22(poss)
    else:
        links = config.setLinks.links_action2(poss)
    return links

#切缝动作
def SlittingAction(sorted_data,euler10):
    poss = []               
    if len(sorted_data) == 40:
        #fanxianghight = (sorted_data[19][2]+sorted_data[20][2]+sorted_data[21][2])/3+vector10_2[2]
        singlepos = sorted_data[0]+np.array([0,0,100])        
        poss.append({'x':int(singlepos[0]*1000),'y':int(singlepos[1]*1000),'z':int(singlepos[2]*1000),'u':int(euler10['u']*1000),'v':int(euler10['v']*1000),'w':int(euler10['w']*1000)})  
        for i in range (0,2):
            Avg = (copy.deepcopy(np.array(sorted_data[0]))+copy.deepcopy(np.array(sorted_data[1])))/2
            singlepos = sorted_data[0]- np.array([0,0,3])
            poss.append({'x':int(singlepos[0]*1000),'y':int(singlepos[1]*1000),'z':int(singlepos[2]*1000),'u':int(euler10['u']*1000),'v':int(euler10['v']*1000),'w':int(euler10['w']*1000)})  
            singlepos = sorted_data[0]+np.array([0,0,4])
            poss.append({'x':int(singlepos[0]*1000),'y':int(singlepos[1]*1000),'z':int(singlepos[2]*1000),'u':int(euler10['u']*1000),'v':int(euler10['v']*1000),'w':int(euler10['w']*1000)})
            if i == 0:
                singlepos = Avg- np.array([0,0,3])           
                poss.append({'x':int(singlepos[0]*1000),'y':int(singlepos[1]*1000),'z':int(singlepos[2]*1000),'u':int(euler10['u']*1000),'v':int(euler10['v']*1000),'w':int(euler10['w']*1000)})  
                singlepos = Avg+np.array([0,0,4])
                poss.append({'x':int(singlepos[0]*1000),'y':int(singlepos[1]*1000),'z':int(singlepos[2]*1000),'u':int(euler10['u']*1000),'v':int(euler10['v']*1000),'w':int(euler10['w']*1000)})
            sorted_data.remove(sorted_data[0])
        for i in range (0,8):                        
            singlepos = sorted_data[0]- np.array([0,0,4])
            poss.append({'x':int(singlepos[0]*1000),'y':int(singlepos[1]*1000),'z':int(singlepos[2]*1000),'u':int(euler10['u']*1000),'v':int(euler10['v']*1000),'w':int(euler10['w']*1000)})  
            sorted_data.remove(sorted_data[0])
    elif len(sorted_data) == 30:       
        for i in range (0,15):                        
            singlepos = sorted_data[0] - np.array([0,0,4])
            poss.append({'x':int(singlepos[0]*1000),'y':int(singlepos[1]*1000),'z':int(singlepos[2]*1000),'u':int(euler10['u']*1000),'v':int(euler10['v']*1000),'w':int(euler10['w']*1000)})  
            sorted_data.remove(sorted_data[0])
        sorted_data.remove(sorted_data[0])
    elif len(sorted_data) == 14: 
        for i in range (0,6):                        
            singlepos = sorted_data[0]- np.array([0,0,4])
            poss.append({'x':int(singlepos[0]*1000),'y':int(singlepos[1]*1000),'z':int(singlepos[2]*1000),'u':int(euler10['u']*1000),'v':int(euler10['v']*1000),'w':int(euler10['w']*1000)})  
            sorted_data.remove(sorted_data[0])
        for i in range (0,8):                        
            singlepos = sorted_data[0]- np.array([0,0,4])
            poss.append({'x':int(singlepos[0]*1000),'y':int(singlepos[1]*1000),'z':int(singlepos[2]*1000),'u':int(euler10['u']*1000),'v':int(euler10['v']*1000),'w':int(euler10['w']*1000)})  
            sorted_data.remove(sorted_data[0]) 
        singlepos += np.array([0,0,30])
        for i in range(0,1):
            poss.append({'x':int(singlepos[0]*1000),'y':int(singlepos[1]*1000),'z':int(singlepos[2]*1000),'u':int(euler10['u']*1000),'v':int(euler10['v']*1000),'w':int(euler10['w']*1000)})  
    print(poss)
    links = config.setLinks.links_action4(poss)
    return links

#点头切
def SlittingAction2(vector133,vector134,vector_qie,euler10_2):
    poss = []
    vector33 = copy.deepcopy(vector133)+ vector_qie
    vector34 = copy.deepcopy(vector134)+ vector_qie
    vector40 = vector33*7/8+ vector34*1/8
    vector41 = vector33*6/8+ vector34*2/8
    vector42 = vector33*5/8+ vector34*3/8
    vector43 = vector33*4/8+ vector34*4/8
    vector46 = vector33*3/8+ vector34*5/8
    vector47 = vector33*2/8+ vector34*6/8
    vector48 = vector33*1/8+ vector34*7/8
    vector49 = vector34
    vector44 = ([0,0,-16,0,0,0])#下降深度
    vector45 = ([0,0,55,0,0,0])#抬高高度
    euler40 = copy.deepcopy(euler10_2)

    starhig = vector33[2]
    poss.append({'x':int(vector33[0]*1000),'y':int(vector33[1]*1000),'z':int((starhig+100)*1000),'u':int(euler40['u']*1000),'v':int(euler40['v']*1000),'w':int((euler40['w'])*1000)})
    poss.append({'x':int(vector33[0]*1000),'y':int(vector33[1]*1000),'z':int(starhig*1000),'u':int(euler40['u']*1000),'v':int(euler40['v']*1000),'w':int((euler40['w'])*1000)})
    poss.append({'x':int(vector40[0]*1000),'y':int(vector40[1]*1000),'z':int(starhig*1000),'u':int(euler40['u']*1000),'v':int(euler40['v']*1000),'w':int((euler40['w'])*1000)})               
    poss.append({'x':int(vector41[0]*1000),'y':int(vector41[1]*1000),'z':int(starhig*1000),'u':int(euler40['u']*1000),'v':int(euler40['v']*1000),'w':int((euler40['w'])*1000)})               
    poss.append({'x':int(vector42[0]*1000),'y':int(vector42[1]*1000),'z':int(starhig*1000),'u':int(euler40['u']*1000),'v':int(euler40['v']*1000),'w':int((euler40['w'])*1000)})                
    poss.append({'x':int(vector43[0]*1000),'y':int(vector43[1]*1000),'z':int(starhig*1000),'u':int(euler40['u']*1000),'v':int(euler40['v']*1000),'w':int((euler40['w'])*1000)})                
    poss.append({'x':int(vector34[0]*1000),'y':int(vector34[1]*1000),'z':int(starhig*1000),'u':int(euler40['u']*1000),'v':int(euler40['v']*1000),'w':int((euler40['w'])*1000)})
    poss.append({'x':int(vector44[0]*1000),'y':int(vector44[1]*1000),'z':int(vector44[2]*1000),'u':int(vector44[3]*1000),'v':int(vector44[4]*1000),'w':int(vector44[5]*1000)})
    poss.append({'x':int(vector45[0]*1000),'y':int(vector45[1]*1000),'z':int(vector45[2]*1000),'u':int(vector45[3]*1000),'v':int(vector45[4]*1000),'w':int(vector45[5]*1000)})
    poss.append({'x':int(vector46[0]*1000),'y':int(vector46[1]*1000),'z':int(starhig*1000),'u':int(euler40['u']*1000),'v':int(euler40['v']*1000),'w':int((euler40['w'])*1000)})    
    poss.append({'x':int(vector47[0]*1000),'y':int(vector47[1]*1000),'z':int(starhig*1000),'u':int(euler40['u']*1000),'v':int(euler40['v']*1000),'w':int((euler40['w'])*1000)})    
    poss.append({'x':int(vector48[0]*1000),'y':int(vector48[1]*1000),'z':int(starhig*1000),'u':int(euler40['u']*1000),'v':int(euler40['v']*1000),'w':int((euler40['w'])*1000)})    
    poss.append({'x':int(vector49[0]*1000),'y':int(vector49[1]*1000),'z':int(starhig*1000),'u':int(euler40['u']*1000),'v':int(euler40['v']*1000),'w':int((euler40['w'])*1000)}) 
    links = config.setLinks.links_action5(poss)
    return links

#翻箱动作
def MouldTurnoverAction(mouldEuler,vector_xipan,vector51,vector53,vector53_2,vector56,firstEuler,twiceEuler,derW,carton_height,derVector1,derVector2):    
    euler2 = firstEuler

    poss = []
    poss.append({'x':int(-0.038*1000),'y':int(18.407*1000),'z':int(-41.890*1000),'u':int(-0.098*1000),'v':int(23.482*1000),'w':int(0.087*1000)})
                
    vector_xipan_2 = revolve(euler2,vector_xipan)
    vector54 = vector51 + revolve({ 'u':0, 'v':0, 'w':derW},vector53)
    vector70 = vector54 - vector_xipan_2 

    poss.append({'x':int((vector70[0]+derVector1[0])*1000),'y':int((vector70[1]+derVector1[1])*1000),'z':int((vector70[2]+250)*1000),'u':int(euler2['u']*1000),'v':int((euler2['v'])*1000),'w':int((euler2['w'])*1000)})
    poss.append({'x':int((vector70[0]+derVector1[0])*1000),'y':int((vector70[1]+derVector1[1])*1000),'z':int((vector70[2]+derVector1[2])*1000),'u':int(euler2['u']*1000),'v':int((euler2['v'])*1000),'w':int((euler2['w'])*1000)})
    poss.append({'x':int((vector70[0]+derVector2[0])*1000),'y':int((vector70[1]+derVector2[1])*1000),'z':int((vector70[2]+derVector2[2])*1000),'u':int(euler2['u']*1000),'v':int((euler2['v'])*1000),'w':int((euler2['w'])*1000)})

    vector53 = vector53_2
                
    mouldEulerLIst = []
    for i in range(0,9):
        mouldEulerLIst.append({ 'u':mouldEuler['u']*i, 'v':mouldEuler['v']*i, 'w':mouldEuler['w'] })     
        
    euler2 = { 'u':(firstEuler['u']+twiceEuler['u'])/2, 'v':(firstEuler['v']+twiceEuler['v'])/2, 'w':(firstEuler['w']+twiceEuler['w'])/2} 
    vector_xipan_2 = revolve(euler2,vector_xipan)

    vector54 = vector51 + revolve(mouldEulerLIst[1],vector53)
    vector70 = vector54 - vector_xipan_2    
    poss.append({'x':int(vector70[0]*1000),'y':int(vector70[1]*1000),'z':int(vector70[2]*1000),'u':int(euler2['u']*1000),'v':int((euler2['v'])*1000),'w':int((euler2['w'])*1000)})

    euler2 = twiceEuler
    vector_xipan_2 = revolve(euler2,vector_xipan)

    vector54 = vector51 + revolve(mouldEulerLIst[2],vector53)
    vector70 = vector54 - vector_xipan_2   
    poss.append({'x':int(vector70[0]*1000),'y':int(vector70[1]*1000),'z':int(vector70[2]*1000),'u':int(euler2['u']*1000),'v':int((euler2['v'])*1000),'w':int((euler2['w'])*1000)})

    vector54 = vector51 + revolve(mouldEulerLIst[3],vector53)
    vector70 = vector54 - vector_xipan_2    
    poss.append({'x':int(vector70[0]*1000),'y':int(vector70[1]*1000),'z':int(vector70[2]*1000),'u':int(euler2['u']*1000),'v':int((euler2['v'])*1000),'w':int((euler2['w'])*1000)})

    vector54 = vector56 + revolve(mouldEulerLIst[4],vector53)
    vector70 = vector54 - vector_xipan_2    
    poss.append({'x':int(vector70[0]*1000),'y':int(vector70[1]*1000),'z':int(vector70[2]*1000),'u':int(euler2['u']*1000),'v':int((euler2['v'])*1000),'w':int((euler2['w'])*1000)})

    vector54 = vector56 + revolve(mouldEulerLIst[5],vector53)
    vector70 = vector54 - vector_xipan_2    
    poss.append({'x':int(vector70[0]*1000),'y':int(vector70[1]*1000),'z':int(vector70[2]*1000),'u':int(euler2['u']*1000),'v':int((euler2['v'])*1000),'w':int((euler2['w'])*1000)})

    vector54 = vector56 + revolve(mouldEulerLIst[6],vector53)
    vector70 = vector54 - vector_xipan_2   
    poss.append({'x':int(vector70[0]*1000),'y':int(vector70[1]*1000),'z':int(vector70[2]*1000),'u':int(euler2['u']*1000),'v':int((euler2['v'])*1000),'w':int((euler2['w'])*1000)})

    vector54 = vector56 + revolve(mouldEulerLIst[7],vector53)
    vector70 = vector54 - vector_xipan_2    
    poss.append({'x':int(vector70[0]*1000),'y':int(vector70[1]*1000),'z':int(vector70[2]*1000),'u':int(euler2['u']*1000),'v':int((euler2['v'])*1000),'w':int((euler2['w'])*1000)})

    vector54 = vector51 + revolve(mouldEulerLIst[8],vector53)
    vector70 = vector54 - vector_xipan_2    
    poss.append({'x':int(vector70[0]*1000),'y':int(vector70[1]*1000),'z':int((vector70[2]+10)*1000),'u':int(euler2['u']*1000),'v':int((euler2['v'])*1000),'w':int((euler2['w'])*1000)})

    vector_xipan_2 = revolve({ 'u':euler2['u'], 'v':euler2['v'], 'w':euler2['w'] },vector_xipan)
    vector53 = (100/((vector53[0]**2+vector53[1]**2)**0.5))*vector53
    #vector54 = vector51 + revolve(mouldEulerLIst[1]*10,vector53)
    vector54 = vector51 + revolve( {'u':mouldEulerLIst[1]['u']*10, 'v':mouldEulerLIst[1]['v']*10, 'w':mouldEulerLIst[1]['w']*10 },vector53)
    vector71 = vector54 - vector_xipan_2  

    poss.append({'x':int(vector71[0]*1000),'y':int(vector71[1]*1000),'z':int((vector71[2]+10)*1000),'u':int(euler2['u']*1000),'v':int(euler2['v']*1000),'w':int((euler2['w'])*1000)})            
    poss.append({'x':int(vector70[0]*1000),'y':int(vector70[1]*1000),'z':int((vector70[2]+10)*1000),'u':int(euler2['u']*1000),'v':int(euler2['v']*1000),'w':int((euler2['w'])*1000)})
    poss.append({'x':int(vector70[0]*1000),'y':int(vector70[1]*1000),'z':int((vector70[2]+250)*1000),'u':int(euler2['u']*1000),'v':int(euler2['v']*1000),'w':int((euler2['w'])*1000)})
    poss.append({'x':int(0),'y':int(0),'z':int(0),'u':int(0),'v':int(0),'w':int(0)})
    links = config.setLinks.links_action8(poss) 
    return links

def IdentificationCmd1(links,typeID):
    links.append({'State':True, 'typeID': typeID})
    return links

def IdentificationCmd2(links,typeID,direction):
    links.append({'State':True, 'typeID': typeID, 'dir': direction}) 
    return links

def IdentificationCmd3(links,typeID,length,width):
    links.append({'State':True, 'typeID': typeID,'length': length, 'width': width})
    return links

def IdentificationCmd4(links,typeID,ID,length):
    links.append({'State':True, 'typeID': typeID,'ID': ID, 'width': length})
    return links


"""
vector_line_left 左侧坐标集
vector_line_right 右侧坐标集
函数名：切缝坐标计算  
"""
def SlitCoordinate(vector_line_left,vector_line_right):
    line_left_x = np.array(vector_line_left)[:,0]
    line_left_y = np.array(vector_line_left)[:,1]
    line_left_z = np.array(vector_line_left)[:,2]

    line_right_x = np.array(vector_line_right)[:,0]
    line_right_y = np.array(vector_line_right)[:,1]
    line_right_z = np.array(vector_line_right)[:,2]

    res1 = stats.linregress(line_left_x, line_left_y)
    res2 = stats.linregress(line_right_x, line_right_y)

    ystar = res1.slope*line_left_x[8]+res1.intercept
    yend = res2.slope*line_right_x[12]+res2.intercept
    slope =  (yend - ystar)/(line_right_x[12]-line_left_x[8])
    intercept = ystar - slope*line_left_x[8]

    posleft = []
    posright = []
    pos = []

    for  i in range(0,len(line_left_x)):
        y2 = slope*line_left_x[i]+intercept
        posleft.append(np.array([line_left_x[i],y2,line_left_z[i]]))
        pos.append(np.array([line_left_x[i],y2,line_left_z[i]]))
    for  i in range(0,len(line_right_x)):
        y2 = slope*line_right_x[i]+intercept
        posright.append(np.array([line_right_x[i],y2,line_right_z[i]]))
        pos.append(np.array([line_right_x[i],y2,line_right_z[i]]))
        
    #merged_array = np.concatenate((array1, array2))
    pos = np.array(pos)
    idex=np.lexsort([pos[:,0]])
    sorted_data = pos[idex, :]
    sorted_data2 = copy.deepcopy(sorted_data)
    for i in range(8,len(sorted_data)-8):
        sorted_data2[i][2] = (sorted_data2[i-1][2]+sorted_data2[i][2]+sorted_data2[i+1][2]+sorted_data2[i+2][2])/4
    #A = 1
    #last_names = data[:, 1]
    return sorted_data2.tolist()
"""
函数名：SCARAMain()  
机械臂线程
"""
def SCARAMain():
    config.scaraStart()
    config.scara.start()
    config.manageConn.start()#oooooooooooooooooooooooooooooooooooooooo
    config.rcs.start()
    time.sleep(1)
    pos_mren = []
    poss = []
    current_time = datetime.now()
    #config.database.insert(str(current_time),1,1,2,3,4,5,6)
    #pos_mren = StarStartUpPreparation()
    while True:
        current_time = datetime.now()
        #config.links =[]#-------------------------------------------------
        
        if config.action == 0: 
            if getStep() == False: 
                
                carton_dir = 0  #0是开左侧箱，1是开右侧箱
                carton_height = 1 #0表示第一层，1表示第二层......
                count = 0
                carton0 = 0 #表示当前放空纸箱的托盘上一共有几个纸箱
                sdgs = 0 #表示托盘上一共有几个纱锭
                #config.links = []
                #config.links.append({'State':True, 'typeID': 16,'length': 574, 'width': 381,'type1': 1,'rule':0})
                config.action = 133

        if config.action == 133:
            if getStep() == False:  
                config.rcs.sender = "UNB"
                project = config.rcs.unpackingSpoolQueue.get()
                StarStartUpPreparation()
                carton_numder = 7 #纸箱类型的编号，1.83/72 百宏 2.55/72 百宏 3.44/36 鑫森 4.22/24 鑫森(环保纱) 5. 33/36 百宏 7.22/24 鑫森
                frequency = 0
                #config.vectorA = np.array([[ 1.007,  0.018,  0.018],  [-0.017,  1.011,  0.012], [-0.015, -0.012,  1.021]])
                config.vectorA = np.array([[ 1.001,0.017,0.02 ],[-0.017,1.01 ,0.01 ],[-0.013,0,1.018]])
                #config.vectorA = config.vectorA*(-982)/config.POS_barcode['z']
                pos_mren = []
                cartonCount = 0
                config.spindle_id,config.spindle_od,Hight,Longsidecoe,Shortsidecoe,order,rule = GetParameter(carton_numder)
                sdgs = 0
                sdgs1 = project['task']['count']
                #sdgs1 = 24
                sdgs2 = 0
                if project['task']['endAddress'][0]['location'] == "R07":
                    pos_mren.append(np.array([350,-850,183]))
                    pos_mren.append(np.array([100,-850,183]))
                    pos_mren.append(np.array([-150,-850,183]))
                    pos_mren.append(np.array([-400,-850,183]))
                    pos_mren.append(np.array([350,-1100,183]))
                    pos_mren.append(np.array([100,-1100,183]))
                    pos_mren.append(np.array([-150,-1100,183]))
                    pos_mren.append(np.array([-400,-1100,183]))
                    pos_mren.append(np.array([350,-1350,183]))
                    pos_mren.append(np.array([100,-1350,183]))
                    pos_mren.append(np.array([-150,-1350,183]))
                    pos_mren.append(np.array([-400,-1350,183]))
                    config.action = 1
                if project['task']['endAddress'][0]['location'] == "R13":
                    pos_mren.append(np.array([350,850,195]))
                    pos_mren.append(np.array([100,850,195]))
                    pos_mren.append(np.array([-150,850,195]))
                    pos_mren.append(np.array([-400,850,195]))
                    pos_mren.append(np.array([350,1100,195]))
                    pos_mren.append(np.array([100,1100,195]))
                    pos_mren.append(np.array([-150,1100,195]))
                    pos_mren.append(np.array([-400,1100,195]))
                    pos_mren.append(np.array([350,1350,195]))
                    pos_mren.append(np.array([100,1350,195]))
                    pos_mren.append(np.array([-150,1350,195]))
                    pos_mren.append(np.array([-400,1350,195]))
                if config.POS_barcode['z']< -965 and config.POS_barcode['z']>-995 and config.POS_barcode['x']< -184 and config.POS_barcode['x']>-214 and config.POS_barcode['y']< -17 and config.POS_barcode['y']>-37:
                    config.action = 1
                    config.vectorA = config.vectorA*(-982)/config.POS_barcode['z']
                else: 
                    config.action = 999999
                    config.log.logger.info("标定二维码识别错误")

        if config.action == 1:
            if getStep() == False: 
                if carton_dir == 0:
                   vector0 = np.array([1312,100,700])
                   euler0 = { 'u':0, 'v':90, 'w':90 }
                   euler0_0 = { 'u':0, 'v':90, 'w':90 }
                if carton_dir == 1:
                   vector0 = np.array([1312,0,700])
                   euler0 = { 'u':0, 'v':90, 'w':-90 }
                   euler0_0 = { 'u':0, 'v':90, 'w':-90 }
                vector0[2] = vector0[2] + Hight*carton_height

                links = IdentificationAction1(vector0,euler0,1000) 
                config.links = IdentificationCmd1(links,9) 
                
                config.action = 2
                config.box = []
                #config.box.append({'x': -200,'y':-300,'z':-750})
                #config.box.append({'x': 200,'y':-300,'z':-750})
                #config.box.append({'x': 200,'y':300,'z':-750})
                #config.box.append({'x': -200,'y':300,'z':-750})
                
        if config.action == 2:#再次识别纸箱
            if getStep() == False: 
                if len(config.box) >0:
                    angle = math.atan2((config.box[1]['x']-config.box[2]['x']),(config.box[2]['y']-config.box[1]['y']))/math.pi*180
                    vector1 = np.array([-91.291,  35.325, 463.056])#相机偏移
                    vector2 = np.array([(config.box[0]['x']+config.box[1]['x']+config.box[2]['x']+config.box[3]['x'])/4,
                                    (config.box[0]['y']+config.box[1]['y']+config.box[2]['y']+config.box[3]['y'])/4,
                                    (config.box[0]['z']+config.box[1]['z']+config.box[2]['z']+config.box[3]['z'])/4])
                    euler1 = { 'u':euler0['u'], 'v':euler0['v'], 'w':euler0['w']+angle }
                    real_point = GetRealPoint(vector0,vector2,euler0,vector1)
                    twice_ident_point = GetTwiceIdentPoint(real_point,vector1,euler1,-vector2[2])
                    twice_ident_point[2] = vector0[2]
                    vector4 = copy.deepcopy(twice_ident_point)
                    vector60 = copy.deepcopy(twice_ident_point)
                    fanye_euler = copy.deepcopy(euler1)
                    
                    if  config.box[0]['z'] ==0 or config.box[0]['z'] < -886 or config.box[0]['z'] > -700:
                        config.action = 21
                    else:                       
                        links = IdentificationAction1(vector4,euler1,vector4[2]) 
                        config.links = IdentificationCmd1(links,9) 
                        config.action = 3
                        vector0 = copy.deepcopy(vector4) 
                        euler0 = copy.deepcopy(euler1)
                    config.box = []
                    #config.box.append({'x': -200,'y':-300,'z':-750})
                    #config.box.append({'x': 200,'y':-300,'z':-750})
                    #config.box.append({'x': 200,'y':300,'z':-750})
                    #config.box.append({'x': -200,'y':300,'z':-750})                    
                else:
                    config.action = 1
                    
        if config.action == 3:#识别切缝方向
            if getStep() == False: 
                if len(config.box) >0:
                    avgHight = (config.box[0]['z']+ config.box[1]['z'] + config.box[2]['z'] + config.box[3]['z'])/4
                    config.box0 = copy.deepcopy(config.box)
                    angle = math.atan2((config.box[1]['x']-config.box[2]['x']),(config.box[2]['y']-config.box[1]['y']))/math.pi*180
                    if abs(config.box[1]['x']+config.box[3]['x'])>15 or abs(angle)>1.5 or abs(config.box[0]['y']+config.box[2]['y'])>15:
                        vector0 = copy.deepcopy(vector4) 
                        euler0 = copy.deepcopy(euler1)
                        config.action = 2
                    elif avgHight > -860 and avgHight < -760:                      
                        vector40 = GetRealPoint(vector4,np.array([config.box[0]['x'],config.box[0]['y'],config.box[0]['z']]),euler1,vector1)
                        vector41 = GetRealPoint(vector4,np.array([config.box[1]['x'],config.box[1]['y'],config.box[1]['z']]),euler1,vector1)
                        vector42 = GetRealPoint(vector4,np.array([config.box[2]['x'],config.box[2]['y'],config.box[2]['z']]),euler1,vector1)
                        vector43 = GetRealPoint(vector4,np.array([config.box[3]['x'],config.box[3]['y'],config.box[3]['z']]),euler1,vector1)
                                            
                        config.database.insert(str(current_time),config.action*1000+0,config.box0[0]['x'],config.box0[0]['y'],config.box0[0]['z'],vector40[0],vector40[1],vector40[2])
                        config.database.insert(str(current_time),config.action*1000+1,config.box0[1]['x'],config.box0[1]['y'],config.box0[1]['z'],vector41[0],vector41[1],vector41[2])
                        config.database.insert(str(current_time),config.action*1000+2,config.box0[2]['x'],config.box0[2]['y'],config.box0[2]['z'],vector43[0],vector42[1],vector42[2])
                        config.database.insert(str(current_time),config.action*1000+3,config.box0[3]['x'],config.box0[3]['y'],config.box0[3]['z'],vector43[0],vector43[1],vector43[2])

                        vectorLenth = (vector41 - vector42 +vector40 - vector43)/4
                        vectorWidth = (vector41 - vector40 +vector42 - vector43)/4

                        Lenth = (vectorLenth[0]**2+vectorLenth[1]**2+vectorLenth[2]**2)**0.5
                        Width = (vectorWidth[0]**2+vectorWidth[1]**2+vectorWidth[2]**2)**0.5
                        
                        euler1['w'] += angle
                        euler_vis = {'u':0, 'v':90, 'w':euler1['w']-euler0_0['w']}
                        point_left = 0.5*vector42+0.5*vector43
                        point_right = 0.5*vector40+0.5*vector41
                        point_vis = 0.5*point_left+0.5*point_right

                        twice_ident_point = GetTwiceIdentPoint(point_vis,vector1,euler_vis,450)
                        vector5 = copy.deepcopy(twice_ident_point)

                        links = IdentificationAction1(vector5,euler_vis,vector5[2]) 
                        config.links = IdentificationCmd1(links,10) 

                        config.database.insert(str(current_time),100,vector5[0],vector5[1],vector5[2],euler_vis['u'],euler_vis['v'],euler_vis['w'])
                        
                        config.action = 4
                        config.line_box = []
                        #config.line_box.append({'x': 200,'y':0,'z':-400})
                        #config.line_box.append({'x': -200,'y':0,'z':-400})
                else:
                   config.action = 2

        if config.action == 4:
            if getStep() == False: 
                vector_line_centre = []
                xuhao = 0
                angle = math.atan2((config.line_box[0]['y']-config.line_box[1]['y']),(config.line_box[0]['x']-config.line_box[1]['x']))/math.pi*180
                for i in config.line_box:
                    current_time = datetime.now()
                    xuhao += 1
                    vector_vis0 = np.array([i['x'],i['y'],i['z']])
                    real_point = GetRealPoint(vector5,vector_vis0,euler_vis,vector1)
                    vector_line_centre.append(real_point)
                    #config.database.insert(str(current_time),700+ xuhao,vector_vis0[0],vector_vis0[1],vector_vis0[2],vector_pos[0],vector_pos[1],vector_pos[2])
                    config.database.insert(str(current_time),config.action*1000+0,vector_vis0[0],vector_vis0[1],vector_vis0[2],real_point[0],real_point[1],real_point[2])

                if carton_dir == 0:
                    point_left =  vector_line_centre[1]
                    point_right = vector_line_centre[0]
                else:
                    point_left =  vector_line_centre[0]
                    point_right = vector_line_centre[1]

                point_vis = 1*point_left+0*point_right
                point_vis[2] = 1*point_left[2]+0*point_right[2]
                euler1 = copy.deepcopy(euler_vis)
                euler1['w'] = (angle+euler0_0['w']+euler_vis['w'])
                twice_ident_point = GetTwiceIdentPoint(point_vis,vector1,euler1,450)
                vector5 = copy.deepcopy(twice_ident_point)

                links = IdentificationAction1(vector5,euler1,vector5[2]) 
                config.links = IdentificationCmd2(links,11,0) #识别长切缝右侧

                config.database.insert(str(current_time),100,vector5[0],vector5[1],vector5[2],euler1['u'],euler1['v'],euler1['w'])
                config.action = 5
                config.line_box = []
                #for i in range(0,20):
                #    config.line_box.append({'x': 0,'y':175-25*i,'z':-400,'angle':0,'code':0})

        if config.action == 5:
            if getStep() == False:
                flag = 0
                for i in config.line_box:
                    if i['z'] <-500 or i['z'] >-400:
                        flag = 1
                if len(config.line_box) >0  and flag == 0:
                    config.database.insert(str(current_time),101,config.currentPos['x'],config.currentPos['y'],config.currentPos['z'],config.currentPos['u'],config.currentPos['v'],config.currentPos['w'])
                    point_vis = 0*point_left+1*point_right
                    point_vis[2] = 0*point_left[2]+1*point_right[2]
                    twice_ident_point = GetTwiceIdentPoint(point_vis,vector1,euler1,450)
                    vector5_2 = copy.deepcopy(twice_ident_point)
                    line_left = copy.deepcopy(config.line_box)

                    links = IdentificationAction1(vector5_2,euler1,vector5_2[2]) 
                    config.links = IdentificationCmd2(links,11,1) 

                    config.database.insert(str(current_time),102,vector5_2[0],vector5_2[1],vector5_2[2],euler1['u'],euler1['v'],euler1['w'])
                    config.action = 6  
                    config.line_box = []
                    #for i in range(0,20):
                    #    config.line_box.append({'x': 0,'y':287-25*i,'z':-400,'angle':0,'code':1})
                else:
                    config.action = 3

        if config.action == 6:#计算缝隙坐标
            if getStep() == False: 
                flag = 0
                for i in config.line_box:
                    if i['z'] <-500 or i['z'] >-400:
                        flag = 1
                config.database.insert(str(current_time),103,config.currentPos['x'],config.currentPos['y'],config.currentPos['z'],config.currentPos['u'],config.currentPos['v'],config.currentPos['w'])
                if len(config.line_box) >0 and flag == 0:
                    euler10 = { 'u':euler1['u'], 'v':euler1['v'], 'w':euler1['w'] }#切割长缝时刀片的姿态
                    euler10_2 = { 'u':euler10['u'], 'v':euler10['v'], 'w':euler10['w']-euler0_0['w'] }#切割短缝时刀片的姿态
                    #vector10 = np.array([237.193,12.122,318.876])#[-250,4,313]#刀片偏移
                    vector10 = np.array([314.6360173, 4.62224229, 319.45580293])#[-250,4,313]#刀片偏移
                    vector10_2 = revolve(euler10,vector10)#刀片偏移坐标                    

                    line_right = copy.deepcopy(config.line_box)
                    vector_line_left = []
                    vector_line_right = []
                    xuhao = 0

                    for i in line_left:
                        current_time = datetime.now()
                        xuhao += 1
                        vector_vis0 = np.array([i['x'],i['y'],i['z']])
                        real_point = GetRealPoint(vector5,vector_vis0,euler1,vector1)
                        clamp_point = GetThePinchPoint(real_point,euler10,vector10)- np.array([0,0,2])
                        vector_line_left.append(clamp_point)
                        config.database.insert(str(current_time),config.action*1000+200+ xuhao,vector_vis0[0],vector_vis0[1],vector_vis0[2],clamp_point[0],clamp_point[1],clamp_point[2])

                    xuhao = 0
                    for i in line_right:
                        current_time = datetime.now()
                        xuhao += 1
                        vector_vis0 = np.array([i['x'],i['y'],i['z']])
                        real_point = GetRealPoint(vector5_2,vector_vis0,euler1,vector1)
                        clamp_point = GetThePinchPoint(real_point,euler10,vector10)- np.array([0,0,2])
                        vector_line_right.append(clamp_point)
                        config.database.insert(str(current_time),config.action*1000+300+ xuhao,vector_vis0[0],vector_vis0[1],vector_vis0[2],clamp_point[0],clamp_point[1],clamp_point[2])
                    
                    sorted_data = SlitCoordinate(vector_line_left,vector_line_right)

                    vector14 = sorted_data[0]#刀片切割缝隙时左侧端点坐标
                    vector15 = sorted_data[len(sorted_data)-1]#刀片切割缝隙时右侧端点坐标    
                                
                    vector10_3 = revolve(euler10_2,vector10)#切割左侧胶带的刀片偏移
                    vector10_4 = revolve(euler10_2,vector10)#切割右侧胶带的刀片偏移

                    vector31 =revolve(euler10_2,np.array([0,40,0]))#胶带宽度设置为40
                    vector32 =revolve(euler10_2,np.array([0,-40,0]))#胶带宽度设置为40
                                                           
                    vector133 = vector15 + vector10_2 + vector32 - vector10_4#右侧胶带切割终点
                    vector134 = vector15 + vector10_2 + vector31 - vector10_4#右侧胶带切割起点
                    vector135 = vector14 + vector10_2 + vector32 - vector10_3#左侧胶带切割终点
                    vector136 = vector14 + vector10_2 + vector31 - vector10_3#左侧胶带切割起点

                    fanxianghight = (sorted_data[19][2]+sorted_data[20][2]+sorted_data[21][2])/3+vector10_2[2]
                   
                    vector16 = np.array([vector14[0],vector14[1],vector14[2]])
                    derstarthig = sorted_data[1][2] - sorted_data[0][2]
                    derendhig = sorted_data[len(sorted_data)-2][2] - sorted_data[len(sorted_data)-1][2]

                    starhig = vector14[2]
                    starVector = vector14+vector10_2                  
                    endhig = vector15[2]
                    endVector = vector15+vector10_2                    
                    starVector[2] =  fanxianghight
                    endVector[2] =  fanxianghight
                    vectorLenth = (starVector - endVector)/2
                    Lenth = (vectorLenth[0]**2+vectorLenth[1]**2+vectorLenth[2]**2)**0.5
                    config.action = 7
                    #config.action = 10
                else:
                    config.action = 3
                    
        if config.action == 7:#长缝切缝动作
            if getStep() == False:  
                if vector14[2]>125 and vector15[2]>125:#识别高度符合要求执行动作，否则重新识别
                    config.links = SlittingAction(sorted_data,euler10)
                    if len(sorted_data) == 0:
                        config.action = 8
                        qiecount = 2

                
        if config.action == 8:#将右侧切缝分6刀切完
            if getStep() == False:  
                qiecount -= 1
                if(qiecount == 1):
                    vector_qie = np.array([-20,0,0+derendhig])
                else:
                    vector_qie = np.array([-10,0,0])              
                config.links = SlittingAction2(vector133,vector134,vector_qie,euler10_2)
                if(qiecount == 0):
                    qiecount = 2
                    config.action = 9

        if config.action == 9:#将左侧切缝分6刀切完
            if getStep() == False:
                qiecount -= 1
                if(qiecount == 1):
                    vector_qie = np.array([20,0,0+derstarthig])
                else:
                    vector_qie = np.array([10,0,0])               
                config.links = SlittingAction2(vector135,vector136,vector_qie,euler10_2)
                if(qiecount == 0):
                    config.action = 10

        if config.action == 10:#刀片围绕右边缘做翻箱动作
            if getStep() == False: 
                vector_xipan = np.array([3.82524579, 185.32992087, 310.38751022])#翻箱片偏移
                #vector_xipan = np.array([6.41459874,183.64143843,308.92476951])
                vector50 = 0.5*starVector+0.5*endVector#中心点
                #vector50[1] = vector50[1] - frequency*7
                vector53 = np.array([0,Width,0])#旋转偏移
                vector51 = vector50 - revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },vector53)
                vector56 = vector51 - 0.6*revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },np.array([Lenth,0,0]))
                vector53_2 = vector53-np.array([0,40,0])

                vector80 = 0.5*starVector+0.5*endVector - revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },vector53)

                derW = euler1['w']-euler0_0['w']
                firstEuler = { 'u':-90, 'v':15, 'w':-90+derW}
                twiceEuler = { 'u':-90, 'v':0, 'w':-90+derW}
                kaixiangangle = 22.5
                mouldEuler = {  'u':0+kaixiangangle, 'v':0, 'w':derW }

                #按照长边偏移来设定旋转点
                vector51 = vector51 - revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },np.array([ Longsidecoe*Lenth,0,0]))

                if rule == 1:
                    config.action = 200
                else:
                    config.action = 11
                derVector1 = np.array([0,15,-15])
                derVector2 = np.array([0,-20,-20])
                config.links = MouldTurnoverAction(mouldEuler,vector_xipan,vector51,vector53,vector53_2,vector56,firstEuler,twiceEuler,derW,carton_height,derVector1,derVector2)

        if config.action == 200:#前往中心点识别是否翻起，并确认下一片的翻箱点
            if getStep() == False: 
                
                center = copy.deepcopy(0.5*starVector+0.5*endVector)

                vector61 = GetTwiceIdentPoint(center,vector1,euler1,800)
                poss = []
                if carton_height == 2:
                    poss.append({'x':int(-0.038*1000),'y':int(18.407*1000),'z':int(-41.890*1000),'u':int(-0.098*1000),'v':int(23.482*1000),'w':int(0.087*1000)})
                else :
                    poss.append({'x':int(0*1000),'y':int(-1.408*1000),'z':int(-54.165*1000),'u':int(-0.082*1000),'v':int(55.569*1000),'w':int(0.046*1000)})
                poss.append({'x':int(vector61[0]*1000),'y':int(vector61[1]*1000),'z':int(vector61[2]*1000),'u':int(euler1['u']*1000),'v':int(euler1['v']*1000),'w':int(euler1['w']*1000)})  
                config.setLinks.links_action16(poss,Lenth*2,Width*2,0)
                config.action = 201
            
        if config.action == 201:#确认是否翻起
            if getStep() == False: 

                vector_fanye1 = GetRealPoint(vector61,config.point[0][2],euler1,vector1)
                vector_fanye2 = GetRealPoint(vector61,config.point[1][2],euler1,vector1)
                vector_fanye3 = GetRealPoint(vector61,config.point[2][2],euler1,vector1)
                vector_fanye4 = GetRealPoint(vector61,config.point[3][2],euler1,vector1)
                vector_fanye10 = GetRealPoint(vector61,config.point[0][0],euler1,vector1)
                vector_fanye20 = GetRealPoint(vector61,config.point[1][0],euler1,vector1)
                vector_fanye30 = GetRealPoint(vector61,config.point[2][0],euler1,vector1)
                vector_fanye40 = GetRealPoint(vector61,config.point[3][0],euler1,vector1)
                vector_fanye12 = GetRealPoint(vector61,config.point[0][1],euler1,vector1)
                vector_fanye22 = GetRealPoint(vector61,config.point[1][1],euler1,vector1)
                vector_fanye32 = GetRealPoint(vector61,config.point[2][1],euler1,vector1)
                vector_fanye42 = GetRealPoint(vector61,config.point[3][1],euler1,vector1)
                if config.notice1 == 0 and config.notice2 == 0:
                    config.action = 1
                elif carton_dir == 0 and config.notice1 == 0 and config.notice2 == 1:                    
                    if abs(vector_fanye1[2]-fanxianghight)<60:
                        config.action = 11
                elif carton_dir == 1 and config.notice1 == 1 and config.notice2 == 0:
                    if abs(vector_fanye2[2]-fanxianghight)<60:
                        config.action = 11

                if config.action == 201:
                    frequency += 1
                    if frequency == 3:
                        config.action = 9999999999
                    else :
                        config.action = 200

        if config.action == 11:#刀片围绕左边缘做翻箱动作
            if getStep() == False: 

                vector_xipan = np.array([-46.70158978, 183.63014186, 310.40850719])
                vector50 = 0.5*starVector+0.5*endVector

                vector53 = np.array([0,-Width,0])#旋转偏移
                vector51 = vector50 - revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },vector53)#旋转点
                vector56 = vector51 - 0.6*revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },np.array([Lenth,0,0]))

                if rule == 1:#规则的直接使用数据
                    if carton_dir == 0:
                        vector53 = revolve({ 'u':0, 'v':0, 'w':-euler1['w']+euler0_0['w'] }, vector_fanye1-vector51)
                    else:
                        vector53 = revolve({ 'u':0, 'v':0, 'w':-euler1['w']+euler0_0['w'] }, vector_fanye2-vector51)

                    vector51 = vector51 + revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },np.array([vector53[0],0,0]))#旋转点
                    vector53[0] = 0
                else:
                    vector51 = vector51 - revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },np.array([Longsidecoe*Lenth,0,0]))#旋转点
                    vector53[0] = 0

                config.action = 202
                
                vector53_2 = vector53-np.array([0,-40,0])

                derW = euler1['w']-euler0_0['w']
                firstEuler = { 'u':-90, 'v':-15, 'w':-90+derW}
                twiceEuler = { 'u':-90, 'v':15, 'w':-90+derW}
                kaixiangangle = 22.5
                mouldEuler = {  'u':0-kaixiangangle, 'v':0, 'w':derW }

                derVector1 = np.array([0,-20,-15])
                derVector2 = np.array([0,20,-20])
                config.links =  MouldTurnoverAction(mouldEuler,vector_xipan,vector51,vector53,vector53_2,vector56,firstEuler,twiceEuler,derW,carton_height,derVector1,derVector2) 

        if config.action == 202:#识别2，3页翻箱
            if getStep() == False:
                poss = []
                center = copy.deepcopy(0.5*starVector+0.5*endVector)
                vector61 = GetTwiceIdentPoint(center,vector1,euler1,800)

                if carton_height == 2:
                    poss.append({'x':int(-0.038*1000),'y':int(18.407*1000),'z':int(-41.890*1000),'u':int(-0.098*1000),'v':int(23.482*1000),'w':int(0.087*1000)})
                else :
                    poss.append({'x':int(0*1000),'y':int(-1.408*1000),'z':int(-54.165*1000),'u':int(-0.082*1000),'v':int(55.569*1000),'w':int(0.046*1000)})
                poss.append({'x':int(vector61[0]*1000),'y':int(vector61[1]*1000),'z':int(vector61[2]*1000),'u':int(euler1['u']*1000),'v':int(euler1['v']*1000),'w':int(euler1['w']*1000)})  
                config.setLinks.links_action16(poss,Lenth*2,Width*2,1,rule)
                config.action = 203
                
        #if config.action == 203:#识别2，3页翻箱
        #    if getStep() == False:
        #        if config.notice1 == 1 and config.notice2 == 1  and config.notice3 == 0  and config.notice4 == 0:                    
        #            if config.point[2][2] > -850 and config.point[2][2]<-750 and config.point[3][2] > -850 and config.point[3][2]<-750:
        #                config.action = 12
        #            else:
        #                config.action = 200
        #        else:
        #            frequency += 1
        #            if frequency == 3:
        #                config.action = 9999999999
        #            else :
        #                config.action = 202
        if config.action == 203:#识别2，3页翻箱
            if getStep() == False:
                vector_fanye1 = GetRealPoint(vector61,config.point[0][2],euler1,vector1)
                vector_fanye2 = GetRealPoint(vector61,config.point[1][2],euler1,vector1)
                vector_fanye3 = GetRealPoint(vector61,config.point[2][2],euler1,vector1)
                vector_fanye4 = GetRealPoint(vector61,config.point[3][2],euler1,vector1)
                vector_fanye10 = GetRealPoint(vector61,config.point[0][0],euler1,vector1)
                vector_fanye20 = GetRealPoint(vector61,config.point[1][0],euler1,vector1)
                vector_fanye30 = GetRealPoint(vector61,config.point[2][0],euler1,vector1)
                vector_fanye40 = GetRealPoint(vector61,config.point[3][0],euler1,vector1)
                vector_fanye12 = GetRealPoint(vector61,config.point[0][1],euler1,vector1)
                vector_fanye22 = GetRealPoint(vector61,config.point[1][1],euler1,vector1)
                vector_fanye32 = GetRealPoint(vector61,config.point[2][1],euler1,vector1)
                vector_fanye42 = GetRealPoint(vector61,config.point[3][1],euler1,vector1)

                if config.notice1 == 0 and config.notice2 == 0 :
                    config.action = 10
                elif config.notice1 == 1 and config.notice2 == 1  and config.notice3 == 0  and config.notice4 == 0:                    
                    if abs(vector_fanye3[2]-fanxianghight)<60 and abs(vector_fanye4[2]-fanxianghight)<60:
                        config.action = 12
                elif (carton_dir == 0 and config.notice1 == 0 and config.notice2 == 1) or (carton_dir == 1 and config.notice1 == 1 and config.notice2 == 0):
                    if (carton_dir == 0 and abs(vector_fanye1[2]-fanxianghight)<60) or (carton_dir == 1 and abs(vector_fanye2[2]-fanxianghight)<60):
                        config.action = 205
                elif (carton_dir== 0 and config.notice1 == 1 and config.notice2 == 0) or (carton_dir == 1 and config.notice1 == 0 and config.notice2 == 1):
                    if (carton_dir == 0 and abs(vector_fanye2[2]-fanxianghight)<60) or (carton_dir == 1 and abs(vector_fanye1[2]-fanxianghight)<60):
                        config.action = 204
                if config.action == 203:
                    frequency += 1
                    if frequency == 3:
                        config.action = 9999999999
                    else :
                        config.action = 202

        if config.action == 204:#刀片围绕右边缘做翻箱动作
            if getStep() == False: 
                vector_xipan = np.array([3.82524579, 185.32992087, 310.38751022])#翻箱片偏移
                #vector_xipan = np.array([6.41459874,183.64143843,308.92476951])
                vector50 = 0.5*starVector+0.5*endVector#中心点
                #vector50[1] = vector50[1] - frequency*7
                vector53 = np.array([0,Width,0])#旋转偏移
                vector51 = vector50 - revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },vector53)
                vector56 = vector51 - 0.6*revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },np.array([Lenth,0,0]))
                

                vector80 = 0.5*starVector+0.5*endVector - revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },vector53)

                derW = euler1['w']-euler0_0['w']
                firstEuler = { 'u':-90, 'v':15, 'w':-90+derW}
                twiceEuler = { 'u':-90, 'v':0, 'w':-90+derW}
                kaixiangangle = 22.5
                mouldEuler = {  'u':0+kaixiangangle, 'v':0, 'w':derW }

                #使用识别出来的位置作为翻页点
                if carton_dir == 0:
                    #vector53 = revolve({ 'u':0, 'v':0, 'w':-euler1['w']+euler0_0['w'] }, vector_fanye2-vector51)
                    pianyiVector = vector_fanye22 - vector_fanye2
                    vector51 = vector51 + pianyiVector/np.linalg.norm(pianyiVector)*Lenth*Longsidecoe
                    vector53 = revolve({ 'u':0, 'v':0, 'w':-euler1['w']+euler0_0['w'] },vector_fanye2+ pianyiVector/np.linalg.norm(pianyiVector)*Lenth*Longsidecoe-vector51)
                else:
                    #vector53 = revolve({ 'u':0, 'v':0, 'w':-euler1['w']+euler0_0['w'] }, vector_fanye1-vector51)
                    pianyiVector = vector_fanye12 - vector_fanye1
                    vector51 = vector51 + pianyiVector/np.linalg.norm(pianyiVector)*Lenth*Longsidecoe
                    vector53 = revolve({ 'u':0, 'v':0, 'w':-euler1['w']+euler0_0['w'] },vector_fanye1+ pianyiVector/np.linalg.norm(pianyiVector)*Lenth*Longsidecoe-vector51)

                #vector51 = vector51 + revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },np.array([vector53[0],0,0]))#旋转点
                #vector53[0] = 0

                ##按照长边偏移来设定旋转点
                #vector51 = vector51 - revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },np.array([ Longsidecoe*Lenth,0,0]))
                vector53_2 = vector53-np.array([0,40,0])
                config.action = 202
                derVector1 = np.array([0,20,-15])
                derVector2 = np.array([0,-20,-20])
                config.links = MouldTurnoverAction(mouldEuler,vector_xipan,vector51,vector53,vector53_2,vector56,firstEuler,twiceEuler,derW,carton_height,derVector1,derVector2)


        if config.action == 205:#刀片围绕左边缘做翻箱动作
            if getStep() == False: 

                vector_xipan = np.array([-46.70158978, 183.63014186, 310.40850719])
                vector50 = 0.5*starVector+0.5*endVector

                vector53 = np.array([0,-Width,0])#旋转偏移
                vector51 = vector50 - revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },vector53)#旋转点
                vector56 = vector51 - 0.6*revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },np.array([Lenth,0,0]))

                #使用识别出来的位置作为翻页点
                #if carton_dir == 0:
                #    vector53 = revolve({ 'u':0, 'v':0, 'w':-euler1['w']+euler0_0['w'] }, vector_fanye1-vector51)
                #else:
                #    vector53 = revolve({ 'u':0, 'v':0, 'w':-euler1['w']+euler0_0['w'] }, vector_fanye2-vector51)

                #vector51 = vector51 + revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },np.array([vector53[0],0,0]))#旋转点
                #vector53[0] = 0

                if carton_dir == 0:
                    #vector53 = revolve({ 'u':0, 'v':0, 'w':-euler1['w']+euler0_0['w'] }, vector_fanye2-vector51)
                    pianyiVector = vector_fanye12 - vector_fanye1
                    vector51 = vector51 + pianyiVector/np.linalg.norm(pianyiVector)*Lenth*Longsidecoe
                    vector53 = revolve({ 'u':0, 'v':0, 'w':-euler1['w']+euler0_0['w'] },vector_fanye1+ pianyiVector/np.linalg.norm(pianyiVector)*Lenth*Longsidecoe-vector51)
                else:
                    #vector53 = revolve({ 'u':0, 'v':0, 'w':-euler1['w']+euler0_0['w'] }, vector_fanye1-vector51)
                    pianyiVector = vector_fanye22 - vector_fanye2
                    vector51 = vector51 + pianyiVector/np.linalg.norm(pianyiVector)*Lenth*Longsidecoe
                    vector53 = revolve({ 'u':0, 'v':0, 'w':-euler1['w']+euler0_0['w'] },vector_fanye2+ pianyiVector/np.linalg.norm(pianyiVector)*Lenth*Longsidecoe-vector51)

                config.action = 202                
                vector53_2 = vector53-np.array([0,-40,0])

                derW = euler1['w']-euler0_0['w']
                firstEuler = { 'u':-90, 'v':-15, 'w':-90+derW}
                twiceEuler = { 'u':-90, 'v':15, 'w':-90+derW}
                kaixiangangle = 22.5
                mouldEuler = {  'u':0-kaixiangangle, 'v':0, 'w':derW }

                derVector1 = np.array([0,-20,-15])
                derVector2 = np.array([0,20,-20])
                config.links =  MouldTurnoverAction(mouldEuler,vector_xipan,vector51,vector53,vector53_2,vector56,firstEuler,twiceEuler,derW,carton_height,derVector1,derVector2) 

        if config.action == 12:#刀片围绕下边缘做翻箱动作
            if getStep() == False: 
                #如果一叶没有翻过去重新切左右两侧，如果两页都没有翻过去，重新识别纸箱，重新识别切缝，重新翻箱



                derW = euler1['w']-euler0_0['w']
                if carton_dir == 0:
                    firstEuler = { 'u':-90, 'v':-15, 'w':derW}
                    twiceEuler = { 'u':-90, 'v':0, 'w':derW}
                    #vector_xipan = np.array([-48.909,183.037,310.121])#翻箱片偏移
                    vector_xipan = np.array([-46.70158978, 183.63014186, 310.40850719])#翻箱片偏移
                    euler50 = { 'u':0, 'v':0, 'w':euler1['w']}
                    vector50 = 0.5*starVector+0.5*endVector#中心点
                    vector51 = vector51 = vector50 - revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },np.array([Lenth,0,0]))
                    vector53 = np.array([Width,0,0])#旋转偏移                   
                    vector53 = revolve({ 'u':0, 'v':0, 'w':-euler1['w']+euler0_0['w'] }, vector_fanye3-vector51)
                    if rule == 1:
                        vector51 = vector51 + revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },np.array([0,vector53[1],0]))#旋转点
                        vector53[1] = 0
                    else:
                        pianyiVector = vector_fanye32 - vector_fanye3
                        vector51 = vector51 + pianyiVector/np.linalg.norm(pianyiVector)*Width*Shortsidecoe
                        vector53 = revolve({ 'u':0, 'v':0, 'w':-euler1['w']+euler0_0['w'] }, vector_fanye3+pianyiVector/np.linalg.norm(pianyiVector)*Width*Shortsidecoe-vector51)
                        #vector51 = vector51 - revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },np.array([0,Shortsidecoe*Width,0]))#旋转点
                        #vector53[1] = 0 

                if carton_dir == 1:
                    firstEuler = { 'u':-90, 'v':15, 'w':derW-180}
                    twiceEuler = { 'u':-90, 'v':0, 'w':derW-180}                    
                    vector_xipan = np.array([3.82524579, 185.32992087, 310.38751022])#翻箱片偏移
                    vector50 = 0.5*starVector+0.5*endVector#中心点
                    vector51 = vector51 = vector50 - revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },np.array([Lenth,0,0]))
                    vector53 = np.array([Width,0,0])#旋转偏移
                    vector53 = revolve({ 'u':0, 'v':0, 'w':-euler1['w']+euler0_0['w'] },vector_fanye4-vector51)

                    if rule == 1:
                        vector51 = vector51 + revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },np.array([0,vector53[1],0]))#旋转点
                        vector53[1] = 0
                    else:
                        pianyiVector = vector_fanye42 - vector_fanye4
                        vector51 = vector51 + pianyiVector/np.linalg.norm(pianyiVector)*Width*Shortsidecoe
                        vector53 = revolve({ 'u':0, 'v':0, 'w':-euler1['w']+euler0_0['w'] },vector_fanye4+ pianyiVector/np.linalg.norm(pianyiVector)*Width*Shortsidecoe-vector51)
                        #vector51 = vector51 + revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },np.array([0,Shortsidecoe*Width,0]))#旋转点
                        #vector53[1] = 0 

                
                vector56 = vector51 
                vector53_2 = vector53-np.array([40,0,0])
             
                kaixiangangle = 22.5
                mouldEuler = {  'u':0, 'v':0-kaixiangangle, 'w':derW }  
                derVector1 = np.array([20,0,-15])
                derVector2 = np.array([-20,0,-25])
                config.links = MouldTurnoverAction(mouldEuler,vector_xipan,vector51,vector53,vector53_2,vector56,firstEuler,twiceEuler,derW,carton_height,derVector1,derVector2)                
 
                config.action = 13

        if config.action == 13:#刀片围绕上边缘做翻箱动作
            if getStep() == False: 
                
                #vector_xipan = np.array([-250.988,1.971,283.315])#翻箱片偏移
                vector_xipan = np.array([-260.37451458,    3.53112586,  291.55552622])#翻箱片偏移
                derW = euler1['w']-euler0_0['w']
                firstEuler = { 'u':0, 'v':-90, 'w':180+derW}
                vector50 = 0.5*starVector+0.5*endVector#中心点
                vector51 = vector50 + revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },np.array([Lenth,0,0]))
                vector53 = np.array([-Width,0,0])#旋转偏移
                if carton_dir == 0:
                    vector53 =revolve({ 'u':0, 'v':0, 'w':-euler1['w']+euler0_0['w'] }, vector_fanye4 - vector51)
                    if rule == 1:
                        vector51 = vector51 + revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },np.array([0,vector53[1],0]))#旋转点
                        vector53[1] = 0
                    else:
                        pianyiVector = vector_fanye42 - vector_fanye4
                        vector51 = vector51 + pianyiVector/np.linalg.norm(pianyiVector)*Width*Shortsidecoe
                        vector53 =revolve({ 'u':0, 'v':0, 'w':-euler1['w']+euler0_0['w'] }, vector_fanye4+ pianyiVector/np.linalg.norm(pianyiVector)*Width*Shortsidecoe - vector51)
                        #vector51 = vector51 - revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },np.array([0,Shortsidecoe*Width,0]))#旋转点
                        #vector53[1] = 0 

                if carton_dir == 1:
                    vector53 =revolve({ 'u':0, 'v':0, 'w':-euler1['w']+euler0_0['w'] }, vector_fanye3 - vector51)        
                    if rule == 1:
                        vector51 = vector51 + revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },np.array([0,vector53[1],0]))#旋转点
                        vector53[1] = 0
                    else:
                        pianyiVector = vector_fanye32 - vector_fanye3
                        vector51 = vector51 + pianyiVector/np.linalg.norm(pianyiVector)*Width*Shortsidecoe
                        vector53 =revolve({ 'u':0, 'v':0, 'w':-euler1['w']+euler0_0['w'] }, vector_fanye3+ pianyiVector/np.linalg.norm(pianyiVector)*Width*Shortsidecoe - vector51)
                        #vector51 = vector51 + revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },np.array([0,Shortsidecoe*Width,0]))#旋转点
                        #vector53[1] = 0 


                vector56 = vector51 

                twiceEuler = { 'u':0, 'v':-90, 'w':180+derW} 
                vector53_2 = vector53-np.array([-40,0,0])            
                kaixiangangle = 22.5
                mouldEuler = {  'u':0, 'v':0+kaixiangangle, 'w':derW }
                derVector1 = np.array([-20,0,-15])
                derVector2 = np.array([20,0,-25])
                config.links = MouldTurnoverAction(mouldEuler,vector_xipan,vector51,vector53,vector53_2,vector56,firstEuler,twiceEuler,derW,carton_height,derVector1,derVector2)

                config.action = 14

        if config.action == 14:#识别翻页
            if getStep() == False:     
                poss = []
                
                vector0 = copy.deepcopy(vector61)
                euler0 = copy.deepcopy(euler1)
                if carton_height == 2:
                    poss.append({'x':int(-0.038*1000),'y':int(18.407*1000),'z':int(-41.890*1000),'u':int(-0.098*1000),'v':int(23.482*1000),'w':int(0.087*1000)})
                else :
                    poss.append({'x':int(0*1000),'y':int(-1.408*1000),'z':int(-54.165*1000),'u':int(-0.082*1000),'v':int(55.569*1000),'w':int(0.046*1000)})
                #poss.append({'x':int(0*1000),'y':int(-1.408*1000),'z':int(-54.165*1000),'u':int(-0.082*1000),'v':int(55.569*1000),'w':int(0.046*1000)})
                poss.append({'x':int(vector0[0]*1000),'y':int(vector0[1]*1000),'z':int(vector0[2]*1000),'u':int(euler0['u']*1000),'v':int(euler0['v']*1000),'w':int(euler0['w']*1000)})   

                config.setLinks.links_action10(poss)#识别翻页 
                config.links.append({'State':True, 'typeID': 16,'length': Lenth*2, 'width': Width*2,'type1': 1,'rule':rule})
                config.action = 301
                EndPos = {'x':vector0[0],'y':vector0[1],'z':vector0[2],'u':euler0['u'],'v':euler0['v'],'w':euler0['w']}  
                lastPos = copy.deepcopy(EndPos)
                config.circles = []
                frequency = 0
                #dim = Width
                #config.circles.append({'x':dim/2,'y':-dim,'z':-830,'angle':0})
                #config.circles.append({'x':dim/2,'y':0,'z':-830,'angle':0})
                #config.circles.append({'x':dim/2,'y':dim,'z':-830,'angle':0})
                #config.circles.append({'x':-dim/2,'y':-dim,'z':-830,'angle':0})
                #config.circles.append({'x':-dim/2,'y':0,'z':-830,'angle':0})
                #config.circles.append({'x':-dim/2,'y':dim,'z':-830,'angle':0})
        if config.action == 301:#判断叶片是否翻起
            if getStep() == False:  
                vector_fanye1 = GetRealPoint(vector61,config.point[0][2],euler1,vector1)
                vector_fanye2 = GetRealPoint(vector61,config.point[1][2],euler1,vector1)
                vector_fanye3 = GetRealPoint(vector61,config.point[2][2],euler1,vector1)
                vector_fanye4 = GetRealPoint(vector61,config.point[3][2],euler1,vector1)
                vector_fanye10 = GetRealPoint(vector61,config.point[0][0],euler1,vector1)
                vector_fanye20 = GetRealPoint(vector61,config.point[1][0],euler1,vector1)
                vector_fanye30 = GetRealPoint(vector61,config.point[2][0],euler1,vector1)
                vector_fanye40 = GetRealPoint(vector61,config.point[3][0],euler1,vector1)
                vector_fanye12 = GetRealPoint(vector61,config.point[0][1],euler1,vector1)
                vector_fanye22 = GetRealPoint(vector61,config.point[1][1],euler1,vector1)
                vector_fanye32 = GetRealPoint(vector61,config.point[2][1],euler1,vector1)
                vector_fanye42 = GetRealPoint(vector61,config.point[3][1],euler1,vector1)
                if config.notice1 == 1 and config.notice2 == 1  and config.notice3 == 1  and config.notice4 == 1:
                    config.action = 304
                elif config.notice1 == 1 and config.notice2 == 1  and config.notice3 == 0  and config.notice4 == 0:                    
                    if abs(vector_fanye3[2]-fanxianghight)<60  and abs(vector_fanye4[2]-fanxianghight)<60:
                        config.action = 12
                elif (carton_dir == 0 and config.notice3 == 0 and config.notice4 == 1) or (carton_dir == 1 and config.notice3 == 1 and config.notice4 == 0):
                    if (carton_dir == 0 and abs(vector_fanye3[2]-fanxianghight)<60) or (carton_dir == 1 and abs(vector_fanye4[2]-fanxianghight)<60):
                        config.action = 302
                elif (carton_dir == 0 and config.notice3 == 1 and config.notice4 == 0) or (carton_dir == 1 and config.notice3 == 0 and config.notice4 == 1):
                    if (carton_dir == 0 and abs(vector_fanye4[2]-fanxianghight)<60) or (carton_dir == 1 and abs(vector_fanye3[2]-fanxianghight)<60):
                        config.action = 13
                if config.action == 301:
                    frequency += 1
                    if frequency == 3:
                        config.action = 9999999999
                    else :
                        config.action = 14
        if config.action == 302:#翻下页
            if getStep() == False:  
                derW = euler1['w']-euler0_0['w']
                if carton_dir == 0:
                    firstEuler = { 'u':-90, 'v':-15, 'w':derW}
                    twiceEuler = { 'u':-90, 'v':0, 'w':derW}
                    #vector_xipan = np.array([-48.909,183.037,310.121])#翻箱片偏移
                    vector_xipan = np.array([-46.70158978, 183.63014186, 310.40850719])#翻箱片偏移
                    euler50 = { 'u':0, 'v':0, 'w':euler1['w']}
                    vector50 = 0.5*starVector+0.5*endVector#中心点
                    vector51 = vector51 = vector50 - revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },np.array([Lenth,0,0]))
                    vector53 = np.array([Width,0,0])#旋转偏移                   
                    vector53 = revolve({ 'u':0, 'v':0, 'w':-euler1['w']+euler0_0['w'] }, vector_fanye3-vector51)
                    if rule == 1:
                        vector51 = vector51 + revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },np.array([0,vector53[1],0]))#旋转点
                        vector53[1] = 0
                    else:
                        pianyiVector = vector_fanye32 - vector_fanye3
                        vector51 = vector51 + pianyiVector/np.linalg.norm(pianyiVector)*Width*Shortsidecoe
                        vector53 = revolve({ 'u':0, 'v':0, 'w':-euler1['w']+euler0_0['w'] }, vector_fanye3+pianyiVector/np.linalg.norm(pianyiVector)*Width*Shortsidecoe-vector51)
                        #vector51 = vector51 - revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },np.array([0,Shortsidecoe*Width,0]))#旋转点
                        #vector53[1] = 0 

                if carton_dir == 1:
                    firstEuler = { 'u':-90, 'v':15, 'w':derW-180}
                    twiceEuler = { 'u':-90, 'v':0, 'w':derW-180}                    
                    vector_xipan = np.array([3.82524579, 185.32992087, 310.38751022])#翻箱片偏移
                    vector50 = 0.5*starVector+0.5*endVector#中心点
                    vector51 = vector51 = vector50 - revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },np.array([Lenth,0,0]))
                    vector53 = np.array([Width,0,0])#旋转偏移
                    vector53 = revolve({ 'u':0, 'v':0, 'w':-euler1['w']+euler0_0['w'] },vector_fanye4-vector51)

                    if rule == 1:
                        vector51 = vector51 + revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },np.array([0,vector53[1],0]))#旋转点
                        vector53[1] = 0
                    else:
                        pianyiVector = vector_fanye42 - vector_fanye4
                        vector51 = vector51 + pianyiVector/np.linalg.norm(pianyiVector)*Width*Shortsidecoe
                        vector53 = revolve({ 'u':0, 'v':0, 'w':-euler1['w']+euler0_0['w'] },vector_fanye4+ pianyiVector/np.linalg.norm(pianyiVector)*Width*Shortsidecoe-vector51)
                        #vector51 = vector51 + revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },np.array([0,Shortsidecoe*Width,0]))#旋转点
                        #vector53[1] = 0 

                
                vector56 = vector51 
                vector53_2 = vector53-np.array([40,0,0])
             
                kaixiangangle = 22.5
                mouldEuler = {  'u':0, 'v':0-kaixiangangle, 'w':derW }  
                derVector1 = np.array([20,0,-15])
                derVector2 = np.array([-20,0,-25])
                config.links = MouldTurnoverAction(mouldEuler,vector_xipan,vector51,vector53,vector53_2,vector56,firstEuler,twiceEuler,derW,carton_height,derVector1,derVector2)                
 
                config.action = 14

        if config.action == 304:#识别全局纱锭
            if getStep() == False:   
                config.links.append({'State':True, 'typeID': 12})
                config.circles = []
                #config.action = 21
                config.action = 15

        if config.action == 15:
            if getStep() == False:
                for i in range(0,len(config.circles)):
                    config.database.insert(str(current_time),config.action*1000+i,config.circles[i]['x'],config.circles[i]['y'],config.circles[i]['z'],0,0,0)
                if len(order) == len(config.circles):
                    circles2 = copy.deepcopy(config.circles)
                    for i in range(0,len(order)):
                        circles2[i] = config.circles[order[i]]                        
                    config.circles = copy.deepcopy(circles2)
                config.action = 16    
                
        if config.action == 16:#识别放置点位
            if getStep() == False:
                if (len(config.circles) > 0 ) and (len(pos_mren) > 0):                    
                    poss = []
                    if (pos_mren[sdgs][1]>0):
                        euler_putVis = { 'u':0, 'v':90, 'w':90 }
                    else:
                        euler_putVis = { 'u':0, 'v':90, 'w':-90 }     
                    vector20 = pos_mren[sdgs]+revolve(euler_putVis,np.array([285,6.5,315])) - revolve(euler_putVis,np.array([-860,31,440]))
                    hight = max(1000 - (2-carton_height)*Hight,700)
                    startPos = copy.deepcopy(config.currentPos)
                    EndPos = {'x':vector20[0],'y':vector20[1],'z':vector20[2],'u':euler_putVis['u'],'v':euler_putVis['v'],'w':euler_putVis['w']}                     
                    trans,poss_arm = route_planning(startPos,EndPos,hight)
                    lastPos = copy.deepcopy(EndPos)
                    poss = copy.deepcopy(poss_arm)
                    count = len(poss_arm)
                    for i in range(0,7-count):
                        poss.append(poss_arm[count-1])                       
                    poss.append({'x':int(vector20[0]*1000),'y':int(vector20[1]*1000),'z':int(600*1000),'u':int(euler_putVis['u']*1000),'v':int(euler_putVis['v']*1000),'w':int(euler_putVis['w']*1000)})
                    config.links = config.setLinks.links_action22(poss)
                    config.links.append({'State':True, 'typeID': 14})
                    config.action = 17   
                else:
                    config.action = 1000
                    #pos_mren.remove(pos_mren[0])

        if config.action == 17:#识别放置点，若上方有东西改放置位置
            if getStep() == False: 
                if config.hight > 1500:
                   sdgs+=6
                   config.action = 16
                else:
                   config.action = 18
                   xuhao = 0

        if config.action == 18:#识别单个纱锭
            if getStep() == False:
                if len(config.circles) > 0 :     
                    #vector1 = np.array([-85.718,33.191,462.78])#相机偏移
                    vector1 = np.array([-91.291,  35.325, 463.056])#相机偏移

                    vector2 = np.array([config.circles[0]['x'],config.circles[0]['y'],config.circles[0]['z']])
                    real_point = GetRealPoint(vector0,vector2,euler0,vector1)
                    twice_ident_point = GetTwiceIdentPoint(real_point,vector1,euler0,400)
                    vector4 = copy.deepcopy(twice_ident_point)
                    vector4[2] = vector0[2] -360

                    links = IdentificationAction1(vector4,euler0, hight) 
                    config.links = IdentificationCmd1(links,13) 
                    config.circles.remove(config.circles[0])
                    
                    if sdgs1 == sdgs2 :
                        config.action = 100
                    else :
                        config.action = 19
                else:    
                    euler83 = { 'u':0, 'v':90, 'w':0+derW }

                    twice_ident_point = GetTwiceIdentPoint(vector80,vector1,euler83,500)
                    vector82 = copy.deepcopy(twice_ident_point)
                    links = IdentificationAction1(vector82,euler83, hight) 
                    config.links = IdentificationCmd3(links,17,Lenth*2,Width*2)
                    config.action = 20

        if config.action == 19:#纱锭抓放动作
            if getStep() == False:

                if config.circle['z'] != 0:

                    euler10 =  copy.deepcopy(euler1)
                    vector13 = np.array([config.circle['x'],config.circle['y'],config.circle['z']])
                    #vector12 =  np.array([272,12,323])#[297.50410206,   0.72790701, 303.92396606] 
                    vector12 =  np.array([275,-3.68,307.7]) 
                    real_point = GetRealPoint(vector4,vector13,euler10,vector1)
                    clamp_point = GetThePinchPoint(real_point,euler10,vector12)
                    vector16 = copy.deepcopy(clamp_point)

                    if (pos_mren[sdgs][1]>0):
                        euler_putVis = { 'u':0, 'v':90, 'w':90 }
                    else:
                        euler_putVis = { 'u':0, 'v':90, 'w':-90 }    

                    poss = []
                    #800
                    poss.append({'x':int(vector16[0]*1000),'y':int(vector16[1]*1000),'z':int(vector4[2]*1000),'u':int(euler10['u']*1000),'v':int(euler10['v']*1000),'w':int(euler10['w']*1000)})
                    #806
                    poss.append({'x':int(vector16[0]*1000),'y':int(vector16[1]*1000),'z':int(vector16[2]*1000),'u':int(euler10['u']*1000),'v':int(euler10['v']*1000),'w':int(euler10['w']*1000)})
                   
                    hight = 1170 - (2-carton_height)*Hight
                    startPos = {'x':vector16[0],'y':vector16[1],'z': hight,'u':euler10['u'],'v':euler10['v'],'w':euler10['w']}
                    EndPos = {'x':pos_mren[sdgs][0],'y':pos_mren[sdgs][1],'z': hight,'u':euler_putVis['u'],'v':euler_putVis['v'],'w':euler_putVis['w']}               
                    trans,poss_arm = route_planning3(startPos,EndPos,hight)
                    #poss = copy.deepcopy(poss_arm)
                    count = len(poss_arm)
                    for i in poss_arm:
                        poss.append(i) 

                    #842
                    poss.append({'x':int(pos_mren[sdgs][0]*1000),'y':int(pos_mren[sdgs][1]*1000),'z':int(pos_mren[sdgs][2]*1000),'u':int(euler_putVis['u']*1000),'v':int(euler_putVis['v']*1000),'w':int(euler_putVis['w']*1000)})
                    
                    EndPos = {'x':pos_mren[sdgs][0],'y':pos_mren[sdgs][1],'z':pos_mren[sdgs][2],'u':euler_putVis['u'],'v':euler_putVis['v'],'w':euler_putVis['w']}  
                    lastPos = copy.deepcopy(EndPos)
                    config.setLinks.links_action13(poss)
                    
                    vector74 = np.array([pos_mren[sdgs][0],pos_mren[sdgs][1],600])

                    #UPFSdata = {
                    #    "progress": str(sdgs2+1)+"/"+str(sdgs1),
                    #    "describe":"A",
                    #    "palletInformation":project['task']['palletInformation']
                    #    }
                    #config.rcs.reportProgress("reportProgress",project['number'],UPFSdata) 

                    sdgs += 1
                    sdgs2 += 1

                    config.action = 18
                else: 
                    config.action = 18

        if config.action == 20:#抓箱子放0置动作
            if getStep() == False:
                if carton_dir == 0:
                   euler70 = { 'u':0, 'v':90, 'w':derW }
                   vector71 = np.array([140,-3.68,308.059])
                   #vector71 = np.array([110,6.5,320])
                   

                if carton_dir == 1:
                    euler70 = { 'u':0, 'v':90, 'w':derW }
                    vector71 = np.array([140,-3.68,308.059])
                    
                   
                vector85 = np.array([config.grab['x'],config.grab['y'],config.grab['z']])  
                vector85_2 = revolve({ 'u':0, 'v':0, 'w':derW }, config.vectorA@vector85)
                vector86 = np.array([-94.182,29,440.5])

                real_point = GetRealPoint(vector82,vector85,euler70,vector86)
                clamp_point = GetThePinchPoint(real_point,euler70,vector71)
                vector72 = copy.deepcopy(clamp_point)


                #vector86_2 = revolve(euler83, vector86)
                #vector87 = vector82+vector86_2+vector85_2-revolve(euler70, vector71)                    
                #vector72 = vector80-revolve(euler70, vector71)
                vector73 = np.array([-872,867,316])
                vector75 = np.array([-1438,867,316])

                #vector72 = vector87

                carton = []               
                carton.append(np.array([0,0,0]))
                carton.append(np.array([0,0,320]))

                vector75 = vector75+carton[carton0%2]
                poss = []
                if carton_height ==0:
                    poss.append({'x':int(35.002*1000),'y':int(-2.235*1000),'z':int(-53.306*1000),'u':int(40.270*1000),'v':int(62.361*1000),'w':int(-21.455*1000)})
                elif carton_height ==1:
                    poss.append({'x':int(34.999*1000),'y':int(15.682*1000),'z':int(-43.685*1000),'u':int(56.094*1000),'v':int(43.621*1000),'w':int(-38.126*1000)})
                elif carton_height ==2 :
                    poss.append({'x':int(34.999*1000),'y':int(15.682*1000),'z':int(-43.685*1000),'u':int(56.094*1000),'v':int(43.621*1000),'w':int(-38.126*1000)})
                poss.append({'x':int(vector72[0]*1000),'y':int((vector72[1]-3)*1000),'z':int((vector72[2]+200)*1000),'u':int(euler70['u']*1000),'v':int(euler70['v']*1000),'w':int(euler70['w']*1000)})
                poss.append({'x':int(vector72[0]*1000),'y':int((vector72[1]-3)*1000),'z':int((vector72[2]+100)*1000),'u':int(euler70['u']*1000),'v':int(euler70['v']*1000),'w':int(euler70['w']*1000)})
               
                                              
                
                
                if carton0%2 == 1 or carton0 == 0:
                #if carton0%2 == 1:
                    poss.append({'x':int(vector75[0]*1000),'y':int(vector75[1]*1000),'z':int((900)*1000),'u':int((-90)*1000),'v':int(90000),'w':int(0)})
                    poss.append({'x':int(vector74[0]*1000),'y':int(vector74[1]*1000),'z':int((700)*1000),'u':int(-90000),'v':int(90000),'w':int(0)})
                    poss.append({'x':int(vector75[0]*1000),'y':int(vector75[1]*1000),'z':int((vector75[2])*1000),'u':int((-90)*1000),'v':int(90000),'w':int(0)})
                    poss.append({'x':int(vector75[0]*1000),'y':int(vector75[1]*1000),'z':int((vector75[2])*1000),'u':int((-90)*1000),'v':int(90000),'w':int(0)})
                else :
                    poss.append({'x':int(vector73[0]*1000),'y':int(vector73[1]*1000),'z':int((900)*1000),'u':int((-90)*1000),'v':int(90000),'w':int(0)})
                    poss.append({'x':int(vector74[0]*1000),'y':int(vector74[1]*1000),'z':int((700)*1000),'u':int(-90000),'v':int(90000),'w':int(0)})
                    poss.append({'x':int(vector73[0]*1000),'y':int(vector73[1]*1000),'z':int((vector73[2])*1000),'u':int((-90)*1000),'v':int(90000),'w':int(0)})
                    poss.append({'x':int(vector75[0]*1000),'y':int(vector75[1]*1000),'z':int((vector75[2])*1000),'u':int((-90)*1000),'v':int(90000),'w':int(0)})

                hight = 950
                startPos = {'x':vector72[0],'y':vector72[1],'z': hight,'u':0,'v':90,'w':0}
                EndPos = {'x':vector73[0],'y':vector73[1],'z': hight,'u':0,'v':90,'w':90}               
                trans,poss_arm = route_planning(startPos,EndPos,hight)
                #poss = copy.deepcopy(poss_arm)
                count = len(poss_arm)
                for i in poss_arm:
                    poss.append(i) 
                for i in range(0,7-count):
                    poss.append(poss_arm[count-1]) 

                config.setLinks.links_action14(poss)

                carton0 +=1
                if carton0 == 7:
                    config.action = 102
                else:
                    config.action = 21
        if config.action == 21:#循环
            if getStep() == False:
                cartonCount += 1

                if carton_height >= 0 :
                    if carton_dir == 0 :
                        carton_dir = 1
                    else: 
                        carton_dir = 0
                        carton_height -= 1
                    config.action = 1
                if carton_height == -1:
                    config.action = 100

                if sdgs1 <= sdgs2 :
                    config.action = 100


                #if cartonCount == 2:
                #    config.action = 99999999

        if config.action == 101:#纱锭托盘满
            if getStep() == False:
                sdgs = 0

        if config.action == 100: #结束回复
            if getStep() == False:
                #UPFSdata = {
                #        "result": "pass",
                #        "codeList":[],
                #        "count":sdgs2,
                #        "palletInformation":project['task']['palletInformation']
                #        }
                #link = {'number':project['number'],'data':UPFSdata,'type':"taskStartFeedback",'typeID':"11",'buttonName':"feedback"}
                #config.rcs.unpackingSpoolFeedback(link)        
                #time.sleep(1)
                #config.rcs.CurrentStatus = "Idle"
                flag_a = 0
                for pallet in project['task']['palletInformation']:
                    if pallet['location'] == "R06":
                        pallet['count'] = max(0,pallet['count']-sdgs2)
                        if sdgs2 != 0 :
                            if pallet['count'] == 0:
                                pallet['stateList'] = ["empty"]
                            else:
                                pallet['stateList'] = ["Non-empty"]
                            pallet['countList'] = [pallet['count']]
                    if pallet['location'] == project['task']['endAddress'][0]['location']:
                        pallet['count'] += sdgs2
                        pallet['countList'] = [pallet['count']]
                        if pallet['count'] == 0:
                             pallet['stateList'] = ["empty"]
                        elif sdgs2 >= 12:
                             pallet['stateList'] = ["full"]
                        else:
                             pallet['stateList'] = ["Non-empty"]
                        flag_a = 1

                #found = any(pallet['location'] == "R1" for pallet project['task']['palletInformation'])
                if flag_a == 0:
                        empty = {
                        "location" :project['task']['endAddress'][0]['location'],
                        "number" :"",
                        "fuction":"put",
                        "count":sdgs2,
                        "stateList":["Non-empty"],
                        "countList":[sdgs2],
                        "Lock":"false"
                        }
                        if empty['count'] == 0:
                            empty['stateList'] = ["empty"]
                        elif sdgs2 >= 12:
                            pallet['stateList'] = ["full"]
                        else:
                            empty['stateList'] = ["Non-empty"]
                        project['task']['palletInformation'].append(empty)

                UPFSdata = {
                "result": "pass",
                "codeList":[],
                "count":sdgs2,
                "palletInformation":project['task']['palletInformation']
                }

                link = {'number':project['number'],'data':UPFSdata,'type':"taskStartFeedback",'typeID':"11",'buttonName':"feedback"}
                config.rcs.unpackingSpoolFeedback(link)         
                time.sleep(1)
                config.rcs.CurrentStatus = "Idle"


                config.action = 133
                if carton_height == -1:
                    config.action = 99999999

        if config.action == 102:#纸箱托盘满
            if getStep() == False:
                carton0 = 0
                config.action = 300
        time.sleep(0.01)
     

def main():
    # 读取配置
    config.reparam()
    # 初始化状态机
    config.sys_state()
    # 初始化LOG
    config.loginit()
    # 初始化线程

    # 机械臂
    Thread(target=SCARAMain,daemon=True).start()
    # 视觉
   # Thread(target=RealsenseRun,daemon=True).start()
    # 发送接收处理
    Thread(target=MainRun,daemon=True).start()



    mainthread = Thread(target=RCSConn,daemon=True)
    mainthread.start()
    mainthread.join()
    


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        config.log.logger.info("Main Error:" + str(e.args))
