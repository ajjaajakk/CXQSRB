

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

    def links_action195(self,poss):#识别2，3页翻箱点位置
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
        # self.links.append({'State':True, 'typeID': 16,'length': length, 'width': width,'type1': type1,'rule':rule})
        
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

    # # 从当前位置直线移动到目标位置
    # def Straight_line_Motion(self, targetPoint, speed):
    #     p = targetPoint
    #     poss1 = ""
    #     poss1 += "\"" + "," + "\"" + str(int(p['x']) * 1000)
    #     poss1 += "\"" + "," + "\"" + str(int(p['y']) * 1000)
    #     poss1 += "\"" + "," + "\"" + str(int(p['z']) * 1000)
    #     poss1 += "\"" + "," + "\"" + str(int(p['u']) * 1000)
    #     poss1 += "\"" + "," + "\"" + str(int(p['v']) * 1000)
    #     poss1 += "\"" + "," + "\"" + str(int(p['w']) * 1000)
    #     self.links = []
    #     self.links.append({'State': True, 'typeID': 3, 'speed': config.speed})
    #     # self.links.append({'State': True, 'typeID': 6, 'speed': min(int(speed * 10), 1000)})
    #     self.links.append({'State':True, 'typeID': 7,'number': 0, 'value': 0})
    #     self.links.append({'State':True, 'typeID': 0,'minID': 0, 'maxID': 0})
    #     self.links.append({'State': True, 'typeID': 8, 'addr': 800, 'poslen': 6, 'pos': poss1})
    #     self.links.append({'State': True, 'typeID': 1, 'borad': 4, 'point': 0, 'funtion': 1})
    #     self.links.append({'State': True, 'typeID': 0, 'minID': 2, 'maxID': 2})
    #     self.links.append({'State': True, 'typeID': 9})
    #     config.links = self.links
    #     # self.links.append({'State':True, 'typeID': 3,'speed':  config.speed})
    #     # self.links.append({'State':True, 'typeID': 7,'number': 0, 'value': 0})
    #     # self.links.append({'State':True, 'typeID': 0,'minID': 0, 'maxID': 0})
    #     # self.links.append({'State':True, 'typeID': 8, 'addr': 806 ,'poslen':line*6,'pos':poss1})
    #     # self.links.append({'State':True, 'typeID': 1,'borad': 4, 'point': 2,'funtion':1})
    #     # self.links.append({'State':True, 'typeID': 0,'minID': 6, 'maxID': 6})

    # # 门字型移动（6点轨迹）
    # def senCoordinates(self, targetPoint, HEIGHT, speed):
    #     import math
    #     import copy
    #     # 简化的门字型路径：当前位置 → 抬升到HEIGHT → 水平移动到目标上方 → 下降到目标
    #     startPos = config.currentPos
    #     poss = []
    #     # 点1: 当前位置
    #     poss.append(startPos)
    #     # 点2: 抬升到HEIGHT
    #     point = {'x': startPos['x'], 'y': startPos['y'], 'z': HEIGHT, 'u': startPos['u'], 'v': startPos['v'], 'w': startPos['w']}
    #     poss.append(point)
    #     # 点3-5: 水平移动到目标上方（3个中间点）
    #     for i in range(1, 4):
    #         point = {'x': startPos['x'] + (targetPoint['x'] - startPos['x']) / 4 * i,
    #                  'y': startPos['y'] + (targetPoint['y'] - startPos['y']) / 4 * i,
    #                  'z': HEIGHT,
    #                  'u': startPos['u'], 'v': startPos['v'],
    #                  'w': startPos['w'] + (targetPoint['w'] - startPos['w']) / 4 * i}
    #         poss.append(point)
    #     # 点6: 目标点
    #     poss.append(targetPoint)
        
    #     line = len(poss)
    #     poss1 = ""
    #     for p in poss:
    #         poss1 += "\"" + "," + "\"" + str(int(p['x']) * 1000)
    #         poss1 += "\"" + "," + "\"" + str(int(p['y']) * 1000)
    #         poss1 += "\"" + "," + "\"" + str(int(p['z']) * 1000)
    #         poss1 += "\"" + "," + "\"" + str(int(p['u']) * 1000)
    #         poss1 += "\"" + "," + "\"" + str(int(p['v']) * 1000)
    #         poss1 += "\"" + "," + "\"" + str(int(p['w']) * 1000)
    #     self.links = []
    #     self.links.append({'State': True, 'typeID': 3, 'speed': config.speed})
    #     self.links.append({'State': True, 'typeID': 6, 'speed': min(int(speed * 10), 1000)})
    #     self.links.append({'State': True, 'typeID': 8, 'addr': 848, 'poslen': line * 6, 'pos': poss1})
    #     self.links.append({'State': True, 'typeID': 1, 'borad': 4, 'point': 3, 'funtion': 1})
    #     self.links.append({'State': True, 'typeID': 0, 'minID': 8, 'maxID': 8})
    #     self.links.append({'State': True, 'typeID': 9})
    #     config.links = self.links

    # # 门字型移动（3点简化轨迹）
    # def senCoordinates11(self, targetPoint, HEIGHT, speed):
    #     import copy
    #     startPos = config.currentPos
    #     poss = []
    #     # 点1: 当前位置
    #     poss.append(startPos)
    #     # 点2: 抬升到HEIGHT并移动到目标水平位置
    #     point = {'x': targetPoint['x'], 'y': targetPoint['y'], 'z': HEIGHT,
    #              'u': startPos['u'], 'v': startPos['v'],
    #              'w': startPos['w'] + (targetPoint['w'] - startPos['w']) / 2}
    #     poss.append(point)
    #     # 点3: 目标点
    #     poss.append(targetPoint)
        
    #     line = len(poss)
    #     poss1 = ""
    #     for p in poss:
    #         poss1 += "\"" + "," + "\"" + str(int(p['x']) * 1000)
    #         poss1 += "\"" + "," + "\"" + str(int(p['y']) * 1000)
    #         poss1 += "\"" + "," + "\"" + str(int(p['z']) * 1000)
    #         poss1 += "\"" + "," + "\"" + str(int(p['u']) * 1000)
    #         poss1 += "\"" + "," + "\"" + str(int(p['v']) * 1000)
    #         poss1 += "\"" + "," + "\"" + str(int(p['w']) * 1000)
    #     self.links = []
    #     self.links.append({'State': True, 'typeID': 3, 'speed': config.speed})
    #     self.links.append({'State': True, 'typeID': 6, 'speed': min(int(speed * 10), 1000)})
    #     self.links.append({'State': True, 'typeID': 8, 'addr': 800, 'poslen': line * 6, 'pos': poss1})
    #     self.links.append({'State': True, 'typeID': 1, 'borad': 4, 'point': 10, 'funtion': 1})
    #     self.links.append({'State': True, 'typeID': 0, 'minID': 22, 'maxID': 22})
    #     self.links.append({'State': True, 'typeID': 9})
    #     config.links = self.links

    # # 使用逆解到达指定的点位
    # def rotate(self, EndPos, hight):
    #     import math
    #     import copy
    #     import numpy as np
    #     p = config.currentPos
    #     poss1 = ""
    #     poss1 += "\"" + "," + "\"" + str(int(p['x']) * 1000)
    #     poss1 += "\"" + "," + "\"" + str(int(p['y']) * 1000)
    #     poss1 += "\"" + "," + "\"" + str(int(hight) * 1000)
    #     poss1 += "\"" + "," + "\"" + str(int(p['u']) * 1000)
    #     poss1 += "\"" + "," + "\"" + str(int(p['v']) * 1000)
    #     poss1 += "\"" + "," + "\"" + str(int(p['w']) * 1000)

    #     # 逆解计算关节坐标
    #     euler_tar = {'u': EndPos['u'], 'v': EndPos['v'], 'w': EndPos['w']}
    #     vector_tar = np.array([EndPos['x'], EndPos['y'], EndPos['z']])

    #     # 逆解参数 (SCARA 6轴)
    #     a = np.array([400.389, -127.627, 616.5])
    #     b = np.array([0, 0, 1200.858])
    #     c = np.array([1647.775, 0, 251.261])
    #     d = np.array([277, 0, 0])
    #     d2 = np.array([0, 0, 277])

    #     # 旋转矩阵
    #     def revolve(euler, vector):
    #         vector2 = vector.T
    #         u = euler['u'] / 180 * math.pi
    #         v = euler['v'] / 180 * math.pi
    #         w = euler['w'] / 180 * math.pi
    #         a_mat = np.array([[1, 0, 0], [0, math.cos(u), -math.sin(u)], [0, math.sin(u), math.cos(u)]])
    #         b_mat = np.array([[math.cos(v), 0, math.sin(v)], [0, 1, 0], [-math.sin(v), 0, math.cos(v)]])
    #         c_mat = np.array([[math.cos(w), -math.sin(w), 0], [math.sin(w), math.cos(w), 0], [0, 0, 1]])
    #         d_mat = np.dot(np.dot(c_mat, b_mat), a_mat)
    #         return (d_mat @ vector2).T

    #     P2 = vector_tar - revolve(euler_tar, d2)
    #     P2_L = (P2[0] ** 2 + P2[1] ** 2) ** 0.5
    #     if P2_L < 0.001:
    #         return False
    #     P2_angle = math.atan2(P2[1], P2[0]) / math.pi * 180
    #     asin_arg = a[1] / P2_L
    #     if asin_arg > 1:
    #         asin_arg = 1
    #     elif asin_arg < -1:
    #         asin_arg = -1
    #     P2_der_angle = math.asin(asin_arg) / math.pi * 180
    #     J1 = P2_angle - P2_der_angle

    #     P1 = revolve({'u': 0, 'v': 0, 'w': J1}, a)
    #     P3 = P2 - P1
    #     h = P3[2]
    #     l1 = b[2]
    #     l2 = (c[0] ** 2 + c[2] ** 2) ** 0.5
    #     l3 = (P3[0] ** 2 + P3[1] ** 2 + P3[2] ** 2) ** 0.5

    #     if (l1 + l2 < l3) or (l1 + l3 < l2) or (l2 + l3 < l1):
    #         return False

    #     angle2 = math.acos((l1 ** 2 + l3 ** 2 - l2 ** 2) / (2 * l1 * l3)) / math.pi * 180
    #     angle3 = math.acos((l1 ** 2 + l2 ** 2 - l3 ** 2) / (2 * l1 * l2)) / math.pi * 180
    #     J2 = math.asin(h / l3) / math.pi * 180 + angle2 - 90
    #     J3 = angle3 - (90 + math.atan(c[2] / c[0]) / math.pi * 180)

    #     def rotation_matrix(euler):
    #         u = euler['u'] / 180 * math.pi
    #         v = euler['v'] / 180 * math.pi
    #         w = euler['w'] / 180 * math.pi
    #         a_mat = np.array([[1, 0, 0], [0, math.cos(u), -math.sin(u)], [0, math.sin(u), math.cos(u)]])
    #         b_mat = np.array([[math.cos(v), 0, math.sin(v)], [0, 1, 0], [-math.sin(v), 0, math.cos(v)]])
    #         c_mat = np.array([[math.cos(w), -math.sin(w), 0], [math.sin(w), math.cos(w), 0], [0, 0, 1]])
    #         return np.dot(np.dot(c_mat, b_mat), a_mat)

    #     T1 = rotation_matrix({'u': 0, 'v': 0, 'w': J1})
    #     T2 = rotation_matrix({'u': 0, 'v': -J2, 'w': 0})
    #     T3 = rotation_matrix({'u': 0, 'v': -J3, 'w': 0})
    #     T0 = rotation_matrix({'u': 0, 'v': 90, 'w': 0})
    #     T_tar = rotation_matrix(euler_tar)
    #     T123 = np.dot(np.dot(T1, T2), T3)
    #     T123I = (np.mat(T123)).I
    #     T0I = (np.mat(T0)).I
    #     T456 = np.array(T123I @ T_tar @ T0I)

    #     J51 = math.acos(T456[0, 0]) / math.pi * 180
    #     J52 = -math.acos(T456[0, 0]) / math.pi * 180
    #     S51 = math.sin(J51 / 180 * math.pi)
    #     S52 = math.sin(J52 / 180 * math.pi)

    #     JS = []
    #     if abs(T456[0, 0] - 1) > 0.0001:
    #         J41 = math.atan2(-T456[1, 0] / S51, T456[2, 0] / S51) / math.pi * 180
    #         J42 = math.atan2(-T456[1, 0] / S52, T456[2, 0] / S52) / math.pi * 180
    #         J61 = math.atan2(-T456[0, 1] / S51, -T456[0, 2] / S51) / math.pi * 180
    #         J62 = math.atan2(-T456[0, 1] / S52, -T456[0, 2] / S52) / math.pi * 180
    #         JS.append([J1, J2, J3, J41, J51, J61])
    #         JS.append([J1, J2, J3, J42, J52, J62])
    #     else:
    #         J41 = 0
    #         J42 = 180
    #         if T456[2, 1] == 0:
    #             J61 = J41
    #             J62 = J42
    #         else:
    #             J61 = math.atan2(T456[2, 1], T456[1, 1]) / math.pi * 180
    #             J62 = math.atan2(T456[2, 1], T456[1, 1]) / math.pi * 180
    #         JS.append([J1, J2, J3, J41, J51, J61])
    #         JS.append([J1, J2, J3, J42, J52, J62])

    #     # 选择逆解（J4绝对值小的）
    #     if len(JS) == 2:
    #         if abs(JS[0][3]) <= abs(JS[1][3]):
    #             J = JS[0]
    #         else:
    #             J = JS[1]
    #     else:
    #         J = JS[0]

    #     poss1 += "\"" + "," + "\"" + str(int(J[0] * 1000))
    #     poss1 += "\"" + "," + "\"" + str(int(J[1] * 1000))
    #     poss1 += "\"" + "," + "\"" + str(int(J[2] * 1000))
    #     poss1 += "\"" + "," + "\"" + str(int(J[3] * 1000))
    #     poss1 += "\"" + "," + "\"" + str(int(J[4] * 1000))
    #     poss1 += "\"" + "," + "\"" + str(int(J[5] * 1000))

    #     self.links = []
    #     self.links.append({'State': True, 'typeID': 3, 'speed': config.speed})
    #     self.links.append({'State': True, 'typeID': 8, 'addr': 884, 'poslen': 2 * 6, 'pos': poss1})
    #     self.links.append({'State': True, 'typeID': 1, 'borad': 4, 'point': 6, 'funtion': 1})
    #     self.links.append({'State': True, 'typeID': 0, 'minID': 14, 'maxID': 14})
    #     config.links = self.links


