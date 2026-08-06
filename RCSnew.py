import threading
import socket
import json
import queue
import time
import os
from tkinter import SE
import traceback
import datetime
import logging
from logging import handlers
# 配置日志
#logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RobotData:
    def __init__(self):
        self.aa = "false"
        self.code2 = "0"


# 省略其他重复代码，仅标注关键修改点
class RCSServer(threading.Thread):
    def __init__(self, shared: RobotData,host='0.0.0.0', port=23311):
        super().__init__()
        self.shared = shared
        self.host = host
        self.port = port
        self.CurrentStatus = "Idle"
        self.server_socket = None
        self.singleAct = None
        self.Management = None
        self.EmergencyStop1 = 0
        self.log = loginit()
        # 初始化队列
        self.business_queue = queue.Queue()      # RCS
        self.business_queue1 = queue.Queue()     # RCS2
        self.business_queue2 = queue.Queue()     # RCS3 (急停)
        self.business_queue3 = queue.Queue()     # 其他

        self.businessState = 1
        self.businessState1 = 1

        # 创建 socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.log.logger.info(f"RCS TCP 服务端启动，监听 {host}:{port}")

        #反馈参数
        self.ret_code = 0
        self.create_time = 0
        self.err_msg = "None"
        self.desc = "None"
        self.act_status = 0
        self.arm_status = 0
        self.act_name = 0
        self.act_id = 0
        self.act_parameter = {}
        self.progress = "0/0"
        self.code = "0"
        self.cs = 0
        self.time = 0
        self.error = {}
        self.aa = "false"
        self.a23 = 0
        self.cc = 0
        self.stateList1 = "empty"
        self.stateList2 = "empty"
        self.Tray = 0

        # 报警信息管理（移植自报警系统设计文档）
        self.alarm_list = []          # 报警列表
        self.alarm_counter = {}       # 按报警码计数
        self.task_error_msg = ""      # 任务错误信息（英文）

    def add_alarm(self, level, code, desc, describe="", method="", reason=""):
        """添加报警信息"""
        code_str = str(code)
        if code_str in self.alarm_counter:
            self.alarm_counter[code_str]["times"] += 1
        else:
            alarm_item = {
                "code": code_str,
                "desc": desc,
                "times": 1,
                "stime": int(time.time()),
                "describe": describe,
                "method": method,
                "reason": reason,
                "level": level
            }
            self.alarm_counter[code_str] = alarm_item
            self.alarm_list.append(alarm_item)

    def clear_alarm(self, code):
        """清除指定报警码"""
        code_str = str(code)
        if code_str in self.alarm_counter:
            del self.alarm_counter[code_str]
            self.alarm_list[:] = [a for a in self.alarm_list if a["code"] != code_str]

    def run(self):
        try:
            while True:
                client, addr = self.server_socket.accept()
                self.log.logger.info(f"新连接: {addr}")
                t = threading.Thread(target=self.handle_client, args=(client, addr))
                t.daemon = True
                t.start()
        except Exception as e:
            self.log.logger.error(f"服务端崩溃: {e}")
            traceback.print_exc()

    def handle_client(self, sock, addr):
        try:
            while True:
                #接收 10 字节头部
                header = self.recv_all(sock, 10)
                if not header:
                    break

                # 解析头部
                sync_byte = header[0]
                version = header[1]
                seq_num = int.from_bytes(header[2:4], 'big')
                msg_type = int.from_bytes(header[4:6], 'big')
                data_len = int.from_bytes(header[6:10], 'big')

                # 验证同步字节和版本
                if sync_byte != 0xAC or version != 0x01:
                    self.log.logger.warning(f"无效包头: sync={hex(sync_byte)}, ver={version}")
                    print(sync_byte)
                    print(version)
                    continue

                # 接收 JSON 数据
                json_data = b''
                if data_len > 0:
                    json_data = self.recv_all(sock, data_len)
                    if not json_data:
                        break

                # 解析 JSON（如果存在）
                payload = {}
                if json_data:
                    try:
                        payload = json.loads(json_data.decode('utf-8'))
                        self.log.logger.info(f"收到消息 [seq={seq_num}, type={msg_type}]: {payload}")
                    except Exception as e:
                        self.log.logger.error(f"JSON 解析失败: {e}")
                        self.send_error(sock, seq_num, "Invalid JSON")
                        continue

                #  根据报文类型分发
                if msg_type == 2200:  # taskStart / RCS
                    # self.singleAct.EmergencyStop = 0
                    self.a23 = 0
                    required = ['act_name', 'act_id', 'act_parameter']
                    required2 = ['materialID','count','startAddress','endAddress']
                    required3 = ['location','number','count','stateList']
                    self.act_name = payload['act_name']
                    self.act_id = payload['act_id']
                    self.act_parameter = payload['act_parameter']
                    if all(k in payload for k in required):
                        if self.CurrentStatus == "Idle":
                            self.stateList1 = self.act_parameter['startAddress'][0]['stateList']
                            self.stateList2 = self.act_parameter['endAddress'][0]['stateList']
                            self.CurrentStatus = "Busy"
                            self.business_queue.put(payload)
                            if self.act_parameter['endAddress'][0]['location'] != []:
                                if self.act_parameter['endAddress'][0]['location'] == 'RO1':
                                    self.Tray = 0
                                elif self.act_parameter['endAddress'][0]['location'] == 'RO2':
                                    self.Tray = 1
                                else:
                                    self.Tray = 0
                            report_data = {
                                "ret_code": 0,
                                "create_time":str(time.time()),
                                "err_msg": 0
                            }
                            new_msg_type = msg_type + 10000
                            packet = self.build_packet(seq_num, new_msg_type, report_data)
                            sock.sendall(packet)
                        elif self.CurrentStatus == "Busy":
                            report_data = {
                                "ret_code": 40102,
                                "create_time":str(time.time()),
                                "err_msg": "robot_Busy"
                            }
                            new_msg_type = msg_type + 10000
                            packet = self.build_packet(seq_num, new_msg_type, report_data)
                            sock.sendall(packet)
                        elif payload['act_name'] != 'CXQS':
                            report_data = {
                                "ret_code": 40102,
                                "create_time":str(time.time()),
                                "err_msg": "Task_does_not_exist"
                            }
                            new_msg_type = msg_type + 10000
                            packet = self.build_packet(seq_num, new_msg_type, report_data)
                            sock.sendall(packet)
                        elif all(k in payload['act_parameter'] for k in required2):
                            report_data = {
                                "ret_code": 40001,
                                "create_time":str(time.time()),
                                "err_msg": "param_missing"
                            }
                            new_msg_type = msg_type + 10000
                            packet = self.build_packet(seq_num, new_msg_type, report_data)
                            sock.sendall(packet)
                        elif all(k in payload['act_parameter']['startAddress'][0] for k in required3):
                            report_data = {
                                "ret_code": 40001,
                                "create_time":str(time.time()),
                                "err_msg": "param_missing"
                            }
                            new_msg_type = msg_type + 10000
                            packet = self.build_packet(seq_num, new_msg_type, report_data)
                            sock.sendall(packet)
                        elif all(k in payload['act_parameter']['endAddress'][0] for k in required3):
                            report_data = {
                                "ret_code": 40001,
                                "create_time":str(time.time()),
                                "err_msg": "param_missing"
                            }
                            new_msg_type = msg_type + 10000
                            packet = self.build_packet(seq_num, new_msg_type, report_data)
                            sock.sendall(packet)
                    else:
                        self.send_error(sock, seq_num, "Missing fields")
                
                elif msg_type == 2201:  # 继续动作
                    # self.EmergencyStop1 = 0
                    self.act_status = 2
                    self.arm_status = 1
                    resp = {
                        "ret_code": 0,
                        "create_time": str(time.time()),
                        "err_msg": self.err_msg
                    }
                    new_msg_type = msg_type + 10000
                    packet = self.build_packet(seq_num, new_msg_type, resp)
                    sock.sendall(packet)

                elif msg_type == 2202:  # 暂停动作
                    # self.EmergencyStop1 = 1
                    self.act_status = 3
                    self.arm_status = 2
                    resp = {
                        "ret_code": 0,
                        "create_time": str(time.time()),
                        "err_msg": self.err_msg
                    }
                    new_msg_type = msg_type + 10000
                    packet = self.build_packet(seq_num, new_msg_type, resp)
                    sock.sendall(packet)

                elif msg_type == 2203:  # 取消动作
                    self.act_status = 6
                    target = {'x': 2017, 'y': 96, 'z': 1700, 'u': 180, 'v': 0, 'w': 180, 'ID': 0}
                    # result = self.singleAct.rotate(target, 1700, 20)
                    # self.singleAct.EmergencyStop = 1
                    # self.a23 = 1
                    # self.singleAct.cancel()
                    # self.singleAct.cancel()
                    # 清除任务相关报警，避免下一个任务接收到残留报警
                    self.clear_alarm("1030")
                    self.clear_alarm("1032")
                    self.ret_code = 0
                    self.err_msg = "0"
                    self.task_error_msg = ""
                    resp = {
                        "ret_code": 0,
                        "create_time": str(time.time()),
                        "err_msg": self.err_msg
                    }
                    self.CurrentStatus = "Idle"
                    new_msg_type = msg_type + 10000
                    packet = self.build_packet(seq_num, new_msg_type, resp)
                    sock.sendall(packet)
                    self.log.logger.info("任务已取消，清除任务报警(1030, 1032)")
                elif msg_type == 1024:  # 动作进度
                    if 'startAddress' in self.act_parameter and 'endAddress' in self.act_parameter:
                        start_addr = self.act_parameter['startAddress']
                        end_addr = self.act_parameter['endAddress']
                        if start_addr and end_addr and len(start_addr) > 0 and len(end_addr) > 0:
                            s = start_addr[0]
                            e = end_addr[0]
                            if 'number' in s and 'number' in e:
                                startAddress = [{
                                    "location": s.get('location', ''),
                                    "number": s['number'],
                                    "count": s.get('count', 0) - self.cc,
                                    "stateList": self.stateList1,
                                }]
                                endAddress = [{
                                    "location": e.get('location', ''),
                                    "number": e['number'],
                                    "count": e.get('count', 0) + self.cc,
                                    "stateList": self.stateList2,
                                }]
                            else:
                                startAddress = ["1"]
                                endAddress = ["1"]
                        else:
                            startAddress = ["1"]
                            endAddress = ["1"]
                    else:
                        startAddress = ["2"]
                        endAddress = ["2"]
                    a = {
                        "progress":self.progress,
                        "startAddress":startAddress,
                        "endAddress": endAddress
                    }
                    resp = {
                        "ret_code": self.ret_code,
                        "create_time": str(time.time()),
                        "err_msg": self.task_error_msg if self.task_error_msg else "0",
                        "act_status": self.act_status,
                        "arm_status": self.arm_status,
                        "act_name": self.act_name,
                        "act_id": self.act_id,
                        "act_data":a
                    }
                    new_msg_type = msg_type + 10000
                    packet = self.build_packet(seq_num, new_msg_type, resp)
                    sock.sendall(packet)
 
                elif msg_type == 1007:  # 设备急停信息
                    #if self.singleAct.EmergencyStop == 1:
                    #    self.aa = "true"
                    #if self.singleAct.EmergencyStop == 0:
                    self.aa = "false"
                    resp = {
                        "arm_emc": "false",
                        "soft_emc": self.shared.aa,
                        "ret_code": self.ret_code,
                        "create_time": str(time.time()),
                        "err_msg": 0
                    }
                    new_msg_type = msg_type + 10000
                    packet = self.build_packet(seq_num, new_msg_type, resp)
                    sock.sendall(packet)
                elif msg_type == 1013:  # 设备报警信息
                    # 收集报警信息：errors / warnings / notices
                    errors_list = []
                    warnings_list = []
                    notices_list = []

                    # 1. 来自报警管理器的报警（设备掉线/任务异常等）
                    for a in self.alarm_list:
                        item = {
                            "code": a["code"],
                            "desc": a["desc"],
                            "times": a["times"],
                            "stime": a["stime"]
                        }
                        if a.get("level") == "error":
                            errors_list.append(item)
                        elif a.get("level") == "warning":
                            warnings_list.append(item)
                        else:
                            notices_list.append(item)

                    # 2. 软急停（emc）报警，保留原有逻辑
                    if self.shared.code2 != "0":
                        errors_list.append({
                            "code": "40016",
                            "desc": "emc_status",
                            "times": 1,
                            "stime": int(self.time) if self.time else int(time.time())
                        })
                    elif self.code != "0":
                        errors_list.append({
                            "code": self.code,
                            "desc": self.desc,
                            "times": self.cs,
                            "stime": int(self.time) if self.time else int(time.time())
                        })

                    # 3. 组装响应
                    resp = {
                        "ret_code": self.ret_code,
                        "create_time": str(time.time()),
                        "err_msg": "0"
                    }
                    if errors_list:
                        resp["errors"] = errors_list
                    if warnings_list:
                        resp["warnings"] = warnings_list
                    if notices_list:
                        resp["notices"] = notices_list
                    new_msg_type = msg_type + 10000
                    packet = self.build_packet(seq_num, new_msg_type, resp)
                    sock.sendall(packet)
                elif msg_type == 2300:  # 设备软急停
                    if payload['status'] == True:
                        print('1')
                        self.shared.aa = "true"
                        self.shared.code2 = "40016"
                        self.singleAct.robotInit55()
                    else:
                        print('2')
                        self.shared.aa = "false"
                        self.shared.code2 = "0"
                        self.singleAct.robotInit()
                        self.singleAct.robotInit()
                    resp = {
                        "ret_code": self.ret_code,
                        "create_time": str(time.time()),
                        "err_msg": "0"
                    }
                    new_msg_type = msg_type + 10000
                    packet = self.build_packet(seq_num, new_msg_type, resp)
                    sock.sendall(packet)
                else:
                    resp = {
                        "ret_code": 60001,
                        "create_time": str(time.time()),
                        "err_msg": "Unknown message type",
                    }
                    new_msg_type = msg_type + 10000
                    packet = self.build_packet(seq_num, new_msg_type, resp)
                    sock.sendall(packet)
                    self.log.logger.warning(f"未知报文类型: {msg_type}")

        except Exception as e:
            self.log.logger.error(f"客户端 {addr} 异常: {e}")
            self.log.logger.error("详细堆栈：\n" + traceback.format_exc())
        finally:
            sock.close()
            self.log.logger.info(f"连接 {addr} 关闭")

    def recv_all(self, sock, n):
        """可靠接收 n 字节"""
        data = bytearray()
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data

    def build_packet(self,seq_num, msg_type, json_dict):
        """构造符合协议的二进制包"""
        print(msg_type)
        json_bytes = json.dumps(json_dict, ensure_ascii=False).encode('utf-8')
        header = bytearray(10)
        header[0] = 0xAC               # 同步字节
        header[1] = 0x01               # 协议版本
        header[2:4] = seq_num.to_bytes(2, 'big')      # 序号（回传）
        header[4:6] = msg_type.to_bytes(2, 'big')     # 报文类型
        print(header[4:6])
        header[6:10] = len(json_bytes).to_bytes(4, 'big')  # 数据长度
        return header + json_bytes

    def send_response(self, sock, seq_num, msg_type, data):
        try:
            packet = self.build_packet(seq_num, msg_type, data)
            sock.sendall(packet)
            self.log.logger.debug(f"已发送响应 [seq={seq_num}]")
        except Exception as e:
            self.log.logger.error(f"发送响应失败: {e}")

    def send_success(self, sock, seq_num, data=None):
        data = data or {"code": 0, "msg": "success"}
        self.send_response(sock, seq_num, 0, data)  # 响应类型可设为 0 或原类型

    def send_error(self, sock, seq_num, msg):
        self.send_response(sock, seq_num, 0xFFFF, {"error": msg})

    def RCS(self,stateList3,stateList4,robot, robot2):
        stateList3 -= 1
        stateList4 += 1
        robot2.progress = robot.progress
        robot.cc += 1
        robot2.cc = robot.cc
        if robot.stateList1 == "empty" and 0 < stateList3 < 6:
            robot.stateList1 = "half_full"
            robot2.stateList1 = robot.stateList1
        if robot.stateList1 == "empty" and stateList3 >= 6:
            robot.stateList1 = "full"
            robot2.stateList1 = robot.stateList1
        if robot.stateList1 == "full" and 0 < stateList3 < 6:
            robot.stateList1 = "half_full"
            robot2.stateList1 = robot.stateList1
        if robot.stateList1 == "full" and stateList3 == 0:
            robot.stateList1 = "empty"
            robot2.stateList1 = robot.stateList1
        if robot.stateList1 == "half_full" and stateList3 == 0:
            robot.stateList1 = "empty"
            robot2.stateList1 = robot.stateList1
        if robot.stateList1 == "half_full" and stateList3 >= 6:
            robot.stateList1 = "full"
            robot2.stateList1 = robot.stateList1

        if robot.stateList2 == "empty" and 0 < stateList4 < 6:
            robot.stateList2 = "half_full"
            robot2.stateList2 = robot.stateList2
        if robot.stateList2 == "empty" and stateList4 >= 6:
            robot.stateList2 = "full"
            robot2.stateList2 = robot.stateList2
        if robot.stateList2 == "full" and 0 < stateList4 < 6:
            robot.stateList2 = "half_full"
            robot2.stateList2 = robot.stateList2
        if robot.stateList2 == "full" and stateList4 == 0:
            robot.stateList2 = "empty"
            robot2.stateList2 = robot.stateList2
        if robot.stateList2 == "half_full" and stateList4 == 0:
            robot.stateList2 = "empty"
            robot2.stateList2 = robot.stateList2
        if robot.stateList2 == "half_full" and stateList4 >= 6:
            robot.stateList2 = "full"
            robot2.stateList2 = robot.stateList2

    def RCS_set_A6080(self, value):
        self.businessState = value

    def RCS_set_A6085(self, value):
        self.businessState1 = value


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
    basedir = os.path.abspath(os.path.dirname(__file__))
    log_path = os.path.join(basedir, 'rcsLogs' )  # 日志根目录 ../logs/
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    log_filename = time.strftime("%F") + '.log'
    log_name = os.path.join(log_path,log_filename)
    return Logger(log_name,level='debug')

# def main():
#     shared = RobotData()
#     robot = RCSServer(shared,host='0.0.0.0', port=23311)
#     robot.start()
#     robot2 = RCSServer(shared,host='0.0.0.0', port=23310)
#     robot2.start()
#     a = 0
#     num_layers = 0
#     while True:
#         if a == 0:
#             project = robot.business_queue.get()
#             robot2.act_id = robot.act_id
#             robot2.act_name = robot.act_name
#             robot.act_id = robot.act_id
#             robot.act_name = robot.act_name
#             robot2.act_parameter = robot.act_parameter
#             print(11111111111111111111111111111111111111111111)
#             num_layers2 = project['act_parameter']['count']
#             stateList3 = project['act_parameter']['startAddress'][0]['count']
#             stateList4 = project['act_parameter']['endAddress'][0]['count']
#             if(project["act_name"] == "taskStart"):
#                 if num_layers2 > 6 :
#                     num_layers = 6
#                 else:
#                     num_layers = num_layers2
#                 robot.cc = 0
#                 robot2.cc = robot.cc
#                 robot.progress = str(0) + "/" + str(num_layers2)
#                 robot2.progress = robot.progress
#                 robot.act_status = 2
#                 robot.arm_status = 1
#                 robot2.act_status = robot.act_status
#                 robot2.arm_status = robot.arm_status
#                 robot2.stateList1 = robot.stateList1
#                 robot2.stateList2 = robot.stateList2
#                 for i in range(0, num_layers):
#                     time.sleep(10)
#                     robot.progress = str(i + 1) + "/" + str(num_layers2)
#                     robot.RCS(stateList3,stateList4,robot,robot2)
#
#                 robot.act_status = 4
#                 robot2.act_status = robot.act_status
#                 robot.arm_status = 0
#                 robot2.arm_status = robot.arm_status
#                 robot.CurrentStatus = "Idle"
#                 robot2.CurrentStatus = robot.CurrentStatus
#         a = 0
#
#
# if __name__ == "__main__":
#     try:
#         main()
#     except Exception as e:
#         print("Main Error:" + str(e.args))