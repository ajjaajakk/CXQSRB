

from copy import deepcopy
import config


#设置机械臂动作指令集
class SetLinks:
    def __init__(self):
        #码垛托盘起始点      
        config.log.logger.info("指令集类初始化")

    def linkstar(self):
        self.links = []         
        #self.links.append({'State':True, 'typeID': 16,'length': 300, 'width':200})
       # self.links.append({'State':True, 'typeID': 17,'length': 300, 'width': 200})
        #self.links.append({'State':True, 'typeID': 10})
        self.links.append({'State':True, 'typeID': 6}) 
        self.links.append({'State':True, 'typeID': 6}) 
        self.links.append({'State':True, 'typeID': 7,'number': 0, 'value': 0})
        self.links.append({'State':True, 'typeID': 0,'minID': 0, 'maxID': 0})
        self.links.append({'State':True, 'typeID': 3,'speed': config.speed})
        self.links.append({'State':True, 'typeID': 1,'borad': 4, 'point': 0,'funtion':0})
        self.links.append({'State':True, 'typeID': 1,'borad': 4, 'point': 1,'funtion':0})
        self.links.append({'State':True, 'typeID': 1,'borad': 4, 'point': 2,'funtion':0})
        self.links.append({'State':True, 'typeID': 1,'borad': 4, 'point': 3,'funtion':0})
        self.links.append({'State':True, 'typeID': 1,'borad': 4, 'point': 4,'funtion':0})
        self.links.append({'State':True, 'typeID': 1,'borad': 4, 'point': 5,'funtion':0})
        self.links.append({'State':True, 'typeID': 1,'borad': 4, 'point': 6,'funtion':0})
        self.links.append({'State':True, 'typeID': 1,'borad': 4, 'point': 7,'funtion':0})
        self.links.append({'State':True, 'typeID': 5})
        #self.links.append({'State':True, 'typeID': 11, 'dir': 0})
        #self.links.append({'State':True, 'typeID': 12})
        #self.links.append({'State':True, 'typeID': 13})
        #self.links.append({'State':True, 'typeID': 14})
        config.links = self.links

    def links_action1(self,poss):
        poss0 = poss
        line = len(poss0)
        poss1 = ""
        for p in poss0:
            poss1+= "\""+","+"\""+str(p['x'])
            poss1+= "\""+","+"\""+str(p['y'])
            poss1+= "\""+","+"\""+str(p['z']) 
            poss1+= "\""+","+"\""+str(p['u']) 
            poss1+= "\""+","+"\""+str(p['v'])
            poss1+= "\""+","+"\""+str(p['w']) 
        self.links = []        
        self.links.append({'State':True, 'typeID': 3,'speed':  config.speed})
        if config.currentPos['ID'] == 2:
            self.links.append({'State':True, 'typeID': 7,'number': 0, 'value': 0})
            self.links.append({'State':True, 'typeID': 0,'minID': 0, 'maxID': 0})
        self.links.append({'State':True, 'typeID': 8, 'addr': 800 ,'poslen':line*6,'pos':poss1})
        self.links.append({'State':True, 'typeID': 1,'borad': 4, 'point': 0,'funtion':1})
        self.links.append({'State':True, 'typeID': 0,'minID': 2, 'maxID': 2})
        self.links.append({'State':True, 'typeID': 9})
        
        config.links = self.links

    def links_action2(self,poss):
        poss0 = poss
        line = len(poss0)
        poss1 = ""
        for p in poss0:
            poss1+= "\""+","+"\""+str(p['x'])
            poss1+= "\""+","+"\""+str(p['y'])
            poss1+= "\""+","+"\""+str(p['z']) 
            poss1+= "\""+","+"\""+str(p['u']) 
            poss1+= "\""+","+"\""+str(p['v'])
            poss1+= "\""+","+"\""+str(p['w']) 
        self.links = []       
        self.links.append({'State':True, 'typeID': 3,'speed':  config.speed})
        if config.currentPos['ID'] == 4:
            self.links.append({'State':True, 'typeID': 7,'number': 0, 'value': 0})
            self.links.append({'State':True, 'typeID': 0,'minID': 0, 'maxID': 0})
        self.links.append({'State':True, 'typeID': 8, 'addr': 848 ,'poslen':line*6,'pos':poss1})
        self.links.append({'State':True, 'typeID': 1,'borad': 4, 'point': 1,'funtion':1})
        self.links.append({'State':True, 'typeID': 0,'minID': 4, 'maxID': 4})
         
        return self.links

    def links_action22(self,poss):
        poss0 = poss
        line = len(poss0)
        poss1 = ""
        for p in poss0:
            poss1+= "\""+","+"\""+str(p['x'])
            poss1+= "\""+","+"\""+str(p['y'])
            poss1+= "\""+","+"\""+str(p['z']) 
            poss1+= "\""+","+"\""+str(p['u']) 
            poss1+= "\""+","+"\""+str(p['v'])
            poss1+= "\""+","+"\""+str(p['w']) 
        self.links = []        
        self.links.append({'State':True, 'typeID': 3,'speed':  config.speed})
        if config.currentPos['ID'] == 22:
            self.links.append({'State':True, 'typeID': 7,'number': 0, 'value': 0})
            self.links.append({'State':True, 'typeID': 0,'minID': 0, 'maxID': 0})
        self.links.append({'State':True, 'typeID': 8, 'addr': 848 ,'poslen':line*6,'pos':poss1})
        self.links.append({'State':True, 'typeID': 1,'borad': 4, 'point': 8,'funtion':1})
        self.links.append({'State':True, 'typeID': 0,'minID': 22, 'maxID': 22})
         
        #config.links = self.links
        return self.links




    def links_action3(self,poss):
        poss0 = poss
        line = len(poss0)
        poss1 = ""
        for p in poss0:
            poss1+= "\""+","+"\""+str(p['x'])
            poss1+= "\""+","+"\""+str(p['y'])
            poss1+= "\""+","+"\""+str(p['z']) 
            poss1+= "\""+","+"\""+str(p['u']) 
            poss1+= "\""+","+"\""+str(p['v'])
            poss1+= "\""+","+"\""+str(p['w']) 
        self.links = []        
        self.links.append({'State':True, 'typeID': 3,'speed':  config.speed})
        self.links.append({'State':True, 'typeID': 7,'number': 0, 'value': 0})
        self.links.append({'State':True, 'typeID': 0,'minID': 0, 'maxID': 0})
        self.links.append({'State':True, 'typeID': 8, 'addr': 806 ,'poslen':line*6,'pos':poss1})
        self.links.append({'State':True, 'typeID': 1,'borad': 4, 'point': 2,'funtion':1})
        self.links.append({'State':True, 'typeID': 0,'minID': 6, 'maxID': 6})
        config.links = self.links

    def links_action4(self,poss):
        poss0 = poss
        line = len(poss0)
        poss1 = ""
        for p in poss0:
            poss1+= "\""+","+"\""+str(p['x'])
            poss1+= "\""+","+"\""+str(p['y'])
            poss1+= "\""+","+"\""+str(p['z']) 
            poss1+= "\""+","+"\""+str(p['u']) 
            poss1+= "\""+","+"\""+str(p['v'])
            poss1+= "\""+","+"\""+str(p['w']) 
        self.links = []        
        self.links.append({'State':True, 'typeID': 3,'speed':  config.speed})
        self.links.append({'State':True, 'typeID': 7,'number': 0, 'value': 0})
        self.links.append({'State':True, 'typeID': 0,'minID': 0, 'maxID': 0})
        self.links.append({'State':True, 'typeID': 0,'minID': 0, 'maxID': 0})
        self.links.append({'State':True, 'typeID': 8, 'addr': 806 ,'poslen':line*6,'pos':poss1})
        self.links.append({'State':True, 'typeID': 1,'borad': 4, 'point': 3,'funtion':1})
        self.links.append({'State':True, 'typeID': 0,'minID': 8, 'maxID': 8})
         
        return self.links


    def links_action5(self,poss):
        poss0 = poss
        line = len(poss0)
        poss1 = ""
        for p in poss0:
            poss1+= "\""+","+"\""+str(p['x'])
            poss1+= "\""+","+"\""+str(p['y'])
            poss1+= "\""+","+"\""+str(p['z']) 
            poss1+= "\""+","+"\""+str(p['u']) 
            poss1+= "\""+","+"\""+str(p['v'])
            poss1+= "\""+","+"\""+str(p['w']) 
        self.links = []        
        
        self.links.append({'State':True, 'typeID': 3,'speed':  config.speed})
        self.links.append({'State':True, 'typeID': 7,'number': 0, 'value': 0})
        self.links.append({'State':True, 'typeID': 0,'minID': 0, 'maxID': 0})
        self.links.append({'State':True, 'typeID': 8, 'addr': 806 ,'poslen':line*6,'pos':poss1})
        self.links.append({'State':True, 'typeID': 1,'borad': 4, 'point': 4,'funtion':1})
        self.links.append({'State':True, 'typeID': 0,'minID': 10, 'maxID': 10})

         
        return self.links   

    def links_action6(self,poss,dir):
        poss0 = poss
        line = len(poss0)
        poss1 = ""
        for p in poss0:
            poss1+= "\""+","+"\""+str(p['x'])
            poss1+= "\""+","+"\""+str(p['y'])
            poss1+= "\""+","+"\""+str(p['z']) 
            poss1+= "\""+","+"\""+str(p['u']) 
            poss1+= "\""+","+"\""+str(p['v'])
            poss1+= "\""+","+"\""+str(p['w']) 
        self.links = []        
        self.links.append({'State':True, 'typeID': 3,'speed':  config.speed})
        self.links.append({'State':True, 'typeID': 7,'number': 0, 'value': 0})
        self.links.append({'State':True, 'typeID': 0,'minID': 0, 'maxID': 0})
        self.links.append({'State':True, 'typeID': 8, 'addr': 806 ,'poslen':line*6,'pos':poss1})
        self.links.append({'State':True, 'typeID': 1,'borad': 4, 'point': 1,'funtion':1})
        self.links.append({'State':True, 'typeID': 0,'minID': 4, 'maxID': 4})
        #self.links.append({'State':True, 'typeID': 0,'minID': 4, 'maxID': 4})
        self.links.append({'State':True, 'typeID': 11, 'dir': dir}) 
        config.links = self.links

    def links_action7(self,poss):
        self.links = []
        self.links.append({'State':True, 'typeID': 11}) 
        config.links = self.links

    def links_action8(self,poss):
        poss0 = poss
        line = len(poss0)
        poss1 = ""
        for p in poss0:
            poss1+= "\""+","+"\""+str(p['x'])
            poss1+= "\""+","+"\""+str(p['y'])
            poss1+= "\""+","+"\""+str(p['z']) 
            poss1+= "\""+","+"\""+str(p['u']) 
            poss1+= "\""+","+"\""+str(p['v'])
            poss1+= "\""+","+"\""+str(p['w']) 
        self.links = []        
        
        self.links.append({'State':True, 'typeID': 3,'speed':  config.speed})
        self.links.append({'State':True, 'typeID': 8, 'addr': 800 ,'poslen':line*6,'pos':poss1})
        self.links.append({'State':True, 'typeID': 7,'number': 0, 'value': 0})
        self.links.append({'State':True, 'typeID': 0,'minID': 0, 'maxID': 0})
        self.links.append({'State':True, 'typeID': 1,'borad': 4, 'point': 5,'funtion':1})
        self.links.append({'State':True, 'typeID': 0,'minID': 12, 'maxID': 12})
         
        return self.links   

    def links_ction8(self,poss):
        poss0 = poss
        line = len(poss0)
        poss1 = ""
        for p in poss0:
            poss1+= "\""+","+"\""+str(p['x'])
            poss1+= "\""+","+"\""+str(p['y'])
            poss1+= "\""+","+"\""+str(p['z']) 
            poss1+= "\""+","+"\""+str(p['u']) 
            poss1+= "\""+","+"\""+str(p['v'])
            poss1+= "\""+","+"\""+str(p['w']) 
        self.links = []        
        
        self.links.append({'State':True, 'typeID': 3,'speed':  config.speed})
        self.links.append({'State':True, 'typeID': 8, 'addr': 800 ,'poslen':line*6,'pos':poss1})
        self.links.append({'State':True, 'typeID': 7,'number': 0, 'value': 0})
        self.links.append({'State':True, 'typeID': 0,'minID': 0, 'maxID': 0})
        self.links.append({'State':True, 'typeID': 1,'borad': 4, 'point': 5,'funtion':1})
        self.links.append({'State':True, 'typeID': 0,'minID': 12, 'maxID': 12})
         
        config.links = self.links   

    def links_action9(self,poss):
        poss0 = poss
        line = len(poss0)
        poss1 = ""
        for p in poss0:
            poss1+= "\""+","+"\""+str(p['x'])
            poss1+= "\""+","+"\""+str(p['y'])
            poss1+= "\""+","+"\""+str(p['z']) 
            poss1+= "\""+","+"\""+str(p['u']) 
            poss1+= "\""+","+"\""+str(p['v'])
            poss1+= "\""+","+"\""+str(p['w']) 
        self.links = []        
        
        self.links.append({'State':True, 'typeID': 3,'speed':  config.speed})
        self.links.append({'State':True, 'typeID': 8, 'addr': 800 ,'poslen':line*6,'pos':poss1})
        self.links.append({'State':True, 'typeID': 7,'number': 0, 'value': 0})
        self.links.append({'State':True, 'typeID': 0,'minID': 0, 'maxID': 0})
        self.links.append({'State':True, 'typeID': 1,'borad': 4, 'point': 6,'funtion':1})
        self.links.append({'State':True, 'typeID': 0,'minID': 14, 'maxID': 14})
         
        config.links = self.links   


    def links_action10(self,poss):
        poss0 = poss
        line = len(poss0)
        poss1 = ""
        for p in poss0:
            poss1+= "\""+","+"\""+str(p['x'])
            poss1+= "\""+","+"\""+str(p['y'])
            poss1+= "\""+","+"\""+str(p['z']) 
            poss1+= "\""+","+"\""+str(p['u']) 
            poss1+= "\""+","+"\""+str(p['v'])
            poss1+= "\""+","+"\""+str(p['w']) 
        self.links = []        
        self.links.append({'State':True, 'typeID': 3,'speed':  config.speed})
        self.links.append({'State':True, 'typeID': 7,'number': 0, 'value': 0})
        self.links.append({'State':True, 'typeID': 0,'minID': 0, 'maxID': 0})
        self.links.append({'State':True, 'typeID': 8, 'addr': 800 ,'poslen':line*6,'pos':poss1})
        self.links.append({'State':True, 'typeID': 1,'borad': 4, 'point': 0,'funtion':1})
        self.links.append({'State':True, 'typeID': 0,'minID': 2, 'maxID': 2})
        #self.links.append({'State':True, 'typeID': 12})
        
        config.links = self.links

    def links_action11(self,poss):
        poss0 = poss
        line = len(poss0)
        poss1 = ""
        for p in poss0:
            poss1+= "\""+","+"\""+str(p['x'])
            poss1+= "\""+","+"\""+str(p['y'])
            poss1+= "\""+","+"\""+str(p['z']) 
            poss1+= "\""+","+"\""+str(p['u']) 
            poss1+= "\""+","+"\""+str(p['v'])
            poss1+= "\""+","+"\""+str(p['w']) 
        self.links = []        
        self.links.append({'State':True, 'typeID': 3,'speed':  config.speed})
        self.links.append({'State':True, 'typeID': 7,'number': 0, 'value': 0})
        self.links.append({'State':True, 'typeID': 0,'minID': 0, 'maxID': 0})
        self.links.append({'State':True, 'typeID': 8, 'addr': 800 ,'poslen':line*6,'pos':poss1})
        self.links.append({'State':True, 'typeID': 1,'borad': 4, 'point': 0,'funtion':1})
        self.links.append({'State':True, 'typeID': 0,'minID': 2, 'maxID': 2})
        self.links.append({'State':True, 'typeID': 13})
        
        config.links = self.links

    def links_action12(self,poss):
        poss0 = poss
        line = len(poss0)
        poss1 = ""
        for p in poss0:
            poss1+= "\""+","+"\""+str(p['x'])
            poss1+= "\""+","+"\""+str(p['y'])
            poss1+= "\""+","+"\""+str(p['z']) 
            poss1+= "\""+","+"\""+str(p['u']) 
            poss1+= "\""+","+"\""+str(p['v'])
            poss1+= "\""+","+"\""+str(p['w']) 
        self.links = []        
        self.links.append({'State':True, 'typeID': 3,'speed':  config.speed})
        self.links.append({'State':True, 'typeID': 7,'number': 0, 'value': 0})
        self.links.append({'State':True, 'typeID': 0,'minID': 0, 'maxID': 0})
        self.links.append({'State':True, 'typeID': 8, 'addr': 800 ,'poslen':line*6,'pos':poss1})

        self.links.append({'State':True, 'typeID': 1,'borad': 4, 'point': 0,'funtion':1})
        self.links.append({'State':True, 'typeID': 0,'minID': 2, 'maxID': 2})
        self.links.append({'State':True, 'typeID': 14})
        
        config.links = self.links

    def links_action13(self,poss):
        poss0 = poss
        line = len(poss0)
        poss1 = ""
        for p in poss0:
            poss1+= "\""+","+"\""+str(p['x'])
            poss1+= "\""+","+"\""+str(p['y'])
            poss1+= "\""+","+"\""+str(p['z']) 
            poss1+= "\""+","+"\""+str(p['u']) 
            poss1+= "\""+","+"\""+str(p['v'])
            poss1+= "\""+","+"\""+str(p['w']) 
        self.links = []       
        self.links.append({'State':True, 'typeID': 3,'speed':  config.speed})
        self.links.append({'State':True, 'typeID': 7,'number': 0, 'value': 0})
        self.links.append({'State':True, 'typeID': 0,'minID': 0, 'maxID': 0})
        self.links.append({'State':True, 'typeID': 8, 'addr': 800 ,'poslen':line*6,'pos':poss1})
        self.links.append({'State':True, 'typeID': 1,'borad': 4, 'point': 6,'funtion':1})
        self.links.append({'State':True, 'typeID': 0,'minID': 14, 'maxID': 14})
        
        config.links = self.links

    def links_action14(self,poss):
        poss0 = poss
        line = len(poss0)
        poss1 = ""
        for p in poss0:
            poss1+= "\""+","+"\""+str(p['x'])
            poss1+= "\""+","+"\""+str(p['y'])
            poss1+= "\""+","+"\""+str(p['z']) 
            poss1+= "\""+","+"\""+str(p['u']) 
            poss1+= "\""+","+"\""+str(p['v'])
            poss1+= "\""+","+"\""+str(p['w']) 
        self.links = []        
        self.links.append({'State':True, 'typeID': 3,'speed':  config.speed})
        self.links.append({'State':True, 'typeID': 7,'number': 0, 'value': 0})
        self.links.append({'State':True, 'typeID': 0,'minID': 0, 'maxID': 0})
        self.links.append({'State':True, 'typeID': 8, 'addr': 800 ,'poslen':line*6,'pos':poss1})
        self.links.append({'State':True, 'typeID': 1,'borad': 4, 'point': 7,'funtion':1})
        self.links.append({'State':True, 'typeID': 0,'minID': 16, 'maxID': 16})
        
        config.links = self.links

    def links_action15(self,poss):#放置位置识别
        poss0 = poss
        line = len(poss0)
        poss1 = ""
        for p in poss0:
            poss1+= "\""+","+"\""+str(p['x'])
            poss1+= "\""+","+"\""+str(p['y'])
            poss1+= "\""+","+"\""+str(p['z']) 
            poss1+= "\""+","+"\""+str(p['u']) 
            poss1+= "\""+","+"\""+str(p['v'])
            poss1+= "\""+","+"\""+str(p['w']) 
        self.links = []        
        self.links.append({'State':True, 'typeID': 3,'speed':  config.speed})
        self.links.append({'State':True, 'typeID': 7,'number': 0, 'value': 0})
        self.links.append({'State':True, 'typeID': 0,'minID': 0, 'maxID': 0})
        self.links.append({'State':True, 'typeID': 8, 'addr': 806 ,'poslen':line*6,'pos':poss1})
        self.links.append({'State':True, 'typeID': 1,'borad': 4, 'point': 1,'funtion':1})
        self.links.append({'State':True, 'typeID': 0,'minID': 4, 'maxID': 4})
        self.links.append({'State':True, 'typeID': 0,'minID': 4, 'maxID': 4})
        self.links.append({'State':True, 'typeID': 15})
        
        config.links = self.links

    def links_action16(self,poss,length,width,type1,rule):#识别2，3页翻箱点位置
        poss0 = poss
        line = len(poss0)
        poss1 = ""
        for p in poss0:
            poss1+= "\""+","+"\""+str(p['x'])
            poss1+= "\""+","+"\""+str(p['y'])
            poss1+= "\""+","+"\""+str(p['z']) 
            poss1+= "\""+","+"\""+str(p['u']) 
            poss1+= "\""+","+"\""+str(p['v'])
            poss1+= "\""+","+"\""+str(p['w']) 
        self.links = []        
        self.links.append({'State':True, 'typeID': 3,'speed':  config.speed})
        self.links.append({'State':True, 'typeID': 7,'number': 0, 'value': 0})
        self.links.append({'State':True, 'typeID': 0,'minID': 0, 'maxID': 0})
        self.links.append({'State':True, 'typeID': 8, 'addr': 800 ,'poslen':line*6,'pos':poss1})
        self.links.append({'State':True, 'typeID': 1,'borad': 4, 'point': 0,'funtion':1})
        self.links.append({'State':True, 'typeID': 0,'minID': 2, 'maxID': 2})
        self.links.append({'State':True, 'typeID': 16,'length': length, 'width': width,'type1': type1,'rule':rule})
        
        config.links = self.links




    def links_action17(self,poss,length,width):#识别抓纸箱位置
        poss0 = poss
        line = len(poss0)
        poss1 = ""
        for p in poss0:
            poss1+= "\""+","+"\""+str(p['x'])
            poss1+= "\""+","+"\""+str(p['y'])
            poss1+= "\""+","+"\""+str(p['z']) 
            poss1+= "\""+","+"\""+str(p['u']) 
            poss1+= "\""+","+"\""+str(p['v'])
            poss1+= "\""+","+"\""+str(p['w']) 
        self.links = []        
        self.links.append({'State':True, 'typeID': 3,'speed':  config.speed})
        self.links.append({'State':True, 'typeID': 7,'number': 0, 'value': 0})
        self.links.append({'State':True, 'typeID': 0,'minID': 0, 'maxID': 0})
        self.links.append({'State':True, 'typeID': 8, 'addr': 800 ,'poslen':line*6,'pos':poss1})
        self.links.append({'State':True, 'typeID': 1,'borad': 4, 'point': 0,'funtion':1})
        self.links.append({'State':True, 'typeID': 0,'minID': 2, 'maxID': 2})
        self.links.append({'State':True, 'typeID': 17,'length': length, 'width': width})
        
        config.links = self.links


    def links_action18(self,poss,ID,length):#识别二维码
        poss0 = poss
        line = len(poss0)
        poss1 = ""
        for p in poss0:
            poss1+= "\""+","+"\""+str(p['x'])
            poss1+= "\""+","+"\""+str(p['y'])
            poss1+= "\""+","+"\""+str(p['z']) 
            poss1+= "\""+","+"\""+str(p['u']) 
            poss1+= "\""+","+"\""+str(p['v'])
            poss1+= "\""+","+"\""+str(p['w']) 
        self.links = []        
        self.links.append({'State':True, 'typeID': 3,'speed':  config.speed})
        self.links.append({'State':True, 'typeID': 7,'number': 0, 'value': 0})
        self.links.append({'State':True, 'typeID': 0,'minID': 0, 'maxID': 0})
        self.links.append({'State':True, 'typeID': 8, 'addr': 800 ,'poslen':line*6,'pos':poss1})
        self.links.append({'State':True, 'typeID': 1,'borad': 4, 'point': 0,'funtion':1})
        self.links.append({'State':True, 'typeID': 0,'minID': 2, 'maxID': 2})
        self.links.append({'State':True, 'typeID': 18,'ID': ID, 'length': length})
        
        config.links = self.links

    def links_action19(self,poss,ID,length):#托盘中心识别
        poss0 = poss
        line = len(poss0)
        poss1 = ""
        for p in poss0:
            poss1+= "\""+","+"\""+str(p['x'])
            poss1+= "\""+","+"\""+str(p['y'])
            poss1+= "\""+","+"\""+str(p['z']) 
            poss1+= "\""+","+"\""+str(p['u']) 
            poss1+= "\""+","+"\""+str(p['v'])
            poss1+= "\""+","+"\""+str(p['w']) 
        self.links = []        
        self.links.append({'State':True, 'typeID': 3,'speed':  config.speed})
        self.links.append({'State':True, 'typeID': 7,'number': 0, 'value': 0})
        self.links.append({'State':True, 'typeID': 0,'minID': 0, 'maxID': 0})
        self.links.append({'State':True, 'typeID': 8, 'addr': 800 ,'poslen':line*6,'pos':poss1})
        self.links.append({'State':True, 'typeID': 1,'borad': 4, 'point': 0,'funtion':1})
        self.links.append({'State':True, 'typeID': 0,'minID': 2, 'maxID': 2})
        self.links.append({'State':True, 'typeID': 19,'length': ID, 'width': length})
        
        config.links = self.links


    def links_action20(self,poss):
        poss0 = poss
        line = len(poss0)
        poss1 = ""
        for p in poss0:
            poss1+= "\""+","+"\""+str(p['x'])
            poss1+= "\""+","+"\""+str(p['y'])
            poss1+= "\""+","+"\""+str(p['z']) 
            poss1+= "\""+","+"\""+str(p['u']) 
            poss1+= "\""+","+"\""+str(p['v'])
            poss1+= "\""+","+"\""+str(p['w']) 
        self.links = []       
        self.links.append({'State':True, 'typeID': 3,'speed':  config.speed})
        self.links.append({'State':True, 'typeID': 7,'number': 0, 'value': 0})
        self.links.append({'State':True, 'typeID': 0,'minID': 0, 'maxID': 0})
        self.links.append({'State':True, 'typeID': 8, 'addr': 806 ,'poslen':line*6,'pos':poss1})
        self.links.append({'State':True, 'typeID': 1,'borad': 4, 'point': 1,'funtion':1})
        self.links.append({'State':True, 'typeID': 0,'minID': 4, 'maxID': 4})
        self.links.append({'State':True, 'typeID': 0,'minID': 4, 'maxID': 4})
        config.links = self.links

    def links_action21(self,poss):
        poss0 = poss
        line = len(poss0)
        poss1 = ""
        for p in poss0:
            poss1+= "\""+","+"\""+str(p['x'])
            poss1+= "\""+","+"\""+str(p['y'])
            poss1+= "\""+","+"\""+str(p['z']) 
            poss1+= "\""+","+"\""+str(p['u']) 
            poss1+= "\""+","+"\""+str(p['v'])
            poss1+= "\""+","+"\""+str(p['w']) 
        self.links = []        
        self.links.append({'State':True, 'typeID': 3,'speed':  config.speed})
        self.links.append({'State':True, 'typeID': 7,'number': 0, 'value': 0})
        self.links.append({'State':True, 'typeID': 0,'minID': 0, 'maxID': 0})
        self.links.append({'State':True, 'typeID': 8, 'addr': 806 ,'poslen':line*6,'pos':poss1})
        self.links.append({'State':True, 'typeID': 1,'borad': 4, 'point': 1,'funtion':1})
        self.links.append({'State':True, 'typeID': 0,'minID': 4, 'maxID': 4})
        self.links.append({'State':True, 'typeID': 10}) 
        config.links = self.links


