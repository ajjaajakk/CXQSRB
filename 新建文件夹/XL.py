import xlwt
import xlrd
import xlutils.copy
from pickle import TRUE
from tkinter import FALSE

#Excel表格操作（不删除表，往后累加数据）
class XL:
    def __init__(self):
        self.tableName='设置速度报文测试'#表名
        self.FileName='./SocketLog.xlsx'#文件路径+文件名
        self.col=('次数','发送时间','接收时间','耗时','备注')#列名
        self.colNum=5#列数
        self.colWidth = 9000#列宽度

        self.style = xlwt.XFStyle()

        borders = xlwt.Borders()#边框样式  DASHED虚线 NO_LINE没有 THIN实线
        borders.left = xlwt.Borders.THIN
        borders.right = xlwt.Borders.THIN
        borders.top = xlwt.Borders.THIN
        borders.bottom = xlwt.Borders.THIN
        self.style.borders = borders

        alignment = xlwt.Alignment()#内容对齐方式
        alignment.horz = xlwt.Alignment.HORZ_CENTER
        self.style.alignment = alignment

        try:
            rd = xlrd.open_workbook(self.FileName, formatting_info = True)   # 打开文件并保留格式
            self.book = xlutils.copy.copy(rd)   # 复制
            self.sheet = self.book.get_sheet(rd.sheet_names().index(self.tableName))   # 读取表名索引对应的工作表
            self.book.save(self.FileName)   # 保存
        except FileNotFoundError as e:
            print('XL Error:' + str(e.args))
            self.CreateXL(TRUE)
            rd = xlrd.open_workbook(self.FileName, formatting_info = True)   # 打开文件并保留格式
        except ValueError as e:
            print('XL Error:' + str(e.args))
            self.CreateXL(FALSE)
        except PermissionError as e:
            print('XL Error:' + str(e.args))
        except Exception as e:
            print('XL Error:' + str(e.args))
        self.row = xlrd.open_workbook(self.FileName, formatting_info = True).sheet_by_name(sheet_name=self.tableName).nrows#当前行数
       
    #创建表（是否重新创建文件）
    def CreateXL(self,isCreate):
        if isCreate:
            self.book = xlwt.Workbook(encoding='utf-8',style_compression=0)
        self.sheet = self.book.add_sheet(self.tableName,cell_overwrite_ok=True)
        for i in range(0,self.colNum):
            self.sheet.col(i).width = self.colWidth
            self.sheet.write(0,i,self.col[i],self.style)
        self.book.save(self.FileName)
        
    # 添加表数据(发送时间，接收时间，耗时，备注)
    def AddData(self,sendTime,receTime,consumeTime,bz):
        self.sheet.write(self.row,0,self.row,self.style)
        self.sheet.write(self.row,1,sendTime,self.style)
        self.sheet.write(self.row,2,receTime,self.style)
        self.sheet.write(self.row,3,consumeTime,self.style)
        self.sheet.write(self.row,4,bz,self.style)
        self.book.save(self.FileName)
        print("写入表格第%d行"%self.row)
        self.row+=1
                