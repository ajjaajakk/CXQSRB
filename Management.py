import socket
import threading
import config
import time
import traceback
import json
import math
import queue
from datetime import datetime
import numpy as np

class ManagementConnect(threading.Thread):
    def __init__(self, st_host, n_port):
        threading.Thread.__init__(self, name="ManagementConnect")
        self.lock = threading.Lock()
        self.st_host = st_host
        self.n_port = n_port
        self.response_queue = queue.Queue()
        self.pending_task = None
        self.reconnect_event = threading.Event()
        self.sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sck.bind(('127.0.0.1', 3001))
        self.sck.listen(5)
        self.connection, self.address = self.sck.accept()
        self.connection.settimeout(60)
        self.sendthread = threading.Thread(target=self.Sender, name='ManagementSender', daemon=True)
        self.state = threading.Condition()
        self.sendPaused = True
        self._task_seq = 0
        self.squeue = queue.Queue()

    def _get_task_num(self, task_type):
        self._task_seq += 1
        if self._task_seq >= 1000000:
            self._task_seq = 0
        now = datetime.now()
        return f"{task_type}{now.strftime('%Y%m%d')}{self._task_seq:06d}"

    def _get_send_time(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _send_json(self, obj):
        msg = json.dumps(obj, ensure_ascii=False) + '\n'
        config.log.logger.info(f"视觉下发: {msg.strip()}")
        self.squeue.put(msg.encode('utf-8'))

    def _wait_response(self, expected_type, timeout=30):
        self.response_queue.queue.clear()
        deadline = time.time() + timeout
        ack_received = False
        while time.time() < deadline:
            try:
                resp = self.response_queue.get(timeout=max(0.1, deadline - time.time()))
                resp_type = resp.get('type', '')
                if resp_type.endswith('Feedback'):
                    base_type = resp_type.replace('Feedback', '')
                    if base_type == expected_type:
                        return resp
                    else:
                        self.response_queue.put(resp)
                elif resp.get('result') is True:
                    ack_received = True
                    config.log.logger.info(f"视觉提交ACK成功")
            except queue.Empty:
                if ack_received:
                    continue
                else:
                    config.log.logger.info(f"等待视觉ACK... ({int(time.time()-deadline+timeout)}s)")
        config.log.logger.error(f"视觉响应超时 (expected: {expected_type}, timeout: {timeout}s)")
        return None

    def run(self):
        self.sendthread.start()
        while True:
            try:
                self.connection.settimeout(300)
                data = self.connection.recv(4096)
                if data:
                    try:
                        text = data.decode('utf-8').strip()
                        for line in text.split('\n'):
                            line = line.strip()
                            if line:
                                try:
                                    resp = json.loads(line)
                                    resp_type = resp.get('type', '')
                                    if resp_type.endswith('Feedback'):
                                        self.response_queue.put(resp)
                                    elif resp_type == 'StatusReport':
                                        code = resp.get('data', {}).get('code', 0)
                                        if code > 0:
                                            config.camera_offline = True
                                            config.log.logger.error(f"相机掉线告警! 视觉上报StatusReport异常码: {code}")
                                            config.log.logger.error(f"resp_type{resp}")
                                        else:
                                            if config.camera_offline:
                                                config.log.logger.info("相机恢复正常")
                                            config.log.logger.error(f"相机正常 视觉上报StatusReport: {code}")
                                            config.camera_offline = False
                                except json.JSONDecodeError:
                                    pass
                    except UnicodeDecodeError:
                        pass
            except OSError:
                traceback.print_exc()
                self.threadPause()
                self.connection.close()
                time.sleep(1)
                try:
                    self.connection, self.address = self.sck.accept()
                    self.connection.settimeout(60)
                except:
                    pass
            except Exception as e:
                config.log.logger.error(f'视觉连接异常: {str(e)}')
                self.threadPause()
                self.connection.close()
                time.sleep(1)
                try:
                    self.connection, self.address = self.sck.accept()
                    self.connection.settimeout(60)
                except:
                    pass

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
        now = datetime.now()
        msg = {
            "eid": "VISUAL",
            "dev": "DC1",
            "type": "heartbeat",
            "sendTime": now.strftime("%Y-%m-%d %H:%M:%S")
        }
        self._send_json(msg)

    def Visual_box_postion(self): # 获取箱体角点
        task_type = "boxLocate"
        task_num = self._get_task_num(task_type)
        msg = {
            "eid": "VISUAL",
            "dev": "DC1",
            "type": task_type,
            "taskNum": task_num,
            "task": {},
            "sendTime": self._get_send_time()
        }
        self._send_json(msg)
        resp = self._wait_response(task_type, timeout=60)
        if resp is None:
            return False
        data = resp.get('data', {})
        config.box = []
        if data.get('result') != 'pass':
            config.log.logger.warning("箱体定位失败")
            config.box.extend([{'x': 0, 'y': 0, 'z': 0}, {'x': 0, 'y': 0, 'z': 0}, {'x': 0, 'y': 0, 'z': 0}, {'x': 0, 'y': 0, 'z': 0}])
            return True
        point = data.get('point', [])
        if len(point) < 4:
            config.log.logger.warning("箱体角点不足4个")
            return False
        
        for p in point:
            # 旧版协议转换：[x,y,z,px,py] -> {'x': x, 'y': y, 'z': -z}
            # 新版协议需交换xy坐标：[x,y,z,px,py] -> {'x': y, 'y': x, 'z': -z}
            # 同时按物理位置排序：左上(-x,+y)→右上(+x,+y)→右下(+x,-y)→左下(-x,-y)
            config.box.append({'x': -p[1], 'y': -p[0], 'z': -p[2]})
        
        # 按左上、右上、右下、左下顺序排列（与旧版一致）
        # 左上: x<0, y>0 | 右上: x>0, y>0 | 右下: x>0, y<0 | 左下: x<0, y<0
        def corner_order(bp):
            if bp['x'] < 0 and bp['y'] < 0: return 0  # 左上
            if bp['x'] > 0 and bp['y'] < 0: return 1  # 右上
            if bp['x'] > 0 and bp['y'] > 0: return 2  # 右下
            if bp['x'] < 0 and bp['y'] > 0: return 3  # 左下
            return 4  # 兜底
        config.box.sort(key=corner_order)
        
        config.log.logger.info(f"箱体角点: {config.box}")
        return True

    def Visual_spindle_pos(self): # 获取中缝点
        task_type = "boxCenterSeamLocate"
        task_num = self._get_task_num(task_type)
        msg = {
            "eid": "VISUAL",
            "dev": "DC1",
            "type": task_type,
            "taskNum": task_num,
            "task": {},
            "sendTime": self._get_send_time()
        }
        self._send_json(msg)
        resp = self._wait_response(task_type, timeout=60)
        if resp is None:
            return False
        data = resp.get('data', {})
        if data.get('result') != 'pass':
            config.log.logger.warning("中缝定位失败")
            return False
        point = data.get('point', [])
        if len(point) < 2:
            config.log.logger.warning("中缝点不足2个")
            return False
        config.line_box = []
        for p in point:
            config.line_box.append({'x': -p[1], 'y': -p[0], 'z': -p[2]})
        config.log.logger.info(f"中缝点: {config.line_box}")
        return True

    def Visual_spindle_pos2(self, link): # 获取切缝点
        dir_val = link.get('dir', 0)
        if dir_val == 0:
            task_type = "boxLeftCutSeam"
            task_data = {"boxLR": 0}
        else:
            task_type = "boxRightCutSeam"
            task_data = {"boxLR": 1}
        task_num = self._get_task_num(task_type)
        msg = {
            "eid": "VISUAL",
            "dev": "DC1",
            "type": task_type,
            "taskNum": task_num,
            "task": task_data,
            "sendTime": self._get_send_time()
        }
        self._send_json(msg)
        config.line_box = []
        resp = self._wait_response(task_type, timeout=60)
        if resp is None:
            return False
        data = resp.get('data', {})
        if data.get('result') != 'pass':
            config.log.logger.warning("切缝识别失败")
            return False
        point = data.get('point', [])
        for p in point:
            x, y, z, angle = -p[1], -p[0], -p[2] , p[5]
            config.line_box.append({'x': x, 'y': y, 'z': z, 'angle': angle, 'code': dir_val})
        config.log.logger.info(f"切缝点数量: {len(config.line_box)}")
        config.log.logger.info(f"切缝点: {config.line_box}")
        return True

    def getAllSpindlePostion(self): # 获取全局纱锭
        task_type = "globalYarnSpindle"
        diameter = int(getattr(config, 'spindle_od', 200))
        inner_d = int(getattr(config, 'spindle_id', 80))
        spindles_cnt = int(getattr(config, 'spindlesCnt', 6))
        task_num = self._get_task_num(task_type)
        msg = {
            "eid": "VISUAL",
            "dev": "DC1",
            "type": task_type,
            "taskNum": task_num,
            "task": {
                "diameter": diameter,
                "innerD": inner_d,
                "spindlesCnt": spindles_cnt
            },
            "sendTime": self._get_send_time()
        }
        self._send_json(msg)
        resp = self._wait_response(task_type, timeout=60)
        if resp is None:
            return False
        data = resp.get('data', {})
        if data.get('result') != 'pass':
            config.log.logger.warning("全局纱锭识别失败")
            return False
        point_info = data.get('point', {})
        points = point_info.get('points', [])
        config.circles = []
        for p in points:
            config.circles.append({'x': -p[1], 'y': -p[0], 'z': -860, 'angle': 0})
        config.log.logger.info(f"全局纱锭数量: {len(config.circles)}")
        config.log.logger.info(f"全局纱锭: {config.circles}")
        return True

    def getSingleSpindlePostion(self): # 获取单个纱锭
        task_type = "singleYarnSpindle"
        diameter = int(getattr(config, 'spindle_od', 200))
        inner_d = int(getattr(config, 'spindle_id', 80))
        task_num = self._get_task_num(task_type)
        msg = {
            "eid": "VISUAL",
            "dev": "DC1",
            "type": task_type,
            "taskNum": task_num,
            "task": {
                "diameter": diameter,
                "innerD": inner_d
            },
            "sendTime": self._get_send_time()
        }
        self._send_json(msg)
        resp = self._wait_response(task_type, timeout=60)
        if resp is None:
            return False
        data = resp.get('data', {})
        if data.get('result') != 'pass':
            config.log.logger.warning("单个纱锭识别失败")
            return False
        point = data.get('point', [])
        if len(point) >= 3:
            config.circle = {'x': -point[1], 'y': -point[0], 'z': -500}
        else:
            config.circle = {'x': 0, 'y': 0, 'z': 0}
            input("请手动输入单个纱锭坐标")
            config.log.logger.warning("单个纱锭识别失败")
        config.log.logger.info(f"单个纱锭: {config.circle}")
        return True

    def getBarcodePostion(self, link): # 获取二维码
        task_type = "qrCode"
        qr_id = link.get('ID', 1)
        task_num = self._get_task_num(task_type)
        msg = {
            "eid": "VISUAL",
            "dev": "DC1",
            "type": task_type,
            "taskNum": task_num,
            "task": {
                "qrID": qr_id
            },
            "sendTime": self._get_send_time()
        }
        self._send_json(msg)
        resp = self._wait_response(task_type, timeout=60)
        if resp is None:
            return False
        data = resp.get('data', {})
        if data.get('result') != 'pass':
            config.log.logger.warning("二维码识别失败")
            return False
        point = data.get('point', [])
        if len(point) >= 6:
            qr_id_resp, x, y, z, px, py = point[0], point[1], point[2], point[3], point[4], point[5]
            config.POS_barcode = {'x': -y, 'y': -x, 'z': -z, 'u': px, 'v': py, 'w': 0}
        else:
            config.POS_barcode = {'x': 0, 'y': 0, 'z': 0, 'u': 640, 'v': 360, 'w': 0}
        config.log.logger.info(f"二维码: {config.POS_barcode}")
        return True

    def getBoxLeafPostion(self, link): # 获取翻页点
        task_type = "boxFlipPage"
        box_length = int(link.get('length', 620))
        box_width = int(link.get('width', 400))
        flip_direction = int(link.get('type1', 1))
        sort_rule = int(link.get('rule', 0))
        task_num = self._get_task_num(task_type)
        msg = {
            "eid": "VISUAL",
            "dev": "DC1",
            "type": task_type,
            "taskNum": task_num,
            "task": {
                "boxLength": box_length,
                "boxWidth": box_width,
                "flipDirection": flip_direction,
                "sortRule": sort_rule
            },
            "sendTime": self._get_send_time()
        }
        self._send_json(msg)
        resp = self._wait_response(task_type, timeout=60)
        if resp is None:
            return False
        data = resp.get('data', {})
        if data.get('result') != 'pass':
            config.log.logger.warning("翻页识别失败")
            return False
        point_info = data.get('point', {})
        # sheets = point_info.get('sheetsInPlace', {})
        # sheetsInPlace在data层级，不在point内
        sheets = data.get('sheetsInPlace', point_info.get('sheetsInPlace', {}))
        config.notice1 = sheets.get('top', 0)
        config.notice2 = sheets.get('bottom', 0)
        config.notice3 = sheets.get('left', 0)
        config.notice4 = sheets.get('right', 0)
        config.point = []
        for direction in ['top', 'bottom', 'left', 'right']:
            pts = point_info.get(direction, [])
            pt_list = []
            for p in pts[:3]:
                pt_list.append(np.array([-p[1], -p[0], -p[2]]))
            while len(pt_list) < 3:
                pt_list.append(np.array([0, 0, 0]))
                # input(f"请手动输入{direction}翻页点")
            config.point.append(pt_list)
        config.log.logger.info(f"翻页识别结果: notice1={config.notice1}, notice2={config.notice2}, notice3={config.notice3}, notice4={config.notice4}, point={config.point}")
        config.log.logger.info(f"翻页点: {config.point}")
        return True

    def getGrabPostion(self, link): # 获取箱子抓取点
        task_type = "boxGraspPoint"
        carton_dir = link.get('carton_dir', 0)
        box_lr = 1 if carton_dir == 0 else 0
        task_num = self._get_task_num(task_type)
        msg = {
            "eid": "VISUAL",
            "dev": "DC1",
            "type": task_type,
            "taskNum": task_num,
            "task": {"boxLR": box_lr},
            "sendTime": self._get_send_time()
        }
        self._send_json(msg)
        resp = self._wait_response(task_type, timeout=60)
        if resp is None:
            return False
        data = resp.get('data', {})
        if data.get('result') != 'pass':
            config.log.logger.warning("抓取点识别失败")
            return False
        point = data.get('point', [])
        if len(point) >= 5:
            config.grab = {'x': -point[1], 'y': -point[0], 'z': -point[2], 'w': point[5] if len(point) > 5 else 0}
        config.log.logger.info(f"抓取点: {config.grab}")
        return True

    def getPalletCenterPostion(self): # 获取托盘中心
        task_type = "pallet"
        task_num = self._get_task_num(task_type)
        msg = {
            "eid": "VISUAL",
            "dev": "DC1",
            "type": task_type,
            "taskNum": task_num,
            "task": {},
            "sendTime": self._get_send_time()
        }
        self._send_json(msg)
        resp = self._wait_response(task_type, timeout=60)
        if resp is None:
            return False
        data = resp.get('data', {})
        if data.get('result') != 'pass':
            config.log.logger.warning("托盘识别失败")
            return False
        point_info = data.get('point', {})
        #需要x，y为负数
        config.palletcenter = {
            'x': -point_info.get('y', 0),
            'y': -point_info.get('x', 0),
            'z': -point_info.get('z', 0),
            'w': -point_info.get('angle', 0)
        }
        config.log.logger.info(f"托盘中心: {config.palletcenter}")
        return True

    def getPutPostion(self, link): # 获取放置位置
        task_type = "yarnSpindlePlacement"
        diameter = int(getattr(config, 'spindle_od', 200))
        spindle_height = int(getattr(config, 'spindleHeight', 400))
        placement_lr = int(link.get('placementLR', 0))
        task_num = self._get_task_num(task_type)
        msg = {
            "eid": "VISUAL",
            "dev": "DC1",
            "type": task_type,
            "taskNum": task_num,
            "task": {
                "diameter": diameter,
                "spindleHeight": spindle_height,
                "placementLR": placement_lr
            },
            "sendTime": self._get_send_time()
        }
        self._send_json(msg)
        resp = self._wait_response(task_type, timeout=60)
        if resp is None:
            return False
        data = resp.get('data', {})
        if data.get('result') != 'pass':
            config.log.logger.warning("放置位置识别失败")
            return False
        point_info = data.get('point', {})
        points = point_info.get('points', [])
        config.temp_putPos = []
        for p in points:
            # config.temp_putPos.append([p[0], p[1], p[2]])
            config.temp_putPos.append([-p[1], -p[0], -p[2]])
        config.log.logger.info(f"放置位置识别结果[placementLR={placement_lr}]: 空位数={point_info.get('spindlesCnt',0)}, 坐标={config.temp_putPos}")
        return True

    def putVis(self): # 获取放置位置可视化
        task_type = "height"
        task_num = self._get_task_num(task_type)
        areaLength = int(getattr(config, 'areaLength'))
        areaWidth = int(getattr(config, 'areaWidth'))
        
        msg = {
            "eid": "VISUAL",
            "dev": "DC1",
            "type": task_type,
            "taskNum": task_num,
            "task": {
                "areaLength": areaLength,
                "areaWidth": areaWidth
            },
            "sendTime": self._get_send_time()
        }
        self._send_json(msg)
        resp = self._wait_response(task_type, timeout=60)
        if resp is None:
            return False
        data = resp.get('data', {})
        if data.get('result') != 'pass':
            config.log.logger.warning("高度识别失败")
            return False
        point_info = data.get('point', {})
        height_val = point_info.get('height', 0)
        config.hight = height_val
        config.log.logger.info(f"高度识别: {height_val}")
        # input("高度识别完成")
        return True

    def revolve(self, euler, vector):
        vector2 = vector.T
        u = euler['u'] / 180 * math.pi
        v = euler['v'] / 180 * math.pi
        w = euler['w'] / 180 * math.pi
        a = np.array([[1, 0, 0], [0, math.cos(u), -math.sin(u)], [0, math.sin(u), math.cos(u)]])
        b = np.array([[math.cos(v), 0, math.sin(v)], [0, 1, 0], [-math.sin(v), 0, math.cos(v)]])
        c = np.array([[math.cos(w), -math.sin(w), 0], [math.sin(w), math.cos(w), 0], [0, 0, 1]])
        d = np.dot(c, b)
        d = np.dot(d, a)
        e = d @ vector2
        return e.T
