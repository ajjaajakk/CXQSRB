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
from RCSnew import RCSServer,RobotData


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
        # config.log.logger.info('SCARA Error:' + str(e.args))
        pass
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
        if config.manageConn.Visual_spindle_pos(): #识别中缝点
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

def RCS(stateList3, stateList4, robot, robot2,A):
    stateList3 -= 1
    stateList4 += 1
    robot.cc += 1
    robot2.cc = robot.cc
    if robot.stateList1 == "empty" and 0 < stateList3 < A:
        robot.stateList1 = "half_full"
        robot2.stateList1 = robot.stateList1
    if robot.stateList1 == "empty" and stateList3 >= A:
        robot.stateList1 = "full"
        robot2.stateList1 = robot.stateList1
    if robot.stateList1 == "full" and 0 < stateList3 < A:
        robot.stateList1 = "half_full"
        robot2.stateList1 = robot.stateList1
    if robot.stateList1 == "full" and stateList3 == 0:
        robot.stateList1 = "empty"
        robot2.stateList1 = robot.stateList1
    if robot.stateList1 == "half_full" and stateList3 == 0:
        robot.stateList1 = "empty"
        robot2.stateList1 = robot.stateList1
    if robot.stateList1 == "half_full" and stateList3 >= A:
        robot.stateList1 = "full"
        robot2.stateList1 = robot.stateList1

    if robot.stateList2 == "empty" and 0 < stateList4 < A:
        robot.stateList2 = "half_full"
        robot2.stateList2 = robot.stateList2
    if robot.stateList2 == "empty" and stateList4 >= A:
        robot.stateList2 = "full"
        robot2.stateList2 = robot.stateList2
    if robot.stateList2 == "full" and 0 < stateList4 < A:
        robot.stateList2 = "half_full"
        robot2.stateList2 = robot.stateList2
    if robot.stateList2 == "full" and stateList4 == 0:
        robot.stateList2 = "empty"
        robot2.stateList2 = robot.stateList2
    if robot.stateList2 == "half_full" and stateList4 == 0:
        robot.stateList2 = "empty"
        robot2.stateList2 = robot.stateList2
    if robot.stateList2 == "half_full" and stateList4 >= A:
        robot.stateList2 = "full"
        robot2.stateList2 = robot.stateList2

    return stateList3,stateList4


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

def inverse_solution(euler_tar,vector_tar):
    JS = []
    # a = np.array([0,0,494.6])
    # b = np.array([0,0,730.870])
    # c = np.array([826.042,0,99.301])
    # d = np.array([117.000,0,0])
    # d2 = np.array([0,0,117.000])
    a = np.array([169.588,0.498,494.6])#(X1ecc,-Y1ecc,Z)
    # a = np.array([169.588,0.498,494.6])#(X1ecc,-Y1ecc,Z)
    b = np.array([0,0,730.870])        #(0,0,L23)
    c = np.array([826.042,0,99.301])   #(L34b,0,L34a)
    d = np.array([164.00,0,0])         #(L56,0,0)
    d2 = np.array([0,0,164.00])        #(0,0,L56)

    P2 = vector_tar - revolve(euler_tar,d2)
    P2_L = (P2[0]**2+P2[1]**2)**0.5
    P2_angle = math.atan2(P2[1],P2[0])/math.pi*180
    # P2_der_angle = math.asin(a[1]/P2_L)/math.pi*180
    # 防止除以零和asin域外错误
    if P2_L < 0.001:
        config.log.logger.warning(f"route_planning: P2_L过小({P2_L})，避免除以零")
        P2_der_angle = 0
    else:
        asin_arg = a[1]/P2_L
        # 限制asin参数在[-1,1]范围内
        if asin_arg > 1:
            asin_arg = 1
        elif asin_arg < -1:
            asin_arg = -1
        P2_der_angle = math.asin(asin_arg)/math.pi*180

    J1 = P2_angle - P2_der_angle

    P1 = revolve({'u':0,'v':0,'w':J1},a)
    P3 = P2-P1

    h = P3[2]
    l = (P3[0]**2 + P3[1]**2)**0.5

    l1 = b[2]
    l2 = (c[0]**2+c[2]**2)**0.5
    l3 = (P3[0]**2+P3[1]**2+P3[2]**2)**0.5

    if (l1+l2<l3) or (l1+l3<l2) or (l2+l3<l1):
        return False,"Error1"

    angle1 = math.acos((l2**2 + l3**2 -l1**2)/(2*l2*l3))/math.pi*180
    angle2 = math.acos((l1**2 + l3**2 -l2**2)/(2*l1*l3))/math.pi*180
    angle3 = math.acos((l1**2 + l2**2 -l3**2)/(2*l1*l2))/math.pi*180
    J2 = math.asin(h/l3)/math.pi*180+angle2-90
    J3 = angle3 - (90+math.atan(c[2]/c[0])/math.pi*180)
    T1 = rotation_matrix({'u':0,'v':0,'w':J1})
    T2 = rotation_matrix({'u':0,'v':-J2,'w':0})
    T3 = rotation_matrix({'u':0,'v':-J3,'w':0})
    T0 = rotation_matrix({'u':0,'v':90,'w':0})
    T_tar = rotation_matrix(euler_tar)
    T12 = np.dot(T1, T2)
    T123 = np.dot(T12, T3)
    T123I = (np.asmatrix(T123)).I
    T0I = (np.asmatrix(T0)).I
    T456 = np.array(T123I@T_tar@T0I)

    J51 = math.acos(T456[0,0])/math.pi*180
    J52 = -math.acos(T456[0,0])/math.pi*180

    S51 = math.sin(J51/180*math.pi)
    S52 = math.sin(J52/180*math.pi)

    if(abs(T456[0,0] -1)>0.0001):
        J41 = math.atan2(-T456[1,0]/S51,T456[2,0]/S51)/math.pi*180
        J42 = math.atan2(-T456[1,0]/S52,T456[2,0]/S52)/math.pi*180
        J61 = math.atan2(-T456[0,1]/S51,-T456[0,2]/S51)/math.pi*180
        J62 = math.atan2(-T456[0,1]/S52,-T456[0,2]/S52)/math.pi*180

        JS.append([J1,J2,J3,J41,J51,J61])
        JS.append([J1,J2,J3,J42,J52,J62])

    else:
        J41 = 0
        J42 = 180
    
        if(T456[2,1] == 0):
            J61 = J41
            J62 = J42
        else:
            J61 = math.atan2(T456[2,1],T456[1,1])/math.pi*180       
            J62 = math.atan2(T456[2,1],T456[1,1])/math.pi*180 
    
        JS.append([J1,J2,J3,J41,J51,J61])
        JS.append([J1,J2,J3,J42,J52,J62])

    JS2 = []
    print(f"JS关节: {JS}")
    # config.log.logger.info(f"JS关节: {JS}")
    tolerance = 0  # 浮点精度容差
    for i in JS:
        flag = 0
        # if i[0]>=170 or i[0]<=-170:
        if i[0]>=170 or i[0]<=-170:
            config.log.logger.info(f"JS关节1: {i[0]} 超限")
            flag = 1
        if i[1]>=65+tolerance or i[1]<=-140-tolerance:
            config.log.logger.info(f"JS关节2: {i[1]} 超限")
            flag = 1
        # if i[2]>=95+tolerance or i[2]<=-80-tolerance:
        if i[2]>=110+tolerance or i[2]<=-70-tolerance:
            config.log.logger.info(f"JS关节3: {i[2]} 超限")
            flag = 1
        if i[3]>=180+tolerance or i[3]<=-180-tolerance:
            config.log.logger.info(f"JS关节4: {i[3]} 超限")
            flag = 1
        if i[4]>=114.5+tolerance or i[4]<=-114.5-tolerance:
            config.log.logger.info(f"JS关节5: {i[4]} 超限")
            flag = 1
        if i[5]>=360+tolerance or i[5]<=-360-tolerance:
            config.log.logger.info(f"JS关节6: {i[5]} 超限")
            flag = 1
        if flag == 0:
            JS2.append(i)

    if len(JS2) != 0:
        config.log.logger.info(f"JS2关节: {JS2}")
        return True,JS2
    else:
        config.log.logger.warning(f"JS失败: {JS}")
        return False,JS

def forward_solution(joints):
    """正向运动学：关节角度 -> 末端位姿（世界坐标）
    joints: [J1, J2, J3, J4, J5, J6] in degrees
    returns: (vector_tar, euler_tar)
    """
    J1, J2, J3, J4, J5, J6 = joints

    a = np.array([169.588, 0.498, 494.6])   # 基座偏移
    b = np.array([0, 0, 730.870])            # 连杆2-3
    c = np.array([826.042, 0, 99.301])       # 连杆3-4
    d2 = np.array([0, 0, 164.00])            # 工具偏移

    # 旋转矩阵
    T1 = rotation_matrix({'u':0, 'v':0, 'w':J1})
    T2 = rotation_matrix({'u':0, 'v':-J2, 'w':0})
    T3 = rotation_matrix({'u':0, 'v':-J3, 'w':0})
    T0 = rotation_matrix({'u':0, 'v':90, 'w':0})
    # T456 = Rx(J4) @ Ry(-J5) @ Rx(J6)
    T456 = np.dot(np.dot(rotation_matrix({'u':J4, 'v':0, 'w':0}),
                         rotation_matrix({'u':0, 'v':-J5, 'w':0})),
                  rotation_matrix({'u':J6, 'v':0, 'w':0}))

    # 末端姿态 T_tar = T1 @ T2 @ T3 @ T456 @ T0
    T_tar = np.dot(np.dot(np.dot(np.dot(T1, T2), T3), T456), T0)

    # 提取欧拉角 (rotation_matrix = Rz(w) @ Ry(v) @ Rx(u))
    u = math.atan2(T_tar[2,1], T_tar[2,2]) / math.pi * 180
    v = math.atan2(-T_tar[2,0], math.sqrt(T_tar[2,1]**2 + T_tar[2,2]**2)) / math.pi * 180
    w = math.atan2(T_tar[1,0], T_tar[0,0]) / math.pi * 180
    euler_tar = {'u':u, 'v':v, 'w':w}

    # 位置计算：腕部中心 = 基座偏移 + 连杆b + 连杆c
    P1 = revolve({'u':0, 'v':0, 'w':J1}, a)
    b_rot = revolve({'u':0, 'v':0, 'w':J1}, revolve({'u':0, 'v':-J2, 'w':0}, b))
    c_rot = revolve({'u':0, 'v':0, 'w':J1}, revolve({'u':0, 'v':-J2, 'w':0}, revolve({'u':0, 'v':-J3, 'w':0}, c)))
    P2 = P1 + b_rot + c_rot  # 腕部中心

    # 末端位置 = 腕部中心 + 工具偏移
    vector_tar = P2 + revolve(euler_tar, d2)

    return vector_tar, euler_tar

def get_dynamic_transition_poss0(default_poss0, max_diff=200):
    """动态生成过渡关节位置poss[0]
    将default_poss0（关节坐标）转换为世界坐标，与当前机械臂x比较
    如果x轴差距超过max_diff，生成中间过渡点并转换为关节坐标
    否则使用默认的固定关节位置
    """
    try:
        # 从default_poss0提取关节角度
        joints = [
            default_poss0['x'] / 1000.0,
            default_poss0['y'] / 1000.0,
            default_poss0['z'] / 1000.0,
            default_poss0['u'] / 1000.0,
            default_poss0['v'] / 1000.0,
            default_poss0['w'] / 1000.0
        ]

        # 正向运动学：关节角度 -> 世界坐标
        target_vector, target_euler = forward_solution(joints)

        current_x = config.currentPos['x']
        target_x = target_vector[0]
        x_diff = abs(current_x - target_x)

        if x_diff > max_diff:
            # x差距过大，生成中间过渡点
            if current_x > target_x:
                mid_x = current_x - max_diff
            else:
                mid_x = current_x + max_diff

            mid_vector = np.array([mid_x, target_vector[1], target_vector[2]])
            success, js = inverse_solution(target_euler, mid_vector)
            if success and len(js) > 0:
                joint = js[0]
                config.log.logger.info(f"动态过渡点: 当前x={current_x:.1f}, 目标x={target_x:.1f}, 中间x={mid_x:.1f}")
                return {
                    'x': int(joint[0]*1000),
                    'y': int(joint[1]*1000),
                    'z': int(joint[2]*1000),
                    'u': int(joint[3]*1000),
                    'v': int(joint[4]*1000),
                    'w': int(joint[5]*1000)
                }
            else:
                config.log.logger.warning(f"动态过渡点逆解失败, 使用默认位置: x_diff={x_diff:.1f}")
        else:
            # x轴差距未超过max_diff，无需生成过渡点，记录当前x和目标x
            config.log.logger.info(f"动态过渡点: 当前x={current_x:.1f}, 目标x={target_x:.1f}, x差={x_diff:.1f}未超{max_diff}mm, 使用默认位置")
    except Exception as e:
        config.log.logger.warning(f"get_dynamic_transition_poss0异常: {e}")

    # 使用默认的固定关节位置
    return default_poss0

def CheckLimit(EndPos, action_name=""):
    # 如果配置中关闭了限位检查，直接返回True
    if config.CHECK_LIMIT == 0:
        return True

    euler_tar = {'u':EndPos['u'] / 1000,'v':EndPos['v'] / 1000,'w':EndPos['w'] / 1000}
    vector_tar = np.array([EndPos['x'] / 1000,EndPos['y'] / 1000,EndPos['z'] / 1000])
    result = inverse_solution(euler_tar,vector_tar)
    if result[0] == True:
        print("目标位置正常")
        return True
    else:
        error_info = f" 限位报警: {action_name} 目标位置超限"
        error_info += f"\n  目标位姿: x={vector_tar[0]}, y={vector_tar[1]}, z={vector_tar[2]}, u={euler_tar['u']}, v={euler_tar['v']}, w={euler_tar['w']}"
        error_info += f"\n  逆解结果: {result[1]}"
        config.log.logger.warning(error_info)
        print(error_info)
        return False

# ==================== 限位预测与回退 ====================

# 关节限位范围
JOINT_LIMITS = {
    1: (-170, 170),
    2: (-140, 65),
    3: (-70, 110),
    4: (-180, 180),
    5: (-114.5, 114.5),
    6: (-360, 360),
}

def CheckPoseValid(x, y, z, u, v, w):
    """快速检查一个位姿（单位：米/度）是否在关节限位内"""
    euler_tar = {'u': u, 'v': v, 'w': w}
    vector_tar = np.array([x, y, z])
    result = inverse_solution(euler_tar, vector_tar)
    return result[0]

def GetOverLimitJoints(x, y, z, u, v, w):
    """返回超限的关节编号列表"""
    euler_tar = {'u': u, 'v': v, 'w': w}
    vector_tar = np.array([x, y, z])
    result = inverse_solution(euler_tar, vector_tar)
    if result[0]:
        return []
    
    over_joints = []
    for js in result[1]:
        j_vals = js
        for j_idx, (jmin, jmax) in JOINT_LIMITS.items():
            if j_vals[j_idx - 1] >= jmax or j_vals[j_idx - 1] <= jmin:
                if j_idx not in over_joints:
                    over_joints.append(j_idx)
    return over_joints

def FindSafeAxisValue(axis, fixed_vals, euler, current_val, search_range=200, precision=0.5):
    """
    保持其他 5 个分量不变，在 current_val ± search_range 内二分查找 axis 的安全值。
    优先往减小方向搜，不行再往增大方向搜。
    
    axis: 'x', 'y', 'z' — 要调整的轴
    fixed_vals: dict — 其他轴的值 {'x':..., 'y':..., 'z':...}（不含当前轴）
    euler: dict — {'u':..., 'v':..., 'w':...}
    current_val: float — 当前轴的值（毫米）
    search_range: float — 搜索范围（毫米），默认 ±200mm
    precision: float — 二分精度（毫米），默认 0.5mm
    
    返回: (found, safe_val)
    """
    x = fixed_vals.get('x', 0)
    y = fixed_vals.get('y', 0)
    z = fixed_vals.get('z', 0)
    u, v, w = euler['u'], euler['v'], euler['w']

    def is_valid(val):
        if axis == 'x':
            return CheckPoseValid(val, y, z, u, v, w)
        elif axis == 'y':
            return CheckPoseValid(x, val, z, u, v, w)
        elif axis == 'z':
            return CheckPoseValid(x, y, val, u, v, w)
        return False

    # 如果当前值已有效，直接返回
    if is_valid(current_val):
        return True, current_val

    def binary_search(valid_val, invalid_val):
        """
        二分法找valid_val和invalid_val之间的安全临界值。
        valid_val 必须是有效的（不限位），invalid_val 必须是无效的（限位）。
        返回的是最靠近 invalid_val 的那个安全值。
        """
        if valid_val < invalid_val:
            # 有效值较小，往增大方向搜，返回最大的有效值
            low, high = valid_val, invalid_val
            for _ in range(50):
                mid = (low + high) / 2
                if is_valid(mid):
                    low = mid
                else:
                    high = mid
                if high - low < precision:
                    return low
            return low
        else:
            # 有效值较大，往减小方向搜，返回最小的有效值
            low, high = invalid_val, valid_val
            for _ in range(50):
                mid = (low + high) / 2
                if is_valid(mid):
                    high = mid
                else:
                    low = mid
                if high - low < precision:
                    return high
            return high

    # 1. 优先往减小方向搜（x更小的方向）
    step_mm = 100  # 粗搜步长 100mm
    low_end = current_val - search_range
    low = current_val
    
    for _ in range(int(search_range / step_mm) + 1):
        low -= step_mm
        if low < low_end:
            break
        if is_valid(low):
            # low有效，current_val无效，有效值较小 → valid_val < invalid_val
            return True, binary_search(low, current_val)

    # 2. 减小方向无效，尝试增大方向（x更大的方向）
    high_end = current_val + search_range
    high = current_val
    
    for _ in range(int(search_range / step_mm) + 1):
        high += step_mm
        if high > high_end:
            break
        if is_valid(high):
            # high有效，current_val无效，有效值较大 → valid_val > invalid_val
            return True, binary_search(high, current_val)

    config.log.logger.warning(f"FindSafeAxisValue: {axis}轴在 {current_val:.1f}mm ±{search_range}mm 内全无效")
    return False, None


def AdjustPosByLimit(EndPos, action_name="", adjust_axis='x'):
    """
    对超限位姿，在指定的 adjust_axis 轴 ±200mm 内查找安全值。
    必须指定 adjust_axis，不会自动切换其他轴。
    
    adjust_axis: 'x', 'y', 'z' — 只调整这一个轴
    
    返回: (adjusted, new_EndPos_dict) — adjusted=False 时 new_EndPos_dict 为原始值
    """
    if config.CHECK_LIMIT == 0:
        return True, EndPos

    if CheckLimit(EndPos, action_name):
        return True, EndPos

    # 单位转换
    x = EndPos['x'] / 1000.0
    y = EndPos['y'] / 1000.0
    z = EndPos['z'] / 1000.0
    u = EndPos['u'] / 1000.0
    v = EndPos['v'] / 1000.0
    w = EndPos['w'] / 1000.0

    fixed_vals = {'x': x, 'y': y, 'z': z}
    cur_val = fixed_vals.pop(adjust_axis)

    found, safe_val = FindSafeAxisValue(adjust_axis, fixed_vals, {'u': u, 'v': v, 'w': w}, cur_val)

    if found and safe_val is not None and abs(safe_val - cur_val) > 0.0005:
        new_pos = dict(EndPos)
        new_pos[adjust_axis] = int(safe_val * 1000)

        info = f"限位回退: {action_name} {adjust_axis}轴 {EndPos[adjust_axis]/1000:.1f}mm → {safe_val:.1f}mm"
        config.log.logger.info(info)
        print(info)

        if CheckLimit(new_pos, action_name):
            return True, new_pos

    error_info = f"限位回退失败: {action_name} {adjust_axis}轴在 {EndPos[adjust_axis]/1000:.0f}mm ±200mm 内无法找到安全值"
    config.log.logger.warning(error_info)
    print(error_info)
    return False, EndPos

# ==================== 限位预测与回退 END ====================

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
    
    for j in poss_arm:
        if not CheckLimit(j, "route_planning3"):
            config.log.logger.warning(f"目标位置 {j} 超限route_planning3")
    
    return poss,poss_arm

def route_planning3_cw(startPos,EndPos,hight,lower_x=650,n_points=4):
    """
    顺时针旋转路径规划（w角度递减方向）。
    适用场景：放置到左托盘(R07等)，w需要从90→0→-90方向递减旋转。
    """
    poss = []

    vector_start = np.array([startPos['x'],startPos['y'],startPos['z']])
    euler_start = {'u':startPos['u'],'v':startPos['v'],'w':startPos['w']}
    vector_end = np.array([EndPos['x'],EndPos['y'],EndPos['z']])
    euler_end = {'u':EndPos['u'],'v':EndPos['v'],'w':EndPos['w']}
    t_start = revolve(euler_start,np.array([0,0,100]))
    t_end = revolve(euler_end,np.array([0,0,100]))
    w_start = math.atan2(t_start[1],t_start[0])/math.pi*180
    w_end = math.atan2(t_end[1],t_end[0])/math.pi*180
    # 归一化到 [0, 360)
    # w_start = w_start % 360
    # w_end = w_end % 360
    # # 强制顺时针（递减）：如果目标角度大于起始角度，减360使其递减
    # if w_end > w_start:

    # 强制顺时针（递减）：若目标角度大于起始，减360使其递减
    w_diff = w_end - w_start
    if w_diff > 0:
        w_end -= 360
    w_point_start = math.atan2(startPos['y'],startPos['x'])/math.pi*180
    w_point_end = math.atan2(EndPos['y'],EndPos['x'])/math.pi*180
    r_start = (startPos['x']**2+startPos['y']**2)**0.5
    r_end = (EndPos['x']**2+EndPos['y']**2)**0.5

    #point = copy.deepcopy(startPos)
    #point['z'] = hight
    #poss.append(point)
    
    for i in range(0,n_points):
        point = {'x':0,'y':0,'z':0,'u':0,'v':90,'w':0} 
        w_point = w_point_start + (w_point_end - w_point_start)/n_points*(i)
        r = r_start +(r_end -r_start)/n_points*(i)
        point['x'] = r*math.cos(w_point/180*math.pi)
        point['y'] = r*math.sin(w_point/180*math.pi)
        if point['x'] < lower_x and hight > 1100:
            point['z'] = 1000
        else:
            point['z'] = hight
        point['w'] = w_start + (w_end - w_start)/n_points*(i)
        poss.append(point)
        
    point = copy.deepcopy(EndPos)
    if point['x'] < lower_x and hight > 1100:
        point['z'] = 1000
    else:
        point['z'] = hight
    poss.append(point)
    poss_arm = []
    for i in poss:
        poss_arm.append({'x':int(i['x']*1000),'y':int(i['y']*1000),'z':int(i['z']*1000),'u':int(i['u']*1000),'v':int(i['v']*1000),'w':int(i['w']*1000)})
        print(i)
    
    for j in poss_arm:
        if not CheckLimit(j, "route_planning3_cw"):
            config.log.logger.warning(f"目标位置 {j} 超限route_planning3_cw")
    
    return poss,poss_arm


def route_planning3_ccw(startPos,EndPos,hight,lower_x=650,n_points=4):
    """
    逆时针旋转路径规划（w角度递增方向）。
    适用场景：放置到右托盘(R13等)，w需要从90→180→270(-90)方向递增旋转。
    """
    poss = []

    vector_start = np.array([startPos['x'],startPos['y'],startPos['z']])
    euler_start = {'u':startPos['u'],'v':startPos['v'],'w':startPos['w']}
    vector_end = np.array([EndPos['x'],EndPos['y'],EndPos['z']])
    euler_end = {'u':EndPos['u'],'v':EndPos['v'],'w':EndPos['w']}
    t_start = revolve(euler_start,np.array([0,0,100]))
    t_end = revolve(euler_end,np.array([0,0,100]))
    w_start = math.atan2(t_start[1],t_start[0])/math.pi*180
    w_end = math.atan2(t_end[1],t_end[0])/math.pi*180
    # 归一化到 [0, 360)
    # w_start = w_start % 360
    # w_end = w_end % 360
    # # 强制逆时针（递增）：如果目标角度小于起始角度，加360使其递增
    # if w_end < w_start:

    # 强制逆时针（递增）：若目标角度小于起始，加360使其递增
    w_diff = w_end - w_start
    if w_diff < 0:
        w_end += 360
    w_point_start = math.atan2(startPos['y'],startPos['x'])/math.pi*180
    w_point_end = math.atan2(EndPos['y'],EndPos['x'])/math.pi*180
    r_start = (startPos['x']**2+startPos['y']**2)**0.5
    r_end = (EndPos['x']**2+EndPos['y']**2)**0.5

    #point = copy.deepcopy(startPos)
    #point['z'] = hight
    #poss.append(point)

    for i in range(0,n_points):
        point = {'x':0,'y':0,'z':0,'u':0,'v':90,'w':0} 
        w_point = w_point_start + (w_point_end - w_point_start)/n_points*(i)
        r = r_start +(r_end -r_start)/n_points*(i)
        point['x'] = r*math.cos(w_point/180*math.pi)
        point['y'] = r*math.sin(w_point/180*math.pi)
        if point['x'] < lower_x and hight > 1100:
            point['z'] = 1000
        else:
            point['z'] = hight
        point['w'] = w_start + (w_end - w_start)/n_points*(i)
        poss.append(point)
        
    point = copy.deepcopy(EndPos)
    if point['x'] < lower_x and hight > 1100:
        point['z'] = 1000
    else:
        point['z'] = hight
    poss.append(point)
    poss_arm = []
    for i in poss:
        poss_arm.append({'x':int(i['x']*1000),'y':int(i['y']*1000),'z':int(i['z']*1000),'u':int(i['u']*1000),'v':int(i['v']*1000),'w':int(i['w']*1000)})
        print(i)
    
    for j in poss_arm:
        if not CheckLimit(j, "route_planning3_ccw"):
            config.log.logger.warning(f"目标位置 {j} 超限route_planning3_ccw")
    
    return poss,poss_arm

def route_planning3_auto(startPos,EndPos,hight,preferred='cw',lower_x=None,n_points=4):
    """
    自适应旋转路径规划：优先按指定方向，若中间点超限则自动回退到反向。
    preferred: 'cw' 顺时针优先(R07等), 'ccw' 逆时针优先(R13等)
    """
    # 首选方向
    cw_lower = 650 if lower_x is None else lower_x
    ccw_lower = 650 if lower_x is None else lower_x
    if preferred == 'cw':
        poss, poss_arm = route_planning3_cw(startPos, EndPos, hight, cw_lower, n_points)
    else:
        poss, poss_arm = route_planning3_ccw(startPos, EndPos, hight, ccw_lower, n_points)
    
    # 检查中间点是否超限
    all_ok = True
    for j in poss_arm:
        if not CheckLimit(j, "route_planning3_auto"):
            all_ok = False
            break
    
    if not all_ok:
        config.log.logger.info(f"首选方向({preferred})超限，自动回退到反向")
        if preferred == 'cw':
            poss, poss_arm = route_planning3_ccw(startPos, EndPos, hight, ccw_lower, n_points)
        else:
            poss, poss_arm = route_planning3_cw(startPos, EndPos, hight, cw_lower, n_points)
        
        for j in poss_arm:
            if not CheckLimit(j, "route_planning3_auto"):
                config.log.logger.warning(f"目标位置 {j} 超限(双向均超限route_planning3_auto)")
    
    return poss, poss_arm

def route_planning4(startPos,EndPos,hight):

    poss = []

    vector_start = np.array([startPos['x'],startPos['y'],startPos['z']])
    euler_start = {'u':startPos['u'],'v':startPos['v'],'w':startPos['w']}
    vector_end = np.array([EndPos['x'],EndPos['y'],EndPos['z']])
    euler_end = {'u':EndPos['u'],'v':EndPos['v'],'w':EndPos['w']}
    t_start = revolve(euler_start,np.array([0,0,100]))
    t_end = revolve(euler_end,np.array([0,0,100]))
    w_start = math.atan2(t_start[1],t_start[0])/math.pi*180
    w_end = math.atan2(t_end[1],t_end[0])/math.pi*180
    # 角度最短路径修正：确保 |w_end - w_start| <= 180，且中间值不超出 [0, 360)
    w_diff = w_end - w_start
    if w_diff > 180:
        w_end_test = w_end - 360
        if w_end_test >= 0:  # 最短路径不会产生负角度，可以走捷径
            w_end = w_end_test
    elif w_diff < -180:
        w_end_test = w_end + 360
        if w_end_test <= 360:  # 最短路径不会超出360，可以走捷径
            w_end = w_end_test
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
    
    for j in poss_arm:
        if not CheckLimit(j, "route_planning4"):
            config.log.logger.warning(f"目标位置 {j} 超限route_planning4")
    
    return poss,poss_arm
    

def route_planning_cw(startPos,EndPos,hight):
    """顺时针(w递减)，6个中间点"""
    poss = []

    vector_start = np.array([startPos['x'],startPos['y'],startPos['z']])
    euler_start = {'u':startPos['u'],'v':startPos['v'],'w':startPos['w']}
    vector_end = np.array([EndPos['x'],EndPos['y'],EndPos['z']])
    euler_end = {'u':EndPos['u'],'v':EndPos['v'],'w':EndPos['w']}
    t_start = revolve(euler_start,np.array([0,0,100]))
    t_end = revolve(euler_end,np.array([0,0,100]))
    w_start = math.atan2(t_start[1],t_start[0])/math.pi*180
    w_end = math.atan2(t_end[1],t_end[0])/math.pi*180
    # 强制顺时针（递减）：若 w_end > w_start，减360使其递减
    if w_end > w_start:
        w_end -= 360
    w_point_start = math.atan2(startPos['y'],startPos['x'])/math.pi*180
    w_point_end = math.atan2(EndPos['y'],EndPos['x'])/math.pi*180
    r_start = (startPos['x']**2+startPos['y']**2)**0.5
    r_end = (EndPos['x']**2+EndPos['y']**2)**0.5

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


def route_planning_ccw(startPos,EndPos,hight):
    """逆时针(w递增)，6个中间点"""
    poss = []

    vector_start = np.array([startPos['x'],startPos['y'],startPos['z']])
    euler_start = {'u':startPos['u'],'v':startPos['v'],'w':startPos['w']}
    vector_end = np.array([EndPos['x'],EndPos['y'],EndPos['z']])
    euler_end = {'u':EndPos['u'],'v':EndPos['v'],'w':EndPos['w']}
    t_start = revolve(euler_start,np.array([0,0,100]))
    t_end = revolve(euler_end,np.array([0,0,100]))
    w_start = math.atan2(t_start[1],t_start[0])/math.pi*180
    w_end = math.atan2(t_end[1],t_end[0])/math.pi*180
    # 强制逆时针（递增）：若 w_end < w_start，加360使其递增
    if w_end < w_start:
        w_end += 360
    w_point_start = math.atan2(startPos['y'],startPos['x'])/math.pi*180
    w_point_end = math.atan2(EndPos['y'],EndPos['x'])/math.pi*180
    r_start = (startPos['x']**2+startPos['y']**2)**0.5
    r_end = (EndPos['x']**2+EndPos['y']**2)**0.5

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


def route_planning(startPos,EndPos,hight):
    """
    自适应旋转路径规划(6中间点)：优先CW(递减)，若中间点超限自动回退CCW(递增)。
    """
    # 首选顺时针
    poss, poss_arm = route_planning_cw(startPos, EndPos, hight)
    
    # 检查中间点是否超限
    all_ok = True
    for j in poss_arm:
        if not CheckLimit(j, "route_planning_auto"):
            all_ok = False
            break
    
    if not all_ok:
        config.log.logger.info("CW路径超限，自动回退CCW")
        poss, poss_arm = route_planning_ccw(startPos, EndPos, hight)
        
        for j in poss_arm:
            if not CheckLimit(j, "route_planning_auto"):
                config.log.logger.warning(f"目标位置 {j} 超限(双向均超限route_planning)")
    
    return poss, poss_arm


#视觉自检，自标定
def StarStartUpPreparation():
    action = 0
    ##1.013538046,0.014249271,0.021339918,   -0.012247965,1.017577204,-0.008829735,    -0.014586829,0.016555877,1.021206479,
    vectorA = config.vectorA
    #440.5351145	31.38990992	85.48878011

    # vector1 = np.array([-91.291,  35.325, 463.056])#相机偏移
    #gui6.2
    vector1 = np.array([-132.465,  -37.636,  463.242])#相机偏移
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
                vectorVisBarcode = np.array([583,1101,135])  # 抬高80mm：55→135
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
                
                # 相机参数对比日志
                config.log.logger.info(f"视觉自检-相机参数对比:")
                config.log.logger.info(f"  相机偏移: {vector1}")
                config.log.logger.info(f"  识别点: {vectorVisBarcode}")
                config.log.logger.info(f"  POS_barcode原始: [{config.POS_barcode['x']},{config.POS_barcode['y']},{config.POS_barcode['z']}]")
                config.log.logger.info(f"  recvVisBarcode计算值: {recvVisBarcode}")
                config.log.logger.info(f"  vectorPosBarcode最终: {vectorPosBarcode}")
                
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


def MatchCartonByMaterial(materialID):
    material_mapping = {
        "11010222": 26,   # 百宏 09R8883D
        "11020065": 27,   # 百宏 85F4616
        "11010186": 28,   # 鑫森 GDF76H505
        "11010225": 24,   # 嘉华 AS40341-ZXK
        "11010103": 25,   # 盛虹 S095/M030
        "1": 30,   
    }
    if materialID in material_mapping:
        return material_mapping[materialID]
    else:
        config.log.logger.info(f"未找到物料ID {materialID} 的映射，使用默认值 carton_numder=1")
        return 1

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
    Longsidecoe = 0 #
    Shortsidecoe = 0
    rule = 0
    count = 0
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
    if carton_numder == 23:               #鑫森78drex/48f DTY全消光（环保纱）
        spindle_od = 140
        spindle_id = 130
        Hight = 310
        Longsidecoe = 0.22
    if carton_numder == 24:               #嘉华 AS40341-ZXK
        spindle_od = 210
        spindle_id = 65
        Hight = 300
        count = 6
        Longsidecoe = 0.22
        # count = 1
        # order = np.array([0,3,2,5,1,4])
        order = np.array([0,2,1,3,4,5])
        # order = np.array([0,1,4,5,2,3])

    if carton_numder == 25:               #盛虹 11010103
        spindle_od = 235
        spindle_id = 65
        Hight = 305
        count = 6
        Longsidecoe = 0.22
        # order = np.array([0,3,2,5,1,4])
        # order = np.array([0,3,2,5,1,4])
        order = np.array([0,2,1,3,4,5])
        # order = np.array([0,1,4,5,2,3])
    if carton_numder == 26:               #百宏 09R8883D 11010222
        spindle_od = 200
        spindle_id = 70
        Hight = 295
        count = 7
        Longsidecoe = 0.22
        # order = np.array([0,1,5,6,2,3,4])
        # order = np.array([0,1,2,3,4,5,12,13,14,15,16,17,6,7,8,9,10,11])
    if carton_numder == 27:               #百宏 11020065 85F4616
        spindle_od = 330
        spindle_id = 135
        Hight = 98
        count = 4
        Longsidecoe = 0.22
        # order = np.array([0,1,5,6,2,3,4])
    if carton_numder == 28:               #鑫森 11010186 GDF76H505
        spindle_od = 215
        spindle_id = 65
        Hight = 290
        count = 6
        # order = np.array([0,1,4,5,2,3])
        Longsidecoe = 0.22
        order = np.array([0,2,1,3,4,5])
        # order = np.array([0,3,2,5,1,4])
        # order = np.array([0,1,5,6,2,3,4])
    if carton_numder == 30:               #盛虹 11010103
        # spindle_od = 235
        # spindle_id = 65
        # Hight = 305
        # count = 1
        # Longsidecoe = 0.22
        spindle_od = 210
        spindle_id = 65
        Hight = 300
        count = 4
        Longsidecoe = 0.22
        # count = 1
    if carton_numder == 10000:               #A-17鑫森33/36 DTY全消光（环保纱）
        spindle_od = 205
        spindle_id = 65
        Hight = 316

    return spindle_id,spindle_od,Hight,Longsidecoe,Shortsidecoe,order,rule,count

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
    for p in poss:
        if not CheckLimit(p, "IdentificationAction1"):
            return False
    if config.currentPos['ID'] == 4:
        links = config.setLinks.links_action22(poss)
        # input("暂停")
    else:
        links = config.setLinks.links_action2(poss)
    return links
def IdentificationAction2(ident_point,ident_euler,hight):
    poss = []               
    #hight = 950
    startPos = copy.deepcopy(config.currentPos)
    EndPos = {'x':ident_point[0],'y':ident_point[1],'z':hight,'u':ident_euler['u'],'v':ident_euler['v'],'w':ident_euler['w']}               
    trans,poss_arm = route_planning(startPos,EndPos,hight)
    poss = copy.deepcopy(poss_arm)
    poss.append({'x':int(ident_point[0]*1000),'y':int(ident_point[1]*1000),'z':int(ident_point[2]*1000),'u':int(ident_euler['u']*1000),'v':int(ident_euler['v']*1000),'w':int(ident_euler['w']*1000)}) 
    for p in poss:
        if not CheckLimit(p, "IdentificationAction2"):
            return False
    # links = config.setLinks.links_action2(poss)
    # return links
    if config.currentPos['ID'] == 4:
        links = config.setLinks.links_action22(poss)
        # input("暂停")
    else:
        links = config.setLinks.links_action2(poss)
    return links

def IdentificationAction3(ident_point,ident_euler,hight):
    poss = []               
    #hight = 950
    startPos = copy.deepcopy(config.currentPos)
    EndPos = {'x':ident_point[0],'y':ident_point[1],'z':hight,'u':ident_euler['u'],'v':ident_euler['v'],'w':ident_euler['w']}               
    trans,poss_arm = route_planning3_auto(startPos,EndPos,hight,lower_x=0,n_points=6)
    poss = copy.deepcopy(poss_arm)
    poss.append({'x':int(ident_point[0]*1000),'y':int(ident_point[1]*1000),'z':int(ident_point[2]*1000),'u':int(ident_euler['u']*1000),'v':int(ident_euler['v']*1000),'w':int(ident_euler['w']*1000)}) 
    for p in poss:
        if not CheckLimit(p, "IdentificationAction3"):
            return False
    # links = config.setLinks.links_action2(poss)
    # return links
    if config.currentPos['ID'] == 4:
        links = config.setLinks.links_action22(poss)
        # input("暂停")
    else:
        links = config.setLinks.links_action2(poss)
    return links
#纯旋转动作（不变位置，只旋转姿态，不经过route_planning避免限位）
def RotationAction(ident_point,ident_euler,hight):
    poss = []
    #第1点：在高处旋转到目标姿态
    poss.append({'x':int(ident_point[0]*1000),'y':int(ident_point[1]*1000),'z':int(hight*1000),'u':int(ident_euler['u']*1000),'v':int(ident_euler['v']*1000),'w':int(ident_euler['w']*1000)})
    #第2点：下降到目标高度
    poss.append({'x':int(ident_point[0]*1000),'y':int(ident_point[1]*1000),'z':int(ident_point[2]*1000),'u':int(ident_euler['u']*1000),'v':int(ident_euler['v']*1000),'w':int(ident_euler['w']*1000)})
    links = config.setLinks.links_action2(poss)
    return links
#切缝动作
def SlittingAction(sorted_data,euler10):
    poss = []               
    if len(sorted_data) == 40:
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
            singlepos = sorted_data[0]- np.array([0,0,6])
            poss.append({'x':int(singlepos[0]*1000),'y':int(singlepos[1]*1000),'z':int(singlepos[2]*1000),'u':int(euler10['u']*1000),'v':int(euler10['v']*1000),'w':int(euler10['w']*1000)})  
            sorted_data.remove(sorted_data[0])
    elif len(sorted_data) == 30:       
        for i in range (0,15):                        
            singlepos = sorted_data[0] - np.array([0,0,6])
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
    for i in range(0,len(poss)):
        ok, adj_p = AdjustPosByLimit(poss[i], "SlittingAction", adjust_axis='x')
        if not ok:
            return False
        if adj_p != poss[i]:
            poss[i] = adj_p
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
    vector44 = ([0,0,-23,0,0,0])#下降深度
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
    for i in range(0,len(poss)):
        # 跳过索引7和8（下降深度和抬高高度），它们是相对偏移量，不是绝对坐标
        if i == 7 or i == 8:
            continue
        ok, adj_p = AdjustPosByLimit(poss[i], "SlittingAction2", adjust_axis='x')
        if not ok:
            return False
        if adj_p != poss[i]:
            poss[i] = adj_p
    links = config.setLinks.links_action5(poss)
    return links

#翻箱动作
def MouldTurnoverAction(mouldEuler,vector_xipan,vector51,vector53,vector53_2,vector56,firstEuler,twiceEuler,derW,carton_height,derVector1,derVector2):
    euler2 = firstEuler

    vector_xipan_2 = revolve(euler2,vector_xipan)
    vector54 = vector51 + revolve({ 'u':0, 'v':0, 'w':derW},vector53)
    vector70 = vector54 - vector_xipan_2

    poss = []
    # 动态生成过渡关节位置，限制x轴移动距离不超过200mm
    default_poss0 = {'x':int(-0.038*1000),'y':int(17.407*1000),'z':int(-35.890*1000),'u':int(-0.078*1000),'v':int(34.234*1000),'w':int(0.052*1000)}
    poss.append(get_dynamic_transition_poss0(default_poss0))

    poss.append({'x':int((vector70[0]+derVector1[0])*1000),'y':int((vector70[1]+derVector1[1])*1000),'z':int((vector70[2]+250)*1000),'u':int(euler2['u']*1000),'v':int((euler2['v'])*1000),'w':int((euler2['w'])*1000)})
    poss.append({'x':int((vector70[0]+derVector1[0])*1000),'y':int((vector70[1]+derVector1[1])*1000),'z':int((vector70[2]+derVector1[2])*1000),'u':int(euler2['u']*1000),'v':int((euler2['v'])*1000),'w':int((euler2['w'])*1000)})
    poss.append({'x':int((vector70[0]+derVector2[0])*1000),'y':int((vector70[1]+derVector2[1])*1000),'z':int((vector70[2]+derVector2[2])*1000),'u':int(euler2['u']*1000),'v':int((euler2['v'])*1000),'w':int((euler2['w'])*1000)})

    vector53 = vector53_2
                
    mouldEulerLIst = []
    # 使用非线性递增：前面角度小，后面角度大，总角度保持不变
    # 使用平方函数：(i/8)^2 * 8，这样前面步长小，后面步长大
    for i in range(0,9):
        # 非线性因子：使用平方函数实现前小后大
        nonlinear_factor = (i / 8.0) ** 1.5 * 8  # 1.5次方，比线性更平缓的开始
        mouldEulerLIst.append({ 'u':mouldEuler['u']*nonlinear_factor, 'v':mouldEuler['v']*nonlinear_factor, 'w':mouldEuler['w'] })     
        
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

    # vector54 = vector51 + revolve(mouldEulerLIst[8],vector53)
    vector54 = vector56 + revolve(mouldEulerLIst[8],vector53) #GAI
    vector70 = vector54 - vector_xipan_2    
    poss.append({'x':int(vector70[0]*1000),'y':int(vector70[1]*1000),'z':int((vector70[2]+10)*1000),'u':int(euler2['u']*1000),'v':int((euler2['v'])*1000),'w':int((euler2['w'])*1000)})

    vector_xipan_2 = revolve({ 'u':euler2['u'], 'v':euler2['v'], 'w':euler2['w'] },vector_xipan)
    vector53 = (100/((vector53[0]**2+vector53[1]**2)**0.5))*vector53#
    #vector54 = vector51 + revolve(mouldEulerLIst[1]*10,vector53)
    # vector54 = vector51 + revolve( {'u':mouldEulerLIst[1]['u']*10, 'v':mouldEulerLIst[1]['v']*10, 'w':mouldEulerLIst[1]['w']*10 },vector53)
    vector54 = vector56 + revolve( {'u':mouldEuler['u']*10, 'v':mouldEuler['v']*10, 'w':mouldEuler['w']*10 },vector53)
    vector71 = vector54 - vector_xipan_2  

    poss.append({'x':int(vector71[0]*1000),'y':int(vector71[1]*1000),'z':int((vector71[2]+10)*1000),'u':int(euler2['u']*1000),'v':int(euler2['v']*1000),'w':int((euler2['w'])*1000)})            
    poss.append({'x':int(vector70[0]*1000),'y':int(vector70[1]*1000),'z':int((vector70[2]+10)*1000),'u':int(euler2['u']*1000),'v':int(euler2['v']*1000),'w':int((euler2['w'])*1000)})
    poss.append({'x':int(vector70[0]*1000),'y':int(vector70[1]*1000),'z':int((vector70[2]+250)*1000),'u':int(euler2['u']*1000),'v':int(euler2['v']*1000),'w':int((euler2['w'])*1000)})
    poss.append({'x':int(0),'y':int(0),'z':int(0),'u':int(0),'v':int(0),'w':int(0)})
    for i in range(0,len(poss)):
        # 跳过全零的占位符位置
        if poss[i]['x'] == 0 and poss[i]['y'] == 0 and poss[i]['z'] == 0:
            continue
        # poss[0]是关节坐标过渡点(非笛卡尔位姿),其合法性已由get_dynamic_transition_poss0
        # 内部的inverse_solution保证,此处不能用CheckLimit做笛卡尔逆解校验,否则会误报超限
        if i == 0:
            continue
        success = CheckLimit(poss[i], "MouldTurnoverAction")
        if not success:
            return False
    links = config.setLinks.links_action8(poss) 
    return links

def IdentificationCmd1(links,typeID):
    links.append({'State':True, 'typeID': typeID})
    return links

def IdentificationCmd2(links,typeID,direction):
    links.append({'State':True, 'typeID': typeID, 'dir': direction}) 
    return links

def IdentificationCmd3(links,typeID,length,width,carton_dir=0):
    links.append({'State':True, 'typeID': typeID,'length': length, 'width': width, 'carton_dir': carton_dir})
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
    a = RobotData()
    rcs = RCSServer(a,host='0.0.0.0', port=23311)
    rcs.start()
    rcs2 = RCSServer(a,host='0.0.0.0', port=23310)
    rcs2.start() 
    time.sleep(1)
    pos_mren = []
    poss = []
    a = 0
    current_time = datetime.now()
    #config.database.insert(str(current_time),1,1,2,3,4,5,6)
    #pos_mren = StarStartUpPreparation()
    while True:
        if a == 0:
            project = rcs.business_queue.get()
            rcs2.act_parameter = project['act_parameter']
            print(rcs2.act_parameter)
            rcs2.act_id = rcs.act_id
            rcs2.act_name = rcs.act_name
            print(project)
            #time.sleep(1)
            if project['act_name'] == 'CXQS':
                rcs2.act_parameter = rcs.act_parameter
                rcs2.act_id = rcs.act_id
                rcs2.act_name = rcs.act_name
                stateList3 = project['act_parameter']['startAddress'][0]['count']
                stateList4 = project['act_parameter']['endAddress'][0]['count']
                rcs2.act_parameter = rcs.act_parameter
                rcs2.progress = str(0) + "/" + str(project['act_parameter']['count'])
                rcs2.act_status = 2
                rcs2.arm_status = 1
                rcs.progress = str(0) + "/" + str(project['act_parameter']['count'])
                rcs.act_status = 2
                rcs.arm_status = 1
                rcs.cc = 0
                rcs2.cc = rcs.cc
                rcs2.stateList1 = rcs.stateList1
                rcs2.stateList2 = rcs.stateList2
                materialID = project['act_parameter']['materialID']
                config.carton_numder = MatchCartonByMaterial(materialID)
                config.log.logger.info(f"物料ID: {materialID}, 匹配纸箱类型: {config.carton_numder}")
                
                break
    while True:
        current_time = datetime.now()
        #config.links =[]#-------------------------------------------------

        if config.camera_offline and config.action not in [0, 1000, 1001]:
            config.log.logger.error("相机掉线，任务终止!")
            config.action = 1001
            continue
        
        if config.action == 0: 
            if getStep() == False: 
                
                carton_dir = 0  #0是开左侧箱，1是开右侧箱
                carton_height = 2 #0表示第一层，1表示第二层......
                count = 0
                carton0 = 0 #表示当前放空纸箱的托盘上一共有几个纸箱
                sdgs = 0 #表示托盘上一共有几个纱锭
                zxgs = 0
                cartonCount = 0
                after_place = False
                #config.links = []
                #config.links.append({'State':True, 'typeID': 16,'length': 574, 'width': 381,'type1': 1,'rule':0})
                config.action = 133

        if config.action == 133:
            if getStep() == False:  
                #config.rcs.sender = "UNB"
                #project = config.rcs.unpackingSpoolQueue.get()
                #print(project)
                #project = {'sender': 'RCS', 'senderID': '1#', 'recipient': 'UNB', 'recipientID': '1#', 'type': 'taskStart', 'typeID': '1', 'number': '202511180050378', 'task': {'TaskType': 0, 'MaterialID': 'PA640D/34FFDDTY(黑纱）', 'count': 12, 'startAddress': [...], 'endAddress': [...], 'palletInformation': [...]}, 'sendTime': '2025-11-18 20:45:31'}
                #project = {'sender': 'RCS', 'senderID': '1#', 'recipient': 'UNB', 'recipientID': '1#', 'type': 'taskStart', 'typeID': '1', 'number': '202511180050383', 'task': {'TaskType': 0, 'MaterialID': 'PA640D/34FFDDTY(黑纱）', 'count': 12, 'startAddress': [{'location': 'R06', 'type': None, 'fuction': None, 'buffList': []}], 'endAddress': [{'location': 'R13', 'type': None, 'fuction': None, 'buffList': []}], 'palletInformation': []}, 'sendTime': '2025-11-18 21:06:04'}
                StarStartUpPreparation()
                # carton_numder = 10#7 #纸箱类型的编号，1.83/72 百宏 2.55/72 百宏 3.44/36 鑫森 4.22/24 鑫森(环保纱) 5. 33/36 百宏 7.22/24 鑫森
                frequency = 0
                
                #config.vectorA = np.array([[ 1.007,  0.018,  0.018],  [-0.017,  1.011,  0.012], [-0.015, -0.012,  1.021]])
                # config.vectorA = np.array([[ 1.001,0.017,0.02 ],[-0.017,1.01 ,0.01 ],[-0.013,0,1.018]])
                #gui6.2
                config.vectorA = np.array([[ 1.001,0.017,0.02 ],[-0.017,1.01 ,0.01 ],[-0.013,0,1.018]])
                #config.vectorA = config.vectorA*(-982)/config.POS_barcode['z']
                pos_mren = []
                cartonCount = 0
                config.spindle_id,config.spindle_od,Hight,Longsidecoe,Shortsidecoe,order,rule,real_spindle_count = GetParameter(config.carton_numder)
                config.circles_identify_count = 0  # 重置识别次数
                config.spindlesCnt = real_spindle_count  # 设置期望纱锭数量
                sdgs = 0
                sdgs1 = project['act_parameter']['count']
                A = project['act_parameter']['count']
                config.log.logger.info(f"从纸箱类型{config.carton_numder}获取真实纱锭个数: {real_spindle_count}")
                sdgs2 = 0
                zxgs = 0
                cartonCount = 0
                putPos_count = 0
                if project['act_parameter']['endAddress'][0]['location'] == "R07":
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
                if project['act_parameter']['endAddress'][0]['location'] == "R13":
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
                # if config.POS_barcode['z']< -965 and config.POS_barcode['z']>-995 and config.POS_barcode['x']< -184 and config.POS_barcode['x']>-214 and config.POS_barcode['y']< -17 and config.POS_barcode['y']>-37:
                if config.POS_barcode['z']< -1000 and config.POS_barcode['z']>-1068 and config.POS_barcode['x']< -184 and config.POS_barcode['x']>-214 and config.POS_barcode['y']< -17 and config.POS_barcode['y']>-50:
                    config.action = 1
                    # config.action = 160
                    # config.vectorA = config.vectorA*(-982)/config.POS_barcode['z']
                    config.vectorA = config.vectorA #*(-1056)/config.POS_barcode['z']
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
                # carton_height1 = carton_height
                # if carton_height1 == 2:
                #     carton_height1 = 1
                vector0[2] = vector0[2] + Hight*carton_height
                if after_place:
                    guodudian = 1150  # 放置纸箱后过渡点必须用1150，避免压到下层纸箱
                    after_place = False
                else:
                    
                    if vector0[2] >1150:
                        guodudian = 1150
                    else:
                        guodudian = vector0[2].copy()
                links = IdentificationAction1(vector0,euler0,guodudian) 
                # links = IdentificationAction1(vector0,euler0,1150) 
                config.links = IdentificationCmd1(links,9) #
                
                # config.action = 20
                config.action = 2
                config.box = []
                #config.box.append({'x': -200,'y':-300,'z':-750})
                #config.box.append({'x': 200,'y':-300,'z':-750})
                #config.box.append({'x': 200,'y':300,'z':-750})
                #config.box.append({'x': -200,'y':300,'z':-750})


        # if config.action == 1:
        #     if getStep() == False: 
        #         if carton_dir == 0:
        #            vector0 = np.array([1312,100,700])
        #            euler0 = { 'u':0, 'v':90, 'w':90 }
        #            euler0_0 = { 'u':0, 'v':90, 'w':90 }
        #         if carton_dir == 1:
        #            vector0 = np.array([1312,0,700])
        #            euler0 = { 'u':0, 'v':90, 'w':-90 }
        #            euler0_0 = { 'u':0, 'v':90, 'w':-90 }
        #         vector0[2] = vector0[2] + Hight*carton_height

        #         vector0[2] = vector0[2] + Hight*carton_height
        #         # if vector0[2] >1150:
        #         #     guodudian = 1150
        #         # else:
        #         #     guodudian = vector0[2].copy()
        #         links = IdentificationAction1(vector0,euler0,guodudian) 
        #         # links = IdentificationAction1(vector0,euler0,1000) 
        #         config.links = IdentificationCmd1(links,9) 
                
        #         # config.action = 20
        #         config.action = 2
        #         config.box = []
        #         #config.box.append({'x': -200,'y':-300,'z':-750})
        #         #config.box.append({'x': 200,'y':-300,'z':-750})
        #         #config.box.append({'x': 200,'y':300,'z':-750})
        #         #config.box.append({'x': -200,'y':300,'z':-750})
                
        if config.action == 2:#再次识别纸箱
            if getStep() == False: 
                if len(config.box) >0:
                    angle = math.atan2((config.box[1]['x']-config.box[2]['x']),(config.box[2]['y']-config.box[1]['y']))/math.pi*180
                    # vector1 = np.array([-91.291,  35.325, 463.056])#相机偏移
                    #gui6.2
                    vector1 = np.array([-132.465,  37.636,  463.242])#相机偏移
                    vector2 = np.array([(config.box[0]['x']+config.box[1]['x']+config.box[2]['x']+config.box[3]['x'])/4,
                                    (config.box[0]['y']+config.box[1]['y']+config.box[2]['y']+config.box[3]['y'])/4,
                                    (config.box[0]['z']+config.box[1]['z']+config.box[2]['z']+config.box[3]['z'])/4])
                    euler1 = { 'u':euler0['u'], 'v':euler0['v'], 'w':euler0['w']+angle }#0,90,90+angle
                    real_point = GetRealPoint(vector0,vector2,euler0,vector1)
                    twice_ident_point = GetTwiceIdentPoint(real_point,vector1,euler1,-vector2[2])
                    # twice_ident_point[2] = min(vector0[2], 1250)
                    # x_limit = 1500 if carton_height == 2 else 1684
                    vector4 = copy.deepcopy(twice_ident_point)
                    x_limit = 1450 if carton_height == 2 else 1684
                    config.vector4_x_limited = False
                    x_limit_a = 0
                    if vector4[0] > x_limit:
                        x_limit_a = vector4[0] - x_limit
                        vector4[0] = x_limit
                        config.vector4_x_limited = True
                    vector60 = copy.deepcopy(twice_ident_point)
                    fanye_euler = copy.deepcopy(euler1)#0,90,90+angle
                    print(f"z:{config.box[0]['z']}")
                    # if  config.box[0]['z'] ==0 or config.box[0]['z'] < -886 or config.box[0]['z'] > -700:
                    # if  config.box[0]['z'] ==0 or config.box[0]['z'] < -900 or config.box[0]['z'] > -700:
                    if  config.box[0]['z'] ==0 or config.box[0]['z'] < -900 or config.box[0]['z'] > -450:
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
                    
        if config.action == 3:#识别切缝方向 #
            if getStep() == False: 
                if len(config.box) >0:
                    avgHight = (config.box[0]['z']+ config.box[1]['z'] + config.box[2]['z'] + config.box[3]['z'])/4
                    config.box0 = copy.deepcopy(config.box)
                    print(f"avgHight:{avgHight}")
                    angle = math.atan2((config.box[1]['x']-config.box[2]['x']),(config.box[2]['y']-config.box[1]['y']))/math.pi*180
                    # if abs(config.box[1]['x']+config.box[3]['x'])>15 or abs(angle)>1.5 or abs(config.box[0]['y']+config.box[2]['y'])>15:
                    if (abs(angle)>1.5 or abs(config.box[0]['y']+config.box[2]['y'])>15 + 2*x_limit_a or abs(config.box[1]['x']+config.box[3]['x'])>15) :#and not config.vector4_x_limited:
                        print(f"config:{abs(config.box[1]['x']+config.box[3]['x'])}")
                        print(f"angle:{angle}")
                        print(f"x_limit_a:{x_limit_a}")
                        print(f"box:{abs(config.box[0]['y']+config.box[2]['y'])}")
                        vector0 = copy.deepcopy(vector4) 
                        euler0 = copy.deepcopy(euler1)
                        config.log.logger.info("识别切缝方向失败,重新识别纸箱")
                        config.action = 2
                    # elif avgHight > -860 and avgHight < -760: 
                    # 
                    # elif avgHight > -900 and avgHight < -760:    
                    elif avgHight > -900 and avgHight < -600:                   
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
                        Width = (vectorWidth[0]**2+vectorWidth[1]**2+vectorWidth[2]**2)**0.5#纸箱宽度
                        
                        euler1['w'] += angle #0,90,90+angle+angle
                        euler_vis = {'u':0, 'v':90, 'w':euler1['w']-euler0_0['w']}#0,90,angle+angle
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
                    config.log.logger.info("无纸箱信息,再次识别纸箱")
                    config.action = 2

        if config.action == 4:
            if getStep() == False: 
                vector_line_centre = []
                xuhao = 0
                angle = math.atan2((config.line_box[0]['y']-config.line_box[1]['y']),(config.line_box[0]['x']-config.line_box[1]['x']))/math.pi*180
                config.log.logger.info(f"中缝angle:{angle}")
                # angle = 0
                for i in config.line_box:
                    current_time = datetime.now()
                    xuhao += 1
                    vector_vis0 = np.array([i['x'],i['y'],i['z']])
                    real_point = GetRealPoint(vector5,vector_vis0,euler_vis,vector1)#0,90,angle+angle
                    vector_line_centre.append(real_point)
                    #config.database.insert(str(current_time),700+ xuhao,vector_vis0[0],vector_vis0[1],vector_vis0[2],vector_pos[0],vector_pos[1],vector_pos[2])
                    config.database.insert(str(current_time),config.action*1000+0,vector_vis0[0],vector_vis0[1],vector_vis0[2],real_point[0],real_point[1],real_point[2])

                if carton_dir == 0:
                    point_left =  vector_line_centre[1]
                    point_right = vector_line_centre[0]
                    # duodupy = 0
                else:
                    point_left =  vector_line_centre[0]
                    point_right = vector_line_centre[1]
                    # duodupy = 0

                point_vis = 1*point_left+0*point_right
                point_vis[2] = (1*point_left[2]+1*point_right[2])/2 #均值point_left
                euler1 = copy.deepcopy(euler_vis)#0,90,angle+angle
                euler1['w'] = (angle+euler0_0['w']+euler_vis['w'])#0,90,90+angle+angle+angle 
                twice_ident_point = GetTwiceIdentPoint(point_vis,vector1,euler1,450)
                vector5 = copy.deepcopy(twice_ident_point)
                # vector5[1] += duodupy
                test_pos = {'x': int(vector5[0]*1000), 'y': int(vector5[1]*1000), 'z': int(vector5[2]*1000),
                            'u': int(euler1['u']*1000), 'v': int(euler1['v']*1000), 'w': int(euler1['w']*1000)}
                ok, adj_pos = AdjustPosByLimit(test_pos, "IdentAction_right", adjust_axis='x')
                if ok and adj_pos != test_pos:
                    vector5[0] = adj_pos['x'] / 1000.0
                    config.log.logger.info("超限矫正")

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
                    point_vis[2] = (1*point_left[2]+1*point_right[2])/2 #均值point_right
                    twice_ident_point = GetTwiceIdentPoint(point_vis,vector1,euler1,450)#0,90,90+angle+angle+angle 
                    vector5_2 = copy.deepcopy(twice_ident_point)
                    # vector5_2[1] += duodupy
                    test_pos = {'x': int(vector5_2[0]*1000), 'y': int(vector5_2[1]*1000), 'z': int(vector5_2[2]*1000),
                                'u': int(euler1['u']*1000), 'v': int(euler1['v']*1000), 'w': int(euler1['w']*1000)}
                    ok, adj_pos = AdjustPosByLimit(test_pos, "IdentAction_left", adjust_axis='x')
                    if ok and adj_pos != test_pos:
                        vector5_2[0] = adj_pos['x'] / 1000.0
                        config.log.logger.info("超限矫正")
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

        if config.action == 6:#计算缝隙坐标  需要改
            if getStep() == False: 
                flag = 0
                for i in config.line_box:
                    if i['z'] <-500 or i['z'] >-400:
                        flag = 1
                config.database.insert(str(current_time),103,config.currentPos['x'],config.currentPos['y'],config.currentPos['z'],config.currentPos['u'],config.currentPos['v'],config.currentPos['w'])
                if len(config.line_box) >0 and flag == 0:
                    euler10 = { 'u':euler1['u'], 'v':euler1['v'], 'w':euler1['w'] }#切割长缝时刀片的姿态#0,90,90+angle+angle+angle 
                    euler10_2 = { 'u':euler10['u'], 'v':euler10['v'], 'w':euler10['w']-euler0_0['w'] }#切割短缝时刀片的姿态#0,90,angle+angle+angle
                    if carton_dir == 0:
                        euler10_11 = { 'u':euler1['u'], 'v':euler1['v'], 'w':euler1['w']-45 }#切割长缝时刀片的姿态#0,90,90+angle+angle+angle -45
                        euler10_211 = { 'u':euler10['u'], 'v':euler10['v'], 'w':euler10['w']-euler0_0['w'] -45 }#切割短缝时刀片的姿态#0,90,angle+angle+angle-45
                    if carton_dir == 1:
                        euler10_11 = { 'u':euler1['u'], 'v':euler1['v'], 'w':euler1['w']+135 }#切割长缝时刀片的姿态#0,90,90+angle+angle+angle -45
                        euler10_211 = { 'u':euler10['u'], 'v':euler10['v'], 'w':euler10['w']-euler0_0['w'] -45 }#切割短缝时刀片的姿态#0,90,angle+angle+angle-45
                    #vector10 = np.array([237.193,12.122,318.876])#[-250,4,313]#刀片偏移
                    # vector10 = np.array([314.6360173, 4.62224229, 319.45580293])#[-250,4,313]#刀片偏移
                    # vector10 = np.array([314.6360173, 4.62224229, 308])#[-250,4,313]#刀片偏移
                    #gui6.2
                    # vector10 = np.array([278.82039642, 4.62224229, 324.26128874])#[-250,4,313]#刀片偏移
                    # vector10 = np.array([267.82039642, 4.62224229, 324.26128874])#[-250,4,313]#刀片偏移 需要修改
                    if carton_dir == 0:
                        # vector10 = np.array([272.72372349,   8.05363711, 314.87578845])
                        vector10 = np.array([267.72372349,   8.05363711, 314.87578845])
                    if carton_dir == 1:
                        vector10 = np.array([262.72372349,   8.05363711, 314.87578845])
                    # vector10 = np.array([267.82039642, 4.62224229, 324.26128874])
                    vector10_2 = revolve(euler10_11,vector10)#刀片偏移坐标 需要改

                    line_right = copy.deepcopy(config.line_box)
                    vector_line_left = []
                    vector_line_right = []
                    xuhao = 0

                    for i in line_left:
                        current_time = datetime.now()
                        xuhao += 1
                        vector_vis0 = np.array([i['x'],i['y'],i['z']])
                        real_point = GetRealPoint(vector5,vector_vis0,euler1,vector1)
                        clamp_point = GetThePinchPoint(real_point,euler10_11,vector10)- np.array([0,0,2])
                        vector_line_left.append(clamp_point)
                        config.database.insert(str(current_time),config.action*1000+200+ xuhao,vector_vis0[0],vector_vis0[1],vector_vis0[2],clamp_point[0],clamp_point[1],clamp_point[2])

                    xuhao = 0
                    for i in line_right:
                        current_time = datetime.now()
                        xuhao += 1
                        vector_vis0 = np.array([i['x'],i['y'],i['z']])
                        real_point = GetRealPoint(vector5_2,vector_vis0,euler1,vector1)
                        clamp_point = GetThePinchPoint(real_point,euler10_11,vector10)- np.array([0,0,2])
                        vector_line_right.append(clamp_point)
                        config.database.insert(str(current_time),config.action*1000+300+ xuhao,vector_vis0[0],vector_vis0[1],vector_vis0[2],clamp_point[0],clamp_point[1],clamp_point[2])

                    sorted_data = SlitCoordinate(vector_line_left,vector_line_right)

                    vector14 = sorted_data[0]#刀片切割缝隙时左侧端点坐标
                    vector15 = sorted_data[len(sorted_data)-1]#刀片切割缝隙时右侧端点坐标    
                    
                    vector10_3 = revolve(euler10_211,vector10)#切割左侧胶带的刀片偏移 需要改
                    vector10_4 = revolve(euler10_211,vector10)#切割右侧胶带的刀片偏移 需要改

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
                    config.log.logger.info(f"sorted_data: {sorted_data}")
                    config.links = SlittingAction(sorted_data,euler10_11) #需要改
                    if len(sorted_data) == 0:
                        config.action = 8
                        qiecount = 2

                
        if config.CUT_ORDER == "left_first":
            # 先左后右: action 8 = 左侧切缝, action 9 = 右侧切缝
            if config.action == 8:#将左侧切缝分6刀切完
                if getStep() == False:
                    qiecount -= 1
                    if(qiecount == 1):
                        vector_qie = np.array([20,0,0+derstarthig])
                    else:
                        vector_qie = np.array([10,0,0])               
                    config.links = SlittingAction2(vector135,vector136,vector_qie,euler10_211)
                    if config.links == False:
                        config.action = 1001
                        continue
                    if(qiecount == 0):
                        qiecount = 2
                        config.action = 9

            if config.action == 9:#将右侧切缝分6刀切完
                if getStep() == False:  
                    qiecount -= 1
                    if(qiecount == 1):
                        vector_qie = np.array([-20,0,0+derendhig])
                    else:
                        vector_qie = np.array([-10,0,0])     
                    config.links = SlittingAction2(vector133,vector134,vector_qie,euler10_211) #需要改
                    if config.links == False:
                        config.action = 1001
                        continue
                    if(qiecount == 0):
                        config.action = 10
        else:
            # 先右后左 (默认): action 8 = 右侧切缝, action 9 = 左侧切缝
            if config.action == 8:#将右侧切缝分6刀切完
                if getStep() == False:  
                    qiecount -= 1
                    # if(qiecount == 1):
                    #     vector_qie = np.array([-40,0,0+derendhig])
                    # else:
                    #     vector_qie = np.array([-25,0,0])      
                    if(qiecount == 1):
                        vector_qie = np.array([-20,0,0+derendhig])
                    else:
                        vector_qie = np.array([-10,0,0])     
                    config.links = SlittingAction2(vector133,vector134,vector_qie,euler10_211) #需要改
                    if config.links == False:
                        config.action = 1001
                        continue
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
                    config.links = SlittingAction2(vector135,vector136,vector_qie,euler10_211)
                    if config.links == False:
                        config.action = 1001
                        continue
                    if(qiecount == 0):
                        config.action = 10

        if config.action == 10:#刀片围绕右边缘做翻箱动作
            if getStep() == False: 
                # vector_xipan = np.array([3.82524579, 185.32992087, 310.38751022])#翻箱片偏移
                #gui6.2
                vector_xipan = np.array([ -0.70160645  , 140.62001267 , 300.4370298  ])#翻箱片偏移
                
                #vector_xipan = np.array([6.41459874,183.64143843,308.92476951])
                vector50 = 0.5*starVector+0.5*endVector#中心点
                #vector50[1] = vector50[1] - frequency*7
                #
                vector53 = np.array([0,Width + 15,0])#旋转偏移
                vector51 = vector50 - revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },vector53)
                vector56 = vector51 + 0.7*revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },np.array([Lenth,0,0]))
                vector53_2 = vector53-np.array([0,40,0])
                #if carton_dir == 0:
                #    vector80 = 0.5*starVector+0.5*endVector + revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },vector53)
                #else:
                vector80 = 0.5*starVector+0.5*endVector - revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },vector53)
                
                derW = euler1['w']-euler0_0['w']
                firstEuler = { 'u':-90, 'v':0, 'w':-90+derW}
                twiceEuler = { 'u':-90, 'v':0, 'w':-90+derW}
                kaixiangangle = 22.5
                mouldEuler = {  'u':0+kaixiangangle, 'v':0, 'w':derW }

                #按照长边偏移来设定旋转点
                vector51 = vector51 + revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },np.array([ Longsidecoe*Lenth,0,0]))

                if rule == 1:
                    config.action = 200
                else:
                    config.action = 11
                derVector1 = np.array([0,20,-15])  # 增加插入深度从-15到-25
                derVector2 = np.array([0,-20,-20])  # 增加插入深度从-20到-30
                config.links = MouldTurnoverAction(mouldEuler,vector_xipan,vector51,vector53,vector53_2,vector56,firstEuler,twiceEuler,derW,carton_height,derVector1,derVector2)
                if config.links == False:
                    config.action = 1001
                    continue
        if config.action == 200:#前往中心点识别是否翻起，并确认下一片的翻箱点
            if getStep() == False: 
                
                center = copy.deepcopy(0.5*starVector+0.5*endVector)
                vector61 = GetTwiceIdentPoint(center,vector1,euler1,800)
                poss = []
                if carton_height == 2:
                    default_poss0 = {'x':int(-0.038*1000),'y':int(18.407*1000),'z':int(-41.890*1000),'u':int(-0.098*1000),'v':int(23.482*1000),'w':int(0.087*1000)}
                   
                else:
                    default_poss0 = {'x':int(0*1000),'y':int(-1.408*1000),'z':int(-41.890*1000),'u':int(-0.082*1000),'v':int(55.569*1000),'w':int(0.046*1000)}
                # 动态生成过渡关节位置，限制x轴移动距离
                # poss.append(get_dynamic_transition_poss0(default_poss0))
                poss.append(default_poss0)
                poss.append({'x':int(vector61[0]*1000),'y':int(vector61[1]*1000),'z':int(vector61[2]*1000),'u':int(euler1['u']*1000),'v':int(euler1['v']*1000),'w':int(euler1['w']*1000)})
                ok, adj_pos = AdjustPosByLimit(poss[-1], "links_action16_0", adjust_axis='x')
                if ok:
                    poss[-1] = adj_pos
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
                    config.log.logger.info("config.notice1 = %d, config.notice2 = %d, carton_dir = %d" % (config.notice1,config.notice2,carton_dir))
                    config.log.logger.info("vector_fanye1[2]-fanxianghight = %f, vector_fanye2[2]-fanxianghight = %f" % (abs(vector_fanye1[2]-fanxianghight),abs(vector_fanye2[2]-fanxianghight)))
                    frequency += 1
                    if frequency == 3:
                        config.log.logger.info("201次判断叶片是否翻起")
                        config.action = 1001
                    else :
                        config.action = 200

        if config.action == 11:#刀片围绕左边缘做翻箱动作
            if getStep() == False: 

                # vector_xipan = np.array([-46.70158978, 183.63014186, 310.40850719])
                #gui6.2
                # [ -0.70160645, 180.62001267, 320.4370298 ]
                vector_xipan = np.array([-46.70158978  , 130.63014186, 300.40850719  ])
                vector50 = 0.5*starVector+0.5*endVector

                vector53 = np.array([0,-Width - 15,0])#旋转偏移
                vector51 = vector50 - revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },vector53)#旋转点
                vector56 = vector51 + 0.7*revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },np.array([Lenth,0,0]))

                if rule == 1:#规则的直接使用数据
                    if carton_dir == 0:
                        vector53 = revolve({ 'u':0, 'v':0, 'w':-euler1['w']+euler0_0['w'] }, vector_fanye1-vector51)
                    else:
                        vector53 = revolve({ 'u':0, 'v':0, 'w':-euler1['w']+euler0_0['w'] }, vector_fanye2-vector51)

                    vector51 = vector51 + revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },np.array([vector53[0],0,0]))#旋转点
                    vector53[0] = 0
                else:
                    vector51 = vector51 + revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },np.array([Longsidecoe*Lenth,0,0]))#旋转点
                    vector53[0] = 0

                config.action = 202
                
                vector53_2 = vector53-np.array([0,-40,0])

                derW = euler1['w']-euler0_0['w']
                firstEuler = { 'u':-90, 'v':-15, 'w':-90+derW}
                twiceEuler = { 'u':-90, 'v':15, 'w':-90+derW}
                kaixiangangle = 22.5
                mouldEuler = {  'u':0-kaixiangangle, 'v':0, 'w':derW }

                derVector1 = np.array([0,-20,-15])  # 增加插入深度从-15到-25
                derVector2 = np.array([0,20,-20])  # 增加插入深度从-20到-30
                config.links =  MouldTurnoverAction(mouldEuler,vector_xipan,vector51,vector53,vector53_2,vector56,firstEuler,twiceEuler,derW,carton_height,derVector1,derVector2) 
                if config.links == False:
                    config.action = 1001
                    continue
        if config.action == 202:#识别2，3页翻箱
            if getStep() == False:
                poss = []
                center = copy.deepcopy(0.5*starVector+0.5*endVector)
                vector61 = GetTwiceIdentPoint(center,vector1,euler1,800)

                # if carton_height == 2:
                #     default_poss0 = {'x':int(-0.038*1000),'y':int(18.407*1000),'z':int(-25*1000),'u':int(-0.098*1000),'v':int(23.482*1000),'w':int(0.087*1000)}
                # else:
                #     default_poss0 = {'x':int(0*1000),'y':int(-1.408*1000),'z':int(-25*1000),'u':int(-0.082*1000),'v':int(55.569*1000),'w':int(0.046*1000)}
                if carton_height == 2:
                    default_poss0 = {'x':int(-0.038*1000),'y':int(17.407*1000),'z':int(-35.890*1000),'u':int(-0.078*1000),'v':int(34.234*1000),'w':int(0.052*1000)}
                else:
                    default_poss0 = {'x':int(-0.038*1000),'y':int(17.407*1000),'z':int(-35.890*1000),'u':int(-0.078*1000),'v':int(34.234*1000),'w':int(0.052*1000)}
                # 动态生成过渡关节位置，限制x轴移动距离
                poss.append(get_dynamic_transition_poss0(default_poss0))
                # poss.append(default_poss0)
                poss.append({'x':int(vector61[0]*1000),'y':int(vector61[1]*1000),'z':int(vector61[2]*1000),'u':int(euler1['u']*1000),'v':int(euler1['v']*1000),'w':int(euler1['w']*1000)})
                ok, adj_pos = AdjustPosByLimit(poss[-1], "links_action16_1", adjust_axis='x')
                if ok:
                    poss[-1] = adj_pos
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
                        config.log.logger.info("203次判断叶片是否翻起")
                        config.action = 9999999999

                    else :
                        config.action = 202

        if config.action == 204:#刀片围绕右边缘做翻箱动作
            if getStep() == False: 
                # vector_xipan = np.array([3.82524579, 185.32992087, 310.38751022])#翻箱片偏移
                #gui6.2
                vector_xipan = np.array([ -0.70160645, 130.62001267, 300.4370298  ])#翻箱片偏移
                #vector_xipan = np.array([6.41459874,183.64143843,308.92476951])
                vector50 = 0.5*starVector+0.5*endVector#中心点
                #vector50[1] = vector50[1] - frequency*7
                vector53 = np.array([0,Width+10,0])#旋转偏移
                vector51 = vector50 - revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },vector53)
                vector56 = vector51 + 0.7*revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },np.array([Lenth,0,0]))
                
                #if carton_dir == 0:
                #    vector80 = 0.5*starVector+0.5*endVector + revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },vector53)
                #else:
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
                if config.links == False:
                    config.action = 1001
                    continue

        if config.action == 205:#刀片围绕左边缘做翻箱动作
            if getStep() == False: 
                #gui6.2
                vector_xipan = np.array([-46.70158978, 120.63014186, 300.40850719])
                vector50 = 0.5*starVector+0.5*endVector

                vector53 = np.array([0,-Width-10,0])#旋转偏移
                vector51 = vector50 - revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },vector53)#旋转点
                vector56 = vector51 + 0.7*revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },np.array([Lenth,0,0]))

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
                if config.links == False:
                    config.action = 1001
                    continue
        if config.action == 12:#刀片围绕下边缘做翻箱动作
            if getStep() == False: 
                #如果一叶没有翻过去重新切左右两侧，如果两页都没有翻过去，重新识别纸箱，重新识别切缝，重新翻箱

                derW = euler1['w']-euler0_0['w']
                if carton_dir == 0:
                    firstEuler = { 'u':-90, 'v':-15, 'w':derW}
                    twiceEuler = { 'u':-90, 'v':0, 'w':derW}
                    #vector_xipan = np.array([-48.909,183.037,310.121])#翻箱片偏移
                    #gui6.2
                    vector_xipan = np.array([-46.70158978 +10, 130.63014186, 300.40850719 ])#翻箱片偏移
                    euler50 = { 'u':0, 'v':0, 'w':euler1['w']}
                    vector50 = 0.5*starVector+0.5*endVector#中心点
                    vector51 = vector50 - revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },np.array([Lenth,0,0]))
                    vector53 = np.array([Width+40,0,0])#旋转偏移                   
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
                    # vector_xipan = np.array([3.82524579, 185.32992087, 310.38751022])#翻箱片偏移
                    #gui6.2
                    vector_xipan = np.array([ 9.30160645 , 140.63014186 , 320.40850719  ])#翻箱片偏移
                    vector50 = 0.5*starVector+0.5*endVector#中心点
                    vector51 = vector50 - revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },np.array([Lenth,0,0]))
                    vector53 = np.array([Width+40,0,0])#旋转偏移
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
                derVector1 = np.array([20,0,-15])  # 增加插入深度从-15到-25
                derVector2 = np.array([-20,0,-25])  # 增加插入深度从-25到-35
                config.links = MouldTurnoverAction(mouldEuler,vector_xipan,vector51,vector53,vector53_2,vector56,firstEuler,twiceEuler,derW,carton_height,derVector1,derVector2)                
                if config.links == False:
                    config.action = 1001
                    continue
                config.action = 13
                count_shang = 0  # 翻上页计数器

        if config.action == 13:#刀片围绕上边缘做翻箱动作
            if getStep() == False: 
                
                #vector_xipan = np.array([-250.988,1.971,283.315])#翻箱片偏移
                # vector_xipan = np.array([-260.37451458,    3.53112586,  291.55552622])#翻箱片偏移
                #gui6.2
                # 根据翻页次数调整a值
                count_shang += 1
                if count_shang == 1:
                    a = 10  # 第一次翻页
                elif count_shang == 2:
                    a = 15  # 第二次翻页
                else:
                    a = 20  # 第三次及以后翻页
                vector_xipan = np.array([-281.21358258 +60 +a,   30.67419854,  299.18651677])
                derW = euler1['w']-euler0_0['w']
                firstEuler = { 'u':0, 'v':-90, 'w':180+derW}
                vector50 = 0.5*starVector+0.5*endVector#中心点
                vector51 = vector50 + revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },np.array([Lenth,0,0]))
                vector53 = np.array([-Width-40,0,0])#旋转偏移
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
                derVector1 = np.array([-20,0,-15])  # 增加插入深度从-15到-25
                derVector2 = np.array([20,0,-25])  # 增加插入深度从-25到-35
                config.links = MouldTurnoverAction(mouldEuler,vector_xipan,vector51,vector53,vector53_2,vector56,firstEuler,twiceEuler,derW,carton_height,derVector1,derVector2)
                if config.links == False:
                    config.action = 1001
                    continue        
                config.action = 14

        if config.action == 14:#识别翻页
            if getStep() == False:     
                poss = []
                
                vector0 = copy.deepcopy(vector61)
                euler0 = copy.deepcopy(euler1)
                if carton_height == 2:
                    default_poss0 = {'x':int(-0.038*1000),'y':int(18.407*1000),'z':int(-25*1000),'u':int(-0.098*1000),'v':int(23.482*1000),'w':int(0.087*1000)}
                else:
                    default_poss0 = {'x':int(0*1000),'y':int(-1.408*1000),'z':int(-25.165*1000),'u':int(-0.082*1000),'v':int(55.569*1000),'w':int(0.046*1000)}
                # 动态生成过渡关节位置，限制x轴移动距离
                # poss.append(get_dynamic_transition_poss0(default_poss0))
                poss.append(default_poss0)
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
                        config.log.logger.info("301次判断叶片是否翻起")
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
                    #gui6.2
                    vector_xipan = np.array([-36.70158978, 120.63014186, 300.40850719])#翻箱片偏移
                    euler50 = { 'u':0, 'v':0, 'w':euler1['w']}
                    vector50 = 0.5*starVector+0.5*endVector#中心点
                    vector51 = vector51 = vector50 - revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },np.array([Lenth,0,0]))
                    vector53 = np.array([Width+20,0,0])#旋转偏移                   
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
                    # vector_xipan = np.array([3.82524579, 185.32992087, 310.38751022])#翻箱片偏移
                    #gui6.2
                    vector_xipan = np.array([ -0.70160645, 130.62001267, 300.4370298  ])#翻箱片偏移
                    vector50 = 0.5*starVector+0.5*endVector#中心点
                    vector51 = vector51 = vector50 - revolve({ 'u':0, 'v':0, 'w':euler1['w']-euler0_0['w'] },np.array([Lenth,0,0]))
                    vector53 = np.array([Width+20,0,0])#旋转偏移
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
                if config.links == False:
                    config.action = 1001
                    continue        
                
                config.action = 14

        if config.action == 304:#识别全局纱锭
            if getStep() == False:   
                config.links.append({'State':True, 'typeID': 12})
                config.circles = []
                config.circles_identify_count += 1  # 增加识别次数
                config.log.logger.info(f"第{config.circles_identify_count}次识别纱锭")
                #config.action = 21
                config.action = 15

        if config.action == 15:
            if getStep() == False:
                for i in range(0,len(config.circles)):
                    config.database.insert(str(current_time),config.action*1000+i,config.circles[i]['x'],config.circles[i]['y'],config.circles[i]['z'],0,0,0)
                
                detected_count = len(config.circles)
                config.log.logger.info(f"识别到{detected_count}个纱锭，真实纱锭数: {real_spindle_count}，已识别次数: {config.circles_identify_count}")
                
                # 检查是否漏识别
                if detected_count != real_spindle_count:
                    if config.circles_identify_count < 3:
                        # 漏识别且识别次数小于3次，重新识别
                        config.log.logger.info(f"纱锭漏识别，第{config.circles_identify_count}次识别不完整，重新识别")
                        config.action = 304
                        continue
                    else:
                        # 识别3次仍然不足，结束任务
                        config.log.logger.info(f"已识别3次仍不足{real_spindle_count}个纱锭，结束任务")
                        
                        config.action = 1001
                        continue

                if len(order) == len(config.circles):
                    circles2 = copy.deepcopy(config.circles)
                    for i in range(0,len(order)):
                        circles2[i] = config.circles[order[i]]                        
                    config.circles = copy.deepcopy(circles2)
                    print(f"排序后的纱锭: {config.circles}")
                if sdgs2 == 0:
                    config.action = 160    
                else:
                    config.action = 18    
                
        if config.action == 160:#视觉托盘识别-移动到识别点
            if getStep() == False:
                # pallet_recog_pos = np.array([-152.94, -1191, 723])
                if project['act_parameter']['endAddress'][0]['location'] == "R13":
                    # pallet_recog_pos = np.array([-152.94, 1191 * zhengfu, 723])
                    angle_1 = 0
                    zhengfu = 1
                if project['act_parameter']['endAddress'][0]['location'] == "R07" or project['act_parameter']['endAddress'][0]['location'] == "R7":
                    
                    angle_1 = 180
                    zhengfu = -1
                pallet_recog_pos = np.array([-152.94, 1191 * zhengfu, 723])
                # pallet_recog_euler = {'u': -90, 'v': 90, 'w': 0}
                pallet_recog_euler = {'u': 0, 'v': 90, 'w': 90 +angle_1}
                # pallet_recog_euler = {'u': 0, 'v': 90, 'w': 90}
                vector_temp = copy.deepcopy(pallet_recog_pos)
                vector_temp[2] = 1050
                links = IdentificationAction1(pallet_recog_pos, pallet_recog_euler, vector_temp[2])
                config.links = IdentificationCmd1(links, 19)
                config.pallet_recog_cam_pos = pallet_recog_pos
                config.pallet_recog_cam_euler = pallet_recog_euler
                config.log.logger.info(f"托盘识别: 移动到识别点 x={pallet_recog_pos[0]}, y={pallet_recog_pos[1]}, z={pallet_recog_pos[2]}")
                # input(111111)
                config.action = 161

        if config.action == 161:#视觉托盘识别结果+左侧放置位识别
            if getStep() == False:
                # vector1 = np.array([-91.291,  35.325, 463.056])#视觉托盘识别点第一个是z
                vector11 = np.array([100,  80, 400 ])
                # vector1 = np.array([100,  100, 410])
                # vector1 = np.array([100,  0, 500])
                pallet = config.palletcenter
                pallet_vision = np.array([pallet['x'], pallet['y'], pallet['z']])
                gudin = -1125.5
                config.pallet_recog_cam_height = pallet_recog_pos[2]  + gudin + 315 +Hight
                config.log.logger.info(f"托盘识别: 识别点高度={pallet_recog_pos[2]}, 视觉高度={pallet['z']}, 315={315}, 纸锭高度={Hight}, 放置高度={config.pallet_recog_cam_height}")
                pallet_world = GetRealPoint(config.pallet_recog_cam_pos, pallet_vision, 
                                           config.pallet_recog_cam_euler, vector11)
                config.log.logger.info(f"托盘中心: 视觉坐标={pallet_vision}, 世界坐标={pallet_world}")
                
                camera_height = 890
                # placement_cam_euler = {'u': -90, 'v': 90, 'w': pallet['w'] - 90}
                placement_cam_euler = {'u': 0, 'v': 90, 'w': pallet['w'] + angle_1}
                # if 90<placement_cam_euler['w'] <= 180:
                #     placement_cam_euler['w'] = 181



                # placement_cam_euler = {'u': 0, 'v': 90, 'w':   181}
                # placement_cam_euler = {'u': 0, 'v': 90, 'w': config.pallet_recog_cam_euler['w'] + pallet['w'] - 90}
                # placement_cam_euler = {'u': -180, 'v': 90, 'w': 0}
                # input(f"左侧放置位识别: 相机euler={placement_cam_euler['w']}")
                camera_pos = np.array([pallet_world[0], pallet_world[1], camera_height])
                
                vector_temp = copy.deepcopy(camera_pos)
                vector_temp[2] = vector_temp[2] 
                # # 使用直线运动移动到识别点
                # targetPoint = {'x': camera_pos[0], 'y': camera_pos[1], 'z': camera_pos[2],
                #                'u': placement_cam_euler['u'], 'v': placement_cam_euler['v'], 'w': placement_cam_euler['w']}
                # config.setLinks.Straight_line_Motion(targetPoint, speed=config.speed)
                links = IdentificationAction2(camera_pos, placement_cam_euler, vector_temp[2])
                if links == False:
                    config.action = 1001
                    continue
                links.append({'State': True, 'typeID': 15, 'placementLR': 1})
                config.links = links
                config.cam_pos_left = camera_pos
                config.cam_euler_left = placement_cam_euler
                config.log.logger.info(f"左侧放置位识别: 相机位置={camera_pos}, euler={placement_cam_euler}")
                config.jiehao = True
                # input(111111)
                # config.action = 162
                config.action = 163

        if config.action == 162:#左侧到右侧过渡位姿（避免180°跳变限位）
            if getStep() == False:
                # 先旋转90°作为过渡，避免直接180°跳变触发限位
                transition_euler = config.pallet_recog_cam_euler.copy()
                # transition_euler = {'u': 0, 'v': 90, 'w': 0 + angle_1}
                # transition_euler = {'u': -180, 'v': 90, 'w': 0}
                # links = IdentificationAction1(config.cam_pos_left, transition_euler, config.cam_pos_left[2])
                links = IdentificationAction2(config.cam_pos_left, transition_euler, config.cam_pos_left[2] )
                config.links = links
                config.log.logger.info(f"过渡位姿: euler={transition_euler}")
                # if config.jiehao == True:
                #     config.action = 163
                # else:
                config.action = 164

        if config.action == 163:#左侧结果+右侧放置位识别
            if getStep() == False:
                config.left_positions = config.temp_putPos[:]
                config.log.logger.info(f"左侧放置位结果: {config.left_positions}")
                # vector1 = np.array([100,  100, 400])
                vector22_2 = np.array([100,  0, 500])
                pallet = config.palletcenter
                pallet_vision = np.array([pallet['x'], pallet['y'], pallet['z']])
                pallet_world = GetRealPoint(config.pallet_recog_cam_pos, pallet_vision,
                                           config.pallet_recog_cam_euler, vector22_2)
                
                camera_height = 890
                placement_cam_euler = {'u': 0, 'v': 90, 'w': pallet['w'] +  180 - angle_1}
                # if placement_cam_euler['w'] >= 180:
                #     placement_cam_euler['w'] = 180
                # placement_cam_euler = {'u': 0, 'v': 90, 'w': config.pallet_recog_cam_euler['w'] + pallet['w'] + 90}
                # input(f"右侧放置位识别: 相机euler={placement_cam_euler['w']}")
                #识别位加50mm
                camera_pos = np.array([pallet_world[0] +50 * zhengfu, pallet_world[1], camera_height])
                
                vector_temp = copy.deepcopy(camera_pos)
                vector_temp[2] = vector_temp[2]
                links = IdentificationAction2(camera_pos, placement_cam_euler, vector_temp[2])
                if links == False:
                    config.action = 1001
                    continue
                
                links.append({'State': True, 'typeID': 15, 'placementLR': 0})
                config.links = links
                config.cam_pos_right = camera_pos
                config.cam_euler_right = placement_cam_euler
                config.log.logger.info(f"右侧放置位识别: 相机位置={camera_pos}, euler={placement_cam_euler}")
                config.jiehao = False
                # input(222222)
                # config.action = 162
                config.action = 164

        if config.action == 164:#右侧结果+合并放置位置
            if getStep() == False:
                config.right_positions = config.temp_putPos[:]
                config.log.logger.info(f"右侧放置位结果: {config.right_positions}")
                
                pos_mren.clear()
                
                # 使用标准相机偏移，与纱锭识别保持一致
                #gui6.2
                # vector1 = np.array([-91.291,  35.325, 463.056])  # 相机偏移
                # vector1 = np.array([-132.465,  37.636,  463.242])
                # 左侧放置位置转换为世界坐标
                for i, pos in enumerate(config.left_positions):
                    # 视觉坐标直接使用原始值 [x, y, z, px, py]
                    vision_pos = np.array([pos[0], pos[1], pos[2]])
                    # GetRealPoint 将视觉坐标转换为纱锭中心的世界坐标
                    world_pos = GetRealPoint(config.cam_pos_left, vision_pos, config.cam_euler_left, vector1)
                    
                    # 修正z高度为托盘表面
                    # world_pos[2] = config.pallet_recog_cam_height
                    
                    pos_mren.append(world_pos)
                    putPos_count = len(pos_mren)
                    config.log.logger.info(f"左侧放置位{i+1}: 视觉坐标={pos}, 世界坐标={world_pos}")
                
                # 右侧放置位置转换为世界坐标
                for i, pos in enumerate(config.right_positions):
                    vision_pos = np.array([pos[0], pos[1], pos[2]])
                    world_pos = GetRealPoint(config.cam_pos_right, vision_pos, config.cam_euler_right, vector1)
                    # world_pos[2] = config.pallet_recog_cam_height
                    
                    pos_mren.append(world_pos)
                    config.log.logger.info(f"右侧放置位{i+1}: 视觉坐标={pos}, 世界坐标={world_pos}")
                
                config.log.logger.info(f"视觉放置位置总数: {len(pos_mren)}, 坐标: {pos_mren}")
                config.fznumber = len(pos_mren)
                # 保存用于测试
                config.putPos_world = pos_mren[:]
                config.putPos_index = 0
                
                # 进入测试模式：逐个移动到放置点位
                # config.action = 165
                config.action = 18
        
        # 测试模式：逐个移动到放置点位（用于验证点位是否正确）
        if config.action == 165:#逐个测试放置点位
            if getStep() == False:
                if config.putPos_index < len(config.putPos_world):
                    target_pos = config.putPos_world[config.putPos_index]
                    
                    config.log.logger.info(f"放置左个数:={putPos_count}")
                    if config.putPos_index < putPos_count:
                        if  -1400 < target_pos[1] < 1250:
                            euler_putVis = copy.deepcopy(config.cam_euler_left)
                            # clamp_T = np.array([314.6360173, 4.62224229, 319.45580293])  # 夹取点偏移
                            #gui6.2
                            clamp_T = np.array([270.82039642, 4.62224229, 324.26128874])  # 夹取点偏移
                            clamp_point = GetThePinchPoint(target_pos, euler_putVis, clamp_T)
                            clamp_point[2] = config.pallet_recog_cam_height
                            input(111111111)
                        else:
                            euler_putVis = copy.deepcopy(config.cam_euler_left)
                            euler_putVis['w'] = euler_putVis['w'] + 90
                            # clamp_T = np.array([314.6360173, 4.62224229, 319.45580293])  # 夹取点偏移
                            #gui6.2
                            clamp_T = np.array([270.82039642, 4.62224229, 324.26128874])  # 夹取点偏移
                            clamp_point = GetThePinchPoint(target_pos, euler_putVis, clamp_T)
                            clamp_point[2] = config.pallet_recog_cam_height
                            input(222222222)
                    else:
                        if  -1400 < target_pos[1] < 1250:
                            euler_putVis = copy.deepcopy(config.cam_euler_right)
                            # clamp_T = np.array([314.6360173, 4.62224229, 319.45580293])  # 夹取点偏移
                            #gui6.2
                            clamp_T = np.array([270.82039642, 4.62224229, 324.26128874])  # 夹取点偏移
                            clamp_point = GetThePinchPoint(target_pos, euler_putVis, clamp_T)
                            clamp_point[2] = config.pallet_recog_cam_height
                            input(333333333)
                        else:
                            euler_putVis = copy.deepcopy(config.cam_euler_right)
                            euler_putVis['w'] = euler_putVis['w'] - 90
                            # clamp_T = np.array([314.6360173, 4.62224229, 319.45580293])  # 夹取点偏移
                            #gui6.2
                            clamp_T = np.array([270.82039642, 4.62224229, 324.26128874])  # 夹取点偏移
                            clamp_point = GetThePinchPoint(target_pos, euler_putVis, clamp_T)
                            clamp_point[2] = config.pallet_recog_cam_height
                            input(444444444)
                    
                    config.log.logger.info(f"测试放置位{config.putPos_index+1}/{len(config.putPos_world)}: {target_pos}")
                    print(f"=== 测试放置位 {config.putPos_index+1}/{len(config.putPos_world)} ===")
                    print(f"目标坐标: x={target_pos[0]:.2f}, y={target_pos[1]:.2f}, z={target_pos[2]:.2f}")
                    print(f"夹取点: x={clamp_point[0]:.2f}, y={clamp_point[1]:.2f}, z={clamp_point[2]:.2f}")
                    print(f"目标姿态: u={euler_putVis['u']}, v={euler_putVis['v']}, w={euler_putVis['w']}")
                    input("按回车键移动到该点位，或按Ctrl+C退出测试...")
                    
                    # 使用逆解到达目标点位
                    EndPos = {'x': clamp_point[0], 'y': clamp_point[1], 'z': clamp_point[2],
                              'u': euler_putVis['u'], 'v': euler_putVis['v'], 'w': euler_putVis['w']}
                    
                    links = IdentificationAction1(clamp_point, euler_putVis, 500)
                    config.links = links
                    config.putPos_index += 1
                else:
                    config.log.logger.info("所有放置点位测试完成")
                    print("=== 所有放置点位测试完成 ===")
                    # config.action = 16  # 返回正常流程
                    config.action = 18  # 返回正常流程

        if config.action == 16:#识别放置点位
            if getStep() == False:
                if (len(config.circles) > 0 ) and (len(pos_mren) > 0) and sdgs < 12:                    
                    poss = []
                    if (pos_mren[sdgs][1]>0):
                        euler_putVis = { 'u':0, 'v':90, 'w':90 }
                    else:
                        euler_putVis = { 'u':0, 'v':90, 'w':-90 }     
                    vector20 = pos_mren[sdgs]+revolve(euler_putVis,np.array([285,6.5,315])) - revolve(euler_putVis,np.array([-860,31,440]))
                    # print(vector20)

                    hight = max(1100 - (2-carton_height)*Hight,700)
                    print(f"过渡高度: {hight}")
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
                    config.action = 100
                    print("放置位置已满")

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
                    if sdgs1 == sdgs2 :
                        config.action = 1000
                        rcs.act_status = 4
                        rcs2.act_status = 4
                        rcs.arm_status = 0
                        rcs2.arm_status = 0
                        rcs.CurrentStatus = "Idle"
                        config.boxfull = False

                        # input("完成所有放置")
                        continue
                        # print("放置位置已满")
                    else:    
                        hight = max(1100 - (2-carton_height)*Hight,700)
                        print(f"过渡高度: {hight}")

                        #vector1 = np.array([-85.718,33.191,462.78])#相机偏移
                        # vector1 = np.array([-91.291,  35.325, 463.056])#相机偏移
                        vector1 = np.array([-132.465,  37.636,  463.242])#相机偏移
                        vector2 = np.array([config.circles[0]['x'],config.circles[0]['y'],config.circles[0]['z']])
                        euler0_18 = copy.deepcopy(euler0)
                        config.log.logger.info(f"config.circles[0]['y'] = {config.circles[0]['y']},")
                        if carton_dir == 0 and config.circles[0]['y'] <= -100:
                            
                            euler0_18['w'] = euler0_18['w'] -90
                            config.log.logger.info(f"左侧纸箱，旋转90度")
                        if carton_dir == 1 and config.circles[0]['y'] >= 100:
                            # euler0_18 = copy.deepcopy(euler0)
                            euler0_18['w'] = euler0_18['w'] +90
                            config.log.logger.info(f"右侧纸箱，旋转90度")
                        
                        real_point = GetRealPoint(vector0,vector2,euler0,vector1)
                        twice_ident_point = GetTwiceIdentPoint(real_point,vector1,euler0_18,400)
                        vector4 = copy.deepcopy(twice_ident_point)
                        vector4[2] = vector0[2] -360
                        # input(11111111)
                        # links = IdentificationAction1(vector4,euler0, hight) 
                        links = IdentificationAction1(vector4,euler0_18, hight) 
                        config.links = IdentificationCmd1(links,13) 
                        config.circles.remove(config.circles[0])
                        config.action = 19
                    # if sdgs1 == sdgs2 :
                    #     config.action = 100
                    # else :
                    #     config.action = 19
                else:    
                    # euler83 = { 'u':0, 'v':90, 'w':0+derW }

                    # twice_ident_point = GetTwiceIdentPoint(vector80,vector1,euler83,500)
                    # vector82 = copy.deepcopy(twice_ident_point)
                    # links = IdentificationAction1(vector82,euler83, hight) 
                    # config.links = IdentificationCmd3(links,17,Lenth*2,Width*2)
                    config.action = 195

        if config.action == 19:#纱锭抓放动作
            if getStep() == False:

                if config.circle['z'] != 0:
                    euler10_19 = copy.deepcopy(euler0_18)
                    # euler10 =  copy.deepcopy(euler1)
                    euler10 =  copy.deepcopy(euler10_19)
                    vector13 = np.array([config.circle['x'],config.circle['y'],config.circle['z']])
                    #vector12 =  np.array([272,12,323])#[297.50410206,   0.72790701, 303.92396606] 
                    # vector12 =  np.array([275 +10 ,-3.68,307.7  ]) 
                    # [267.72372349,   8.05363711, 314.87578845]
                    if config.carton_numder == 25: #S
                        # vector12 =  np.array([275 + 4 -5 ,-3.68,302   ]) 
                        #gui6.2
                        # vector12 =  np.array([260 ,-3.68,312.26128874   ]) 
                        vector12 =  np.array([250 ,-3.68,312.26128874   ]) 

                    elif config.carton_numder == 24: #J
                        vector12 =  np.array([245,-3.68,312.26128874  ]) 
                    elif config.carton_numder == 28: #X
                        vector12 =  np.array([245,-3.68,312.26128874  ])     
                    else:
                        vector12 =  np.array([250,-3.68,312.26128874  ]) 

                    real_point = GetRealPoint(vector4,vector13,euler10_19,vector1)
                    clamp_point = GetThePinchPoint(real_point,euler10,vector12)
                    # input(f"clamp_point = {clamp_point}")
                    vector16 = copy.deepcopy(clamp_point)
                    # 根据纱锭在纸箱中的位置调整夹取深度
                    # 第5、6个纱锭（中间位置）需要额外下降补偿
                    
                    # input(f"vector16 = {vector16}")
                    if zxgs >= 4:
                        vector16[2] -= 10  # 中间纱锭额外下降8mm
                        config.log.logger.info(f"第{zxgs+1}个纱锭(中间位置)，夹取点额外下降8mm: {vector16[2]:.1f}mm")
                    # if (pos_mren[sdgs][1]>0):
                    #     euler_putVis = { 'u':0, 'v':90, 'w':90 }
                    # else:
                    #     euler_putVis = { 'u':0, 'v':90, 'w':-90 }  
                    config.log.logger.info(f"vector16 = {vector16}") 
                    config.log.logger.info(f"放置左个数:={putPos_count}")
                    # if config.putPos_index < putPos_count:
                    #     if pos_mren[sdgs][1] < 1250:
                            
                    #         euler_putVis = copy.deepcopy(config.cam_euler_left)  
                    #         # input(111111111)
                    #     else:
                    #         pos_mren[sdgs][0] = pos_mren[sdgs][0] + 270
                    #         pos_mren[sdgs][1] = pos_mren[sdgs][1] - 300
                    #         euler_putVis = copy.deepcopy(config.cam_euler_left)
                    #         euler_putVis['w'] = euler_putVis['w'] + 90
                    #         # input(222222222)
                    # else:
                    #     if pos_mren[sdgs][1] < 1250:
                    #         euler_putVis = copy.deepcopy(config.cam_euler_right)
                    #         # input(333333333)
                    #     else:
                    #         pos_mren[sdgs][0] = pos_mren[sdgs][0] - 300
                    #         pos_mren[sdgs][1] = pos_mren[sdgs][1] - 300
                    #         euler_putVis = copy.deepcopy(config.cam_euler_right)
                    #         euler_putVis['w'] = euler_putVis['w'] - 90
                    #         # input(444444444)
                    config.log.logger.info(f"放置左个数:={putPos_count}")
                    if config.putPos_index < putPos_count:
                        if  -1400 < pos_mren[sdgs][1] < 1250:
                            euler_putVis = copy.deepcopy(config.cam_euler_left)
                            # clamp_T = np.array([314.6360173, 4.62224229, 319.45580293])  # 夹取点偏移
                            #gui6.2
                            # clamp_T = np.array([270.82039642, 4.62224229, 324.26128874])  # 夹取点偏移
                            clamp_T = np.array([270.82039642 ,-3.68,312.26128874   ])  
                            clamp_point = GetThePinchPoint(pos_mren[sdgs], euler_putVis, clamp_T)
                            clamp_point[2] = config.pallet_recog_cam_height
                            # input(111111111)
                        else:
                            euler_putVis = copy.deepcopy(config.cam_euler_left)
                            euler_putVis['w'] = euler_putVis['w'] + 90
                            # clamp_T = np.array([314.6360173, 4.62224229, 319.45580293])  # 夹取点偏移
                            #gui6.2
                            # clamp_T = np.array([270.82039642, 4.62224229, 324.26128874])  # 夹取点偏移
                            clamp_T = np.array([270.82039642 ,-3.68,312.26128874   ])  
                            clamp_point = GetThePinchPoint(pos_mren[sdgs], euler_putVis, clamp_T)
                            clamp_point[2] = config.pallet_recog_cam_height
                            # input(222222222)
                    else:
                        if  -1400 < pos_mren[sdgs][1] < 1250:
                            euler_putVis = copy.deepcopy(config.cam_euler_right)
                            # clamp_T = np.array([314.6360173, 4.62224229, 319.45580293])  # 夹取点偏移
                            #gui6.2
                            # clamp_T = np.array([270.82039642, 4.62224229, 324.26128874])  # 夹取点偏移
                            clamp_T = np.array([270.82039642 ,-3.68,312.26128874   ])  
                            clamp_point = GetThePinchPoint(pos_mren[sdgs], euler_putVis, clamp_T)
                            clamp_point[2] = config.pallet_recog_cam_height
                            # input(333333333)
                        else:
                            euler_putVis = copy.deepcopy(config.cam_euler_right)
                            euler_putVis['w'] = euler_putVis['w'] - 90
                            # clamp_T = np.array([314.6360173, 4.62224229, 319.45580293])  # 夹取点偏移
                            #gui6.2
                            # clamp_T = np.array([270.82039642, 4.62224229, 324.26128874])  # 夹取点偏移
                            clamp_T = np.array([270.82039642 ,-3.68,312.26128874   ])  
                            clamp_point = GetThePinchPoint(pos_mren[sdgs], euler_putVis, clamp_T)
                            clamp_point[2] = config.pallet_recog_cam_height
                            # input(444444444)                

                    

                    poss = []
                    #800
                    poss.append({'x':int(vector16[0]*1000),'y':int(vector16[1]*1000),'z':int(vector4[2]*1000),'u':int(euler10['u']*1000),'v':int(euler10['v']*1000),'w':int(euler10['w']*1000)})
                    #806
                    poss.append({'x':int(vector16[0]*1000),'y':int(vector16[1]*1000),'z':int(vector16[2]*1000),'u':int(euler10['u']*1000),'v':int(euler10['v']*1000),'w':int(euler10['w']*1000)})
                   
                    # hight = 1170 - (2-carton_height)*Hight
                    hight = 1200 - (2-carton_height)*Hight
                    config.log.logger.info(f"过渡点hight={hight}")
                    startPos = {'x':vector16[0],'y':vector16[1],'z': hight,'u':euler10['u'],'v':euler10['v'],'w':euler10['w']}
                    EndPos = {'x':clamp_point[0],'y':clamp_point[1],'z': hight,'u':euler_putVis['u'],'v':euler_putVis['v'],'w':euler_putVis['w']}               
                    # trans,poss_arm = route_planning3(startPos,EndPos,hight)
                    # trans,poss_arm = route_planning4(startPos,EndPos,hight)
                    # EndPos = {'x':clamp_point[0],'y':clamp_point[1],'z': hight,'u':euler_putVis['u'],'v':euler_putVis['v'],'w':euler_putVis['w']}
                    # 根据托盘位置选择旋转方向：左侧顺时针(CW)，右侧逆时针(CCW)
                    # if config.putPos_index < putPos_count:
                    #     trans,poss_arm = route_planning3_cw(startPos,EndPos,hight)
                    # else:
                    #     trans,poss_arm = route_planning3_ccw(startPos,EndPos,hight)

                    if project['act_parameter']['endAddress'][0]['location'] == "R13":
                        # trans,poss_arm = route_planning3_ccw(startPos,EndPos,hight)
                        trans,poss_arm = route_planning3_auto(startPos,EndPos,hight,preferred='ccw')
                        config.log.logger.info("放置到R13")
                    elif project['act_parameter']['endAddress'][0]['location'] == "R07" or project['act_parameter']['endAddress'][0]['location'] == "R7":
                        # trans,poss_arm = route_planning3_cw(startPos,EndPos,hight)
                        trans,poss_arm = route_planning3_auto(startPos,EndPos,hight,preferred='cw')
                        config.log.logger.info("放置到R7")
                    else:
                        trans,poss_arm = route_planning3_auto(startPos,EndPos,hight,preferred='cw')
                        config.log.logger.info("放置到其他")
                    if trans == False:
                        config.action = 1001
                        continue
                    count = len(poss_arm)
                    for i in poss_arm:
                        poss.append(i) 

                    #842
                    poss.append({'x':int(clamp_point[0]*1000),'y':int(clamp_point[1]*1000),'z':int(clamp_point[2]*1000),'u':int(euler_putVis['u']*1000),'v':int(euler_putVis['v']*1000),'w':int(euler_putVis['w']*1000)})
                    
                    EndPos = {'x':clamp_point[0],'y':clamp_point[1],'z':clamp_point[2],'u':euler_putVis['u'],'v':euler_putVis['v'],'w':euler_putVis['w']}  
                    lastPos = copy.deepcopy(EndPos)
                    limit_ok = True

                    for p in poss:
                        if not CheckLimit(p, "links_action13"):
                            config.action = 1001
                            limit_ok = False
                            break
                    if not limit_ok:
                        continue

                    # input(111112)
                    config.setLinks.links_action13(poss)
                    
                    # vector74 = np.array([pos_mren[sdgs][0],pos_mren[sdgs][1],600])
                    vector74 = np.array([100,1100,600]) #
                    #UPFSdata = {
                    #    "progress": str(sdgs2+1)+"/"+str(sdgs1),
                    #    "describe":"A",
                    #    "palletInformation":project['task']['palletInformation']
                    #    }
                    #config.rcs.reportProgress("reportProgress",project['number'],UPFSdata) 
                    config.putPos_index += 1
                    sdgs += 1
                    sdgs2 += 1
                    print(8888888888888888888888888888888888888888888888888)
                    print(stateList3)
                    print(stateList4)
                    rcs2.progress = str(sdgs2) + "/" + str(sdgs1)
                    rcs2.act_status = 2
                    rcs2.arm_status = 1
                    rcs.progress = str(sdgs2) + "/" + str(sdgs1)
                    rcs.act_status = 2
                    rcs.arm_status = 1
                    rcs2.stateList1 = rcs.stateList1
                    rcs2.stateList2 = rcs.stateList2
                    stateList3,stateList4 = RCS(stateList3,stateList4,rcs,rcs2,A)
                    config.action = 18
                else: 
                    config.action = 18
         #pos_mren.remove(pos_mren[0])

        # if config.action == 17:#识别放置点，若上方有东西改放置位置
        #     if getStep() == False: 
        #         if config.hight > 1500:
        #            sdgs+=6
        #            config.action = 16
                   
     
        if config.action == 195:#移动到纸箱中心点进行高度识别
            if getStep() == False:
                center = copy.deepcopy(0.5*starVector+0.5*endVector)
                vector_box_center = GetTwiceIdentPoint(center, vector1, euler1, 800)
                
                config.vector_box_center = vector_box_center
                config.euler_box_center = euler1
                
                poss = []
                if carton_height == 2:
                    poss.append({'x':int(-0.038*1000),'y':int(18.407*1000),'z':int(-41.890*1000),'u':int(-0.098*1000),'v':int(23.482*1000),'w':int(0.087*1000)})
                else:
                    poss.append({'x':int(0*1000),'y':int(-1.408*1000),'z':int(-41.890*1000),'u':int(-0.082*1000),'v':int(55.569*1000),'w':int(0.046*1000)})
                poss.append({'x':int(vector_box_center[0]*1000),'y':int(vector_box_center[1]*1000),'z':int(vector_box_center[2]*1000),'u':int(euler1['u']*1000),'v':int(euler1['v']*1000),'w':int(euler1['w']*1000)})
                config.log.logger.info(f"poss={poss}")
                
                poss_box_center = np.array([vector_box_center[0], vector_box_center[1], vector_box_center[2]])
                poss_box_euler = euler1
                config.log.logger.info(f"poss_box_center={poss_box_center}")
                config.log.logger.info(f"poss_box_euler={poss_box_euler}")

                links = IdentificationAction3(poss_box_center, poss_box_euler, hight) 
                config.links = links
                # config.setLinks.links_action195(poss)
                config.action = 196
        
        if config.action == 196:#纸箱中心高度识别
            if getStep() == False:
                config.areaLength = int(Lenth * 2)
                config.areaWidth = int(Width * 2)
                config.links.append({'State':True, 'typeID': 14})
                config.log.logger.info(f"纸箱中心高度识别: areaLength={Lenth*2}, areaWidth={Width*2}")
                
                if config.manageConn.putVis():
                    check_height = config.hight
                    config.log.logger.info(f"纸箱中心高度: {check_height}mm")
                    if check_height < 900:
                        config.log.logger.warning(f"纸箱中心高度过低({check_height}mm < 900mm)，判断有纱锭跳过搬运")
                        config.action = 1001
                    else:
                        config.log.logger.info(f"纸箱中心高度正常({check_height}mm >= 900mm)，开始搬运")

                        euler83 = { 'u':0, 'v':90, 'w':0+derW }
                        twice_ident_point = GetTwiceIdentPoint(vector80,vector1,euler83,500)
                        vector82 = copy.deepcopy(twice_ident_point)
                        links = IdentificationAction1(vector82,euler83, hight) 
                        # config.links = IdentificationCmd3(links,17,Lenth*2,Width*2,carton_dir)
                        config.links = IdentificationCmd3(links,17,Lenth*2,Width*2,1)
                        config.action = 20
                else:
                    config.log.logger.warning("纸箱中心高度识别失败，重试")
                    config.action = 196
        
        # if config.action == 20:#抓箱子放0置动作
        #     if getStep() == False:
        #         if carton_dir == 0:
        #            euler71 = { 'u':0, 'v':90, 'w':derW-45 }
        #            euler70 = { 'u':0, 'v':90, 'w':derW }
        #            vector71 = np.array([140,-3.68,308.059])
        #            #vector71 = np.array([110,6.5,320])
                   

        #         if carton_dir == 1:
        #             euler70 = { 'u':0, 'v':90, 'w':derW }
        #             euler71 = { 'u':0, 'v':90, 'w':derW -45}
        #             vector71 = np.array([140,-3.68,308.059])
        #         # if carton0 == 0:
        #         #     carton0 = 3
        #         zxgs = 0   
        #         config.boxfull = True
        #         vector85 = np.array([config.grab['x'],config.grab['y'],config.grab['z']])  
        #         vector85_2 = revolve({ 'u':0, 'v':0, 'w':derW }, config.vectorA@vector85)
        #         vector86 = np.array([-94.182,29,440.5])
        #         # vector1 = np.array([-132.465,  37.636,  463.242])#相机偏移
        #         real_point = GetRealPoint(vector82,vector85,euler70,vector86)
        #         clamp_point = GetThePinchPoint(real_point,euler71,vector71) #抓取点
        #         vector72 = copy.deepcopy(clamp_point)


        #         #vector86_2 = revolve(euler83, vector86)
        #         #vector87 = vector82+vector86_2+vector85_2-revolve(euler70, vector71)                    
        #         #vector72 = vector80-revolve(euler70, vector71)
        #         # vector73 = np.array([-980,867,316]) #推挤放置位置
        #         # #vector75 = np.array([-1438,867,316])
        #         vector74 = np.array([100,1100,600])
        #         # vector75 = np.array([-1460,867,316])#直接放置位置
        #         # vector76 = np.array([-1300,867,316])
        #         #之间间距550 原来480
        #         vector73 = np.array([-980,867,316]) #推挤放置位置
        #         #vector75 = np.array([-1438,867,316])
        #         # vector74 = np.array([100,1100,600])
        #         vector75 = np.array([-1480,867,316])#直接放置位置
        #         vector76 = np.array([-1300,867,316])
        #         #vector72 = vector87

        #         carton = []               
        #         carton.append(np.array([0,0,0]))
        #         carton.append(np.array([0,0,320]))
        #         carton.append(np.array([0,0,640]))

        #         vector75 = vector75+carton[carton0%3]

        #         vector81 = np.array([-1300,1200,316]) #右侧
        #         vector83 = np.array([-1300,1000,316]) #左侧

                
        #         # layer_x_offset = carton_height * (-10)
        #         # vector73 = vector73 + np.array([layer_x_offset, 0, 0])
        #         # vector75 = vector75 + np.array([layer_x_offset, 0, 0])
        #         # vector76 = vector76 + np.array([layer_x_offset, 0, 0])
        #         poss = []
        #         # if carton_height ==0:
        #         #     # poss.append({'x':int(35.002*1000),'y':int(-2.235*1000),'z':int(-53.306*1000),'u':int(40.270*1000),'v':int(62.361*1000),'w':int(-21.455*1000)})
        #         #     poss.append({'x':int(vector79[0]*1000),'y':int(vector79[1]*1000),'z':int((vector79[2])*1000),'u':int((-90)*1000),'v':int(90000),'w':int(0)})
        #         # elif carton_height ==1:
        #         #     poss.append({'x':int(vector79[0]*1000),'y':int(vector79[1]*1000),'z':int((vector79[2])*1000),'u':int((-90)*1000),'v':int(90000),'w':int(0)})
        #         # elif carton_height ==2 :
        #         #     poss.append({'x':int(vector79[0]*1000),'y':int(vector79[1]*1000),'z':int((vector79[2])*1000),'u':int((-90)*1000),'v':int(90000),'w':int(0)})
        #         if carton0 <= 2 :
        #             poss.append({'x':int(vector75[0]*1000),'y':int(vector75[1]*1000),'z':int((vector75[2])*1000),'u':int(0),'v':int(90000),'w':int(90000)})
        #             print("抓箱子直接动作")
        #             config.log.logger.info("抓箱子直接动作")
        #         else:
        #             vector79 = vector75+np.array([200,0,0])
        #             # aa = True
        #             poss.append({'x':int(vector79[0]*1000),'y':int(vector79[1]*1000),'z':int((vector79[2])*1000),'u':int(0),'v':int(90000),'w':int(90000)})
        #             print("抓箱子推动动作")
        #             config.log.logger.info("抓箱子推动动作")  
                
        #         # poss.append({'x':int(vector72[0]*1000),'y':int((vector72[1]-3)*1000),'z':int((vector72[2]+200)*1000),'u':int(euler70['u']*1000),'v':int(euler70['v']*1000),'w':int(euler70['w']*1000)})
        #         # poss.append({'x':int(vector72[0]*1000),'y':int((vector72[1]-3)*1000),'z':int((vector72[2]+100)*1000),'u':int(euler70['u']*1000),'v':int(euler70['v']*1000),'w':int(euler70['w']*1000)})
        #         poss.append({'x':int(vector72[0]*1000),'y':int((vector72[1]-3)*1000),'z':int((vector82[2])*1000),'u':int(euler71['u']*1000),'v':int(euler71['v']*1000),'w':int(euler71['w']*1000)})
        #         poss.append({'x':int(vector72[0]*1000),'y':int((vector72[1]-3)*1000),'z':int((vector72[2]+100)*1000),'u':int(euler71['u']*1000),'v':int(euler71['v']*1000),'w':int(euler71['w']*1000)})                                              
                
                
        #         # if carton0%2 == 1 or carton0 == 0:
        #         #     poss.append({'x':int(vector75[0]*1000),'y':int(vector75[1]*1000),'z':int((800)*1000),'u':int((-90)*1000),'v':int(90000),'w':int(0)})
        #         #     poss.append({'x':int(vector74[0]*1000),'y':int(vector74[1]*1000),'z':int((700)*1000),'u':int(-90000),'v':int(90000),'w':int(0)})
        #         #     poss.append({'x':int(vector75[0]*1000),'y':int(vector75[1]*1000),'z':int((vector75[2])*1000),'u':int((-90)*1000),'v':int(90000),'w':int(0)})
        #         #     poss.append({'x':int(vector75[0]*1000),'y':int(vector75[1]*1000),'z':int((vector75[2])*1000),'u':int((-90)*1000),'v':int(90000),'w':int(0)})
        #         #     print("抓箱子直接动作")
        #         #     config.log.logger.info("抓箱子直接动作")
        #         # else:
        #         #     poss.append({'x':int(vector73[0]*1000),'y':int(vector73[1]*1000),'z':int((800)*1000),'u':int((-90)*1000),'v':int(90000),'w':int(0)})
        #         #     poss.append({'x':int(vector74[0]*1000),'y':int(vector74[1]*1000),'z':int((700)*1000),'u':int(-90000),'v':int(90000),'w':int(0)})
        #         #     poss.append({'x':int(vector73[0]*1000),'y':int(vector73[1]*1000),'z':int((vector73[2])*1000),'u':int((-90)*1000),'v':int(90000),'w':int(0)})
        #         #     poss.append({'x':int(vector75[0]*1000),'y':int(vector75[1]*1000),'z':int((vector75[2])*1000),'u':int((-90)*1000),'v':int(90000),'w':int(0)})
        #         #     print("抓箱子推动动作")
        #         #     config.log.logger.info("抓箱子推动动作")
        #         if carton0 <= 2 or carton0 >= 4:
        #             poss.append({'x':int(vector76[0]*1000),'y':int(vector76[1]*1000),'z':int((1150)*1000),'u':int(0),'v':int(90000),'w':int(90000)})
        #             poss.append({'x':int(vector74[0]*1000),'y':int(vector74[1]*1000),'z':int((700)*1000),'u':int(0),'v':int(90000),'w':int(90000)})
        #             poss.append({'x':int(vector75[0]*1000),'y':int(vector75[1]*1000),'z':int((vector75[2])*1000),'u':int(0),'v':int(90000),'w':int(90000)})
        #             if carton0 >= 4:
        #                 poss.append({'x':int(vector79[0]*1000),'y':int(vector79[1]*1000),'z':int((vector79[2])*1000),'u':int(0),'v':int(90000),'w':int(90000)})
        #             else:
        #                 poss.append({'x':int(vector75[0]*1000),'y':int(vector75[1]*1000),'z':int((vector75[2])*1000),'u':int(0),'v':int(90000),'w':int(90000)})
        #             print("抓箱子直接动作")
        #             hight = 1150
        #             config.log.logger.info("抓箱子直接动作")
        #         else:
        #             poss.append({'x':int(vector73[0]*1000),'y':int(vector73[1]*1000),'z':int((800)*1000),'u':int(0),'v':int(90000),'w':int(90000)})
        #             poss.append({'x':int(vector74[0]*1000),'y':int(vector74[1]*1000),'z':int((700)*1000),'u':int(0),'v':int(90000),'w':int(90000)})
        #             poss.append({'x':int(vector73[0]*1000),'y':int(vector73[1]*1000),'z':int((vector73[2])*1000),'u':int(0),'v':int(90000),'w':int(90000)})
        #             poss.append({'x':int(vector75[0]*1000),'y':int(vector75[1]*1000),'z':int((vector75[2])*1000),'u':int(0),'v':int(90000),'w':int(90000)})
        #             print("抓箱子推动动作")
        #             hight = 800
        #             config.log.logger.info("抓箱子推动动作")                    
        #         config.log.logger.info(f"carton0={carton0}")
        #         # else:
        #         #     push_offset = np.array([-100,0,0])
        #         #     push_vector = vector73 + push_offset if (carton0//3)%2 == 0 else vector75 + push_offset
        #         #     poss.append({'x':int(push_vector[0]*1000),'y':int(push_vector[1]*1000),'z':int((900)*1000),'u':int((-90)*1000),'v':int(90000),'w':int(0)})
        #         #     poss.append({'x':int(vector74[0]*1000),'y':int(vector74[1]*1000),'z':int((700)*1000),'u':int(-90000),'v':int(90000),'w':int(0)})
        #         #     poss.append({'x':int(push_vector[0]*1000),'y':int(push_vector[1]*1000),'z':int((push_vector[2])*1000),'u':int((-90)*1000),'v':int(90000),'w':int(0)})
        #         #     poss.append({'x':int(push_vector[0]*1000),'y':int(push_vector[1]*1000),'z':int((push_vector[2])*1000),'u':int((-90)*1000),'v':int(90000),'w':int(0)})

                
        #         startPos = {'x':vector72[0],'y':vector72[1],'z': hight,'u':0,'v':90,'w':-45}
        #         EndPos = {'x':vector73[0],'y':vector73[1],'z': hight,'u':0,'v':90,'w':90}               
        #         trans,poss_arm = route_planning(startPos,EndPos,hight)
        #         if trans == False:
        #             config.action = 1001
        #             continue
        #         #poss = copy.deepcopy(poss_arm)
        #         count = len(poss_arm)
        #         config.log.logger.info(f"count={count},poss_arm={poss_arm}")
        #         for i in poss_arm:
        #             poss.append(i) 
        #         for i in range(0,7-count):
        #             poss.append(poss_arm[count-1]) 

        #         limit_ok = True
        #         for p in poss:
        #             if not CheckLimit(p, "links_action14"):
        #                 config.action = 1001
        #                 limit_ok = False
        #                 break
        #         if not limit_ok:
        #             continue
        #         config.log.logger.info(f"箱子poss={poss}")
        #         config.setLinks.links_action14(poss)

        #         carton0 +=1
        #         if carton0 == 6:
        #             carton0 = 0
        #             # config.action = 102
                
        #         config.action = 21
        
        if config.action == 20:#抓箱子放0置动作
            if getStep() == False:
                if carton_dir == 0:
                   anglew = config.grab['w']
                   euler71 = { 'u':0, 'v':90, 'w':derW -45 - anglew }
                   angle = config.grab['w']
                   euler70 = { 'u':0, 'v':90, 'w':derW }
                #    vector71 = np.array([140,-3.68,308.059])
                #    vector71 =  np.array([140 ,-3.68,312.26128874   ]) 
                #    vector71 =  np.array([120  ,-3.68,312.26128874   ]) 
                #    vector71 =  np.array([105  ,-3.68,312.26128874   ]) 
                   vector71 =  np.array([105  ,7,312.26128874   ])
                   #vector71 = np.array([110,6.5,320])
                   

                if carton_dir == 1:
                    anglew = config.grab['w']
                    euler70 = { 'u':0, 'v':90, 'w':derW }
                    euler71 = { 'u':0, 'v':90, 'w':derW -45 - anglew }
                    # vector71 = np.array([140,-3.68,308.059])
                    # vector71 = np.array([140 ,-3.68,312.26128874   ]) 
                    # vector71 = np.array([105 ,-3.68,312.26128874   ]) 
                    vector71 = np.array([105 ,7,312.26128874   ]) 
                # if carton0 == 0:
                #     carton0 = 3
                zxgs = 0   
                config.boxfull = True
                vector85 = np.array([config.grab['x'],config.grab['y'],config.grab['z']])  
                vector85_2 = revolve({ 'u':0, 'v':0, 'w':derW }, config.vectorA@vector85)
                # vector86 = np.array([-94.182,29,440.5])
                vector86 = np.array([-132.465,  37.636,  463.242])#相机偏移
                # vector1 = np.array([-132.465,  37.636,  463.242])#相机偏移
                real_point = GetRealPoint(vector82,vector85,euler70,vector86)
                clamp_point = GetThePinchPoint(real_point,euler71,vector71) #抓取点
                vector72 = copy.deepcopy(clamp_point)


                #vector86_2 = revolve(euler83, vector86)
                #vector87 = vector82+vector86_2+vector85_2-revolve(euler70, vector71)                    
                #vector72 = vector80-revolve(euler70, vector71)
                # vector73 = np.array([-980,867,316]) #推挤放置位置
                # #vector75 = np.array([-1438,867,316])
                vector74 = np.array([100,1100,600])
                # vector75 = np.array([-1460,867,316])#直接放置位置
                # vector76 = np.array([-1300,867,316])
                #之间间距550 原来480
                vector73 = np.array([-980,867,310]) #推挤放置位置
                #vector75 = np.array([-1438,867,316])
                # vector74 = np.array([100,1100,600])
                vector75 = np.array([-1480,867,310])#直接放置位置
                # vector76 = np.array([-1300,867,310])
                vector76 =np.array([-1300,1000,310]) #左侧
                #vector72 = vector87

                carton = []               
                carton.append(np.array([0,0,0]))
                carton.append(np.array([0,0,300]))
                carton.append(np.array([0,0,600]))

                #vector75 = vector75+carton[carton0//2]
                # vector75 = vector75+carton[carton0%2]
                
                if carton0 <= 2:#carton_dir == 0:
                    vector81 = np.array([-1301,1264,280]) #右侧
                    hight = 950
                else:
                    vector81 = np.array([-1301,1050,280]) #左侧
                    hight = 1200
                vector81 = vector81+carton[carton0%3]

                poss = []
                if carton0 <= 2:
                    # vector81 = vector81+np.array([0,30,0])
                    # vector81 = vector81+np.array([0,10,0])
                    poss.append({'x':int(vector81[0]*1000),'y':int(vector81[1]*1000),'z':int((vector81[2]+20)*1000),'u':int(0),'v':int(90000),'w':int(135000)})
                    poss.append({'x':int(vector72[0]*1000),'y':int((vector72[1]-3)*1000),'z':int((vector82[2])*1000),'u':int(euler71['u']*1000),'v':int(euler71['v']*1000),'w':int(euler71['w']*1000)})
                    poss.append({'x':int(vector72[0]*1000),'y':int((vector72[1]-3)*1000),'z':int((vector72[2]+70)*1000),'u':int(euler71['u']*1000),'v':int(euler71['v']*1000),'w':int(euler71['w']*1000)})     
                    poss.append({'x':int(vector76[0]*1000),'y':int(vector76[1]*1000),'z':int((950)*1000),'u':int(0),'v':int(90000),'w':int(135000)})
                    poss.append({'x':int(vector81[0]*1000),'y':int(vector81[1]*1000),'z':int((vector81[2])*1000),'u':int(0),'v':int(90000),'w':int(135000)})
                    poss.append({'x':int(vector81[0]*1000),'y':int(vector81[1]*1000),'z':int((vector81[2])*1000),'u':int(0),'v':int(90000),'w':int(135000)})
                    poss.append({'x':int(vector81[0]*1000),'y':int(vector81[1]*1000),'z':int((vector81[2])*1000),'u':int(0),'v':int(90000),'w':int(135000)})
                    print("抓箱子直接动作")
                    hight = 950
                    config.log.logger.info("抓箱子直接动作")
                elif carton0 == 3:
                    # vector76 = np.array([-1308,690,310])
                    vector76 = np.array([-955,595,310])
                    poss.append({'x':int(vector81[0]*1000),'y':int(vector81[1]*1000),'z':int((vector81[2]+70)*1000),'u':int(0),'v':int(90000),'w':int(135000)})
                    poss.append({'x':int(vector72[0]*1000),'y':int((vector72[1]-3)*1000),'z':int((vector82[2])*1000),'u':int(euler71['u']*1000),'v':int(euler71['v']*1000),'w':int(euler71['w']*1000)})
                    poss.append({'x':int(vector72[0]*1000),'y':int((vector72[1]-3)*1000),'z':int((vector72[2]+70)*1000),'u':int(euler71['u']*1000),'v':int(euler71['v']*1000),'w':int(euler71['w']*1000)})   
                    print("抓箱子推动动作")
                    config.log.logger.info("抓箱子推动动作")
                    poss.append({'x':int(vector76[0]*1000),'y':int(vector76[1]*1000),'z':int((950)*1000),'u':int(0),'v':int(90000),'w':int(135000)})
                    poss.append({'x':int(vector76[0]*1000),'y':int(vector76[1]*1000),'z':int((420)*1000),'u':int(0),'v':int(90000),'w':int(135000)})
                    poss.append({'x':int(vector81[0]*1000),'y':int(vector81[1]*1000),'z':int((420)*1000),'u':int(0),'v':int(90000),'w':int(135000)})
                    poss.append({'x':int(vector81[0]*1000),'y':int(vector81[1]*1000),'z':int((vector81[2]+70)*1000),'u':int(0),'v':int(90000),'w':int(135000)})
                    vector81 = np.array([-1308,720,310])
                    hight = 1200
                elif carton0 >= 4:
                    # vector76 = np.array([-1308,690,310])
                    vector76 =np.array([-1300,1000,310]) #左侧
                    poss.append({'x':int(vector81[0]*1000),'y':int(vector81[1]*1000),'z':int((vector81[2]+20)*1000),'u':int(0),'v':int(90000),'w':int(135000)})
                    poss.append({'x':int(vector72[0]*1000),'y':int((vector72[1]-3)*1000),'z':int((vector82[2])*1000),'u':int(euler71['u']*1000),'v':int(euler71['v']*1000),'w':int(euler71['w']*1000)})
                    poss.append({'x':int(vector72[0]*1000),'y':int((vector72[1]-3)*1000),'z':int((vector72[2]+70)*1000),'u':int(euler71['u']*1000),'v':int(euler71['v']*1000),'w':int(euler71['w']*1000)})   
                    print("抓箱子推动动作")
                    config.log.logger.info("抓箱子推动动作")
                    poss.append({'x':int(vector76[0]*1000),'y':int(vector76[1]*1000),'z':int((1000)*1000),'u':int(0),'v':int(90000),'w':int(135000)})
                    poss.append({'x':int(vector76[0]*1000),'y':int(vector76[1]*1000),'z':int((910)*1000),'u':int(0),'v':int(90000),'w':int(135000)})
                    poss.append({'x':int(vector81[0]*1000),'y':int(vector81[1]*1000),'z':int((910)*1000),'u':int(0),'v':int(90000),'w':int(135000)})
                    poss.append({'x':int(vector81[0]*1000),'y':int(vector81[1]*1000),'z':int((vector81[2]+20)*1000),'u':int(0),'v':int(90000),'w':int(135000)})
                    # vector81 = np.array([-1308,690,310])
                    vector81 = np.array([-1308,720,310])
                    hight = 1200
                
                config.log.logger.info("抓箱子推动动作 ")                    
                config.log.logger.info(f"carton0={carton0}")
                # else:
                #     push_offset = np.array([-100,0,0])
                #     push_vector = vector73 + push_offset if (carton0//3)%2 == 0 else vector75 + push_offset
                #     poss.append({'x':int(push_vector[0]*1000),'y':int(push_vector[1]*1000),'z':int((900)*1000),'u':int((-90)*1000),'v':int(90000),'w':int(0)})
                #     poss.append({'x':int(vector74[0]*1000),'y':int(vector74[1]*1000),'z':int((700)*1000),'u':int(-90000),'v':int(90000),'w':int(0)})
                #     poss.append({'x':int(push_vector[0]*1000),'y':int(push_vector[1]*1000),'z':int((push_vector[2])*1000),'u':int((-90)*1000),'v':int(90000),'w':int(0)})
                #     poss.append({'x':int(push_vector[0]*1000),'y':int(push_vector[1]*1000),'z':int((push_vector[2])*1000),'u':int((-90)*1000),'v':int(90000),'w':int(0)})

                
                startPos = {'x':vector72[0],'y':vector72[1],'z': hight,'u':0,'v':90,'w':-45}
                if carton0 >= 4:
                    EndPos = {'x':vector81[0],'y':vector81[1],'z': hight,'u':0,'v':90,'w':135} 
                else:
                    EndPos = {'x':vector81[0],'y':vector81[1],'z': hight,'u':0,'v':90,'w':135}               
                trans,poss_arm = route_planning(startPos,EndPos,hight)
                if trans == False:
                    config.action = 1001
                    continue
                #poss = copy.deepcopy(poss_arm)
                count = len(poss_arm)
                config.log.logger.info(f"count={count},poss_arm={poss_arm}")
                for i in poss_arm:
                    poss.append(i) 
                for i in range(0,7-count):
                    poss.append(poss_arm[count-1]) 

                limit_ok = True
                for p in poss:
                    if not CheckLimit(p, "links_action14"):
                        config.action = 1001
                        limit_ok = False
                        break
                if not limit_ok:
                    continue
                config.log.logger.info(f"箱子poss={poss}")
                config.setLinks.links_action14(poss)

                carton0 +=1
                if carton0 == 6:
                    carton0 = 0
                    # config.action = 102
                
                config.action = 21

        if config.action == 21:#循环
            if getStep() == False:
                cartonCount += 1
                if carton_height >= 0 :
                    if carton_dir == 0 :
                        carton_dir = 1
                    else: 
                        carton_dir = 0
                        # if cartonCount % 3 == 0:
                        carton_height -= 1
                    after_place = True  # 放置纸箱后跳回action 1，过渡点用1150
                    config.action = 1
                if carton_height == -1:
                    config.action = 1000
                    rcs.act_status = 4
                    rcs2.act_status = 4
                    rcs.arm_status = 0
                    rcs2.arm_status = 0
                    #sdgs1
                if sdgs1 <= sdgs2 :
                    
                    print(f"sdgs = {sdgs1}")
                    print(f"sdgs2 = {sdgs2}")
                    # input(1)
                    config.action = 1000
                    rcs.act_status = 4
                    rcs2.act_status = 4
                    rcs.arm_status = 0
                    rcs2.arm_status = 0
                    rcs.CurrentStatus = "Idle"
                #gui
                # if sdgs2 >= 12:
                if sdgs2 >= config.fznumber:
                    print(f"sdgs2 = {sdgs2},real_spindle_count = {real_spindle_count}")
                    #input(2)
                    config.action = 1000
                    rcs.act_status = 4
                    rcs2.act_status = 4
                    rcs.arm_status = 0
                    rcs2.arm_status = 0
                    rcs.CurrentStatus = "Idle"
                #if cartonCount == 2:
                #    config.action = 99999999

        if config.action == 101:#纱锭托盘满
            if getStep() == False:
                sdgs = 0

        if config.action == 100: #结束回复
            if getStep() == False:
                flag_a = 0
                config.action = 133
                if carton_height == -1:
                    config.action = 99999999
                    break
        if config.action == 1000: #结束回复
            if getStep() == False:
                flag_a = 0
                config.log.logger.info("任务完成，等待新任务...")
                
                if carton_height == -1:
                    carton_dir = 0
                    carton_height = 2
                count = 0
                # carton0 = 0
                sdgs = 0
                sdgs1 = 0
                sdgs2 = 0
                
                config.putPos_index = 0
                config.fznumber = 1
                frequency = 0
                cartonCount = 0
                putPos_count = 0
                config.circles_identify_count = 0  # 重置识别次数
                a = 0
                if config.boxfull:
                    #加入机械臂回到初始点的动作
                    vectorStart = np.array([config.currentPos['x'],config.currentPos['y'],config.currentPos['z']])
                    eulerStart = { 'u':config.currentPos['u'], 'v':config.currentPos['v'], 'w':config.currentPos['w'] }
                    config.database.insert(str(current_time),0,vectorStart[0],vectorStart[1],vectorStart[2],eulerStart['u'],eulerStart['v'],eulerStart['w'])
                    hight = 1000
                    startPos = copy.deepcopy(config.currentPos)
                    # EndPos = {'x':583,'y':1101,'z':hight,'u':0,'v':90,'w':0}    
                    EndPos = {'x':583,'y':1101,'z':hight,'u':0,'v':90,'w':0}             
                    trans,poss_arm = route_planning(startPos,EndPos,hight)
                    poss = copy.deepcopy(poss_arm)
                    count = len(poss_arm)
                    for i in range(0,8-count):
                        poss.append(poss_arm[len(poss_arm)-1])
                    config.links = config.setLinks.links_action22(poss)#回到初始点 
                while a == 0:
                    project = rcs.business_queue.get()
                    rcs2.act_parameter = project['act_parameter']
                    print("新任务参数:", rcs2.act_parameter)
                    rcs2.act_id = rcs.act_id
                    rcs2.act_name = rcs.act_name
                    print("新任务:", project)
                    # time.sleep(1)
                    if project['act_name'] == 'CXQS':
                        rcs2.act_parameter = rcs.act_parameter
                        rcs2.act_id = rcs.act_id
                        rcs2.act_name = rcs.act_name
                        stateList3 = project['act_parameter']['startAddress'][0]['count']
                        stateList4 = project['act_parameter']['endAddress'][0]['count']
                        rcs2.act_parameter = rcs.act_parameter
                        rcs2.progress = str(0) + "/" + str(project['act_parameter']['count'])
                        rcs2.act_status = 2
                        rcs2.arm_status = 1
                        rcs.progress = str(0) + "/" + str(project['act_parameter']['count'])
                        rcs.act_status = 2
                        rcs.arm_status = 1
                        rcs.cc = 0
                        rcs2.cc = rcs.cc
                        rcs2.stateList1 = rcs.stateList1
                        rcs2.stateList2 = rcs.stateList2
                        materialID = project['act_parameter']['materialID']
                        config.carton_numder = MatchCartonByMaterial(materialID)
                        config.log.logger.info(f"新任务 - 物料ID: {materialID}, 匹配纸箱类型: {config.carton_numder}")
                        a = 1
                        sdgs1 = project['act_parameter']['count']
                        A = project['act_parameter']['count']
                        if config.boxfull:
                            zxgs = 0
                            config.action = 133
                        else:
                            
                            config.action = 160
        if config.action == 1001: #结束回复
            if getStep() == False:
                rcs.act_status = 5
                rcs2.act_status = 5
                rcs.arm_status = 2
                rcs2.arm_status = 2
                flag_a = 0
                config.log.logger.info("任务失败，等待新任务...")
                
                # if carton_height == -1:
                #     carton_dir = 0
                #     carton_height = 2
                carton_dir = 0
                carton_height = 2
                count = 0
                carton0 = 0
                sdgs = 0
                sdgs1 = 0
                sdgs2 = 0
                # zxgs = 0
                config.putPos_index = 0
                config.fznumber = 1
                putPos_count = 0
                frequency = 0
                cartonCount = 0
                config.circles_identify_count = 0  # 重置识别次数
                a = 0
                while a == 0:
                    project = rcs.business_queue.get()
                    rcs2.act_parameter = project['act_parameter']
                    print("新任务参数:", rcs2.act_parameter)
                    rcs2.act_id = rcs.act_id
                    rcs2.act_name = rcs.act_name
                    print("新任务:", project)
                    #time.sleep(1)
                    if project['act_name'] == 'CXQS':
                        rcs2.act_parameter = rcs.act_parameter
                        rcs2.act_id = rcs.act_id
                        rcs2.act_name = rcs.act_name
                        stateList3 = project['act_parameter']['startAddress'][0]['count']
                        stateList4 = project['act_parameter']['endAddress'][0]['count']
                        rcs2.act_parameter = rcs.act_parameter
                        rcs2.progress = str(0) + "/" + str(project['act_parameter']['count'])
                        rcs2.act_status = 2
                        rcs2.arm_status = 1
                        rcs.progress = str(0) + "/" + str(project['act_parameter']['count'])
                        rcs.act_status = 2
                        rcs.arm_status = 1
                        rcs.cc = 0
                        rcs2.cc = rcs.cc
                        rcs2.stateList1 = rcs.stateList1
                        rcs2.stateList2 = rcs.stateList2
                        materialID = project['act_parameter']['materialID']
                        config.carton_numder = MatchCartonByMaterial(materialID)
                        config.log.logger.info(f"新任务 - 物料ID: {materialID}, 匹配纸箱类型: {config.carton_numder}")
                        a = 1
                        sdgs1 = project['act_parameter']['count']
                        A = project['act_parameter']['count']
                        # config.action = 133
                        if config.boxfull:
                            zxgs = 0
                            config.action = 133
                        else:
                            
                            config.action = 160
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