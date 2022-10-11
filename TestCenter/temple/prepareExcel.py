# coding:gbk
# author:chenliang
# write time:2022-09-24

import os,time,datetime
import xlwt,xlrd
import random

class editExcel(object):
    """基础操作，方便准备导入平台的bug数据 excel，字段采用禅道字段"""
    def __init__(self):
        self.book = xlwt.Workbook(encoding='utf-8', style_compression=0)
        self.row_no = 0

    def insert_title(self, table_name='aa', titles=[]):
        self.sheet = self.book.add_sheet(table_name, cell_overwrite_ok=True)  # 其中的aa是这张表的名字
        for title in titles:
            col_no = titles.index(title)
            try:
                ntitle = title.decode('utf-8')
            except:
                ntitle = title
            self.sheet.write(self.row_no, col_no, ntitle)
        self.row_no += 1

    def add_row(self, row=[]):
        col_no = 0
        for one in row:
            try:
                none = one.decode('utf-8')
            except:
                none = one
            self.sheet.write(self.row_no,col_no,none)
            col_no += 1
        self.row_no += 1

    def save_excel(self, filepath):
        nfile = r'%s' % filepath   # 在字符串前加r，声明为raw字符串，这样就不会处理其中的转义了。否则，可能会报错
        self.book.save(nfile)


    def writeExcel(self):
        """写示例"""
        book=xlwt.Workbook(encoding='utf-8',style_compression = 0)
        # 创建一个sheet对象，一个sheet对象对应Excel文件中的一张表格。
        # 在电脑桌面右键新建一个Excel文件，其中就包含sheet1，sheet2，sheet3三张表
        sheet=book.add_sheet('aa',cell_overwrite_ok = True)  # 其中的aa是这张表的名字
        # 向表aa中添加数据
        sheet.write(0,0,'EnglishName')  # 其中的'0,0'指定表中的单元，'EnglishName'是向该单元写入的内容
        sheet.write(1,0,'Marcovaldo')
        txt1='中文名字'
        sheet.write(0,1,txt1.decode('utf-8'))  # 此处需要将中文字符串解码成unicode码，否则会报错
        txt2='马可瓦多'
        sheet.write(1,1,txt2.decode('utf-8'))
        # 最后，将以上操作保存到指定的Excel文件中
        book.save(r'e:\try1.xlsx')  # 在字符串前加r，声明为raw字符串，这样就不会处理其中的转义了。否则，可能会报错

    def readExcel(self):
        """读示例"""
        excel_path = os.path.normpath("E:\\WorkSpace\\MyTools\\易维导入数据\\eas与云之家匹配的员工关系数据.xls")
        book = xlrd.open_workbook(excel_path)
        sheet0 = book.sheet_by_index(0)
        sheet0_name = book.sheet_names()[0]
        print(sheet0_name)

        sheet1 = book.sheet_by_name(sheet0_name)
        nrows = sheet1.nrows
        print(nrows)

        ncols = sheet1.ncols
        print(ncols)

        row1_data = sheet1.row_values(0)
        print(row1_data)

        cell_value1 = sheet0.cell_value(0, 0)
        print(cell_value1)

class preCandaoBugs():
    """准备导入平台的bug数据 excel，字段采用禅道字段"""

    def __init__(self, bug_id=1, group_name='东语', filename='导入001.xlsx', typestr='offline'):
        self.titles = ['Bug编号', '所属模块', 'Bug标题', '严重程度', '优先级', 'Bug类型', 'Bug状态', '由谁创建', '创建日期', '指派给', '指派日期', '解决者', '解决方案',
              '解决日期', '由谁关闭', '关闭日期', '修改日期']
        self.ee = editExcel()
        self.ee.insert_title('禅道', self.titles)
        self.bug_id = bug_id
        self.filename = filename
        self.group_name = group_name
        self.ownType = typestr

    def choice_moudle(self):
        mudles = ['在线交谈',"工单","用户管理"]
        self.moudle = random.choice(mudles)
        return self.moudle

    def choice_bugtitle(self):
        rantiles = gbk2312(random.choice(range(40)[10:]))
        title = '生产环境' if self.ownType=='online' else '测试环境'
        self.bug_name = "【%s】%s %s" % (title, rantiles,self.bug_id)
        return self.bug_name

    def choice_serious(self):
        serious = ['1','2','3','4']
        self.seriou = random.choice(serious)
        return self.seriou

    def choice_parities(self):
        parities = ['1','2','3','4']
        self.parity = random.choice(parities)
        return self.parity

    def choice_type(self):
        types = ['后端代码错误','前端代码错误','环境故障','运维问题',"第三方问题","设计问题","非问题"]
        self.type = random.choice(types)
        return self.type

    def choice_status(self):
        status_all = ['处理中','待处理','重新打开',"已解决",'已关闭',"已解决",'已关闭',"已解决",'已关闭',"已解决",'已关闭']
        self.status = random.choice(status_all)
        return self.status

    def choice_creater(self, group='东语'):
        if group == '东语':
            creaters = ['满晋','吕莉']
        elif group == '物业':
            creaters = ['张凯', '舒谦谦']
        elif group == '新消费':
            creaters = ['彭朝明', '周俨']
        else:
            creaters = ['满晋', '吕莉']
        self.creater = random.choice(creaters)
        return self.creater

    def choice_solver(self, group='东语'):
        if group == '东语':
            solvers = ['邓东山','周攀蔚','马涛','朱佳佳']
        elif group == '物业':
            solvers = ['王福顺', '陈松伟',"李林贵","郭鑫"]
        elif group == '新消费':
            solvers = ['胡国庆', '费小龙','许佳俊',"赵升"]
        else:
            solvers = ['满晋', '吕莉']
        self.solver = random.choice(solvers)
        return self.solver

    def choice_methods(self):
        methods = ['已修复', '延期', '不解决',"非问题"]
        self.method = random.choice(methods)
        return self.method

    def choice_createtime(self,sday_str='2022-8-1 12:00'):
        self.create_time = sday_str
        return self.create_time

    def choice_solvedtime(self,eday_str='2022-8-2 12:00'):
        self.solvedtime = eday_str if self.status in ['已关闭',"已解决"] else ''
        return self.solvedtime

    def choice_updatedtime(self):
        self.updatedtime = self.solvedtime if self.status in ['已关闭',"已解决"] else self.create_time
        return self.updatedtime

    def preRow(self,sday_str='2022-8-1 12:00',eday_str='2022-8-2 12:00'):
        # 顺序很重要
        rows = [
            self.bug_id,
            self.choice_moudle(),
            self.choice_bugtitle(),
            self.choice_serious(),
            self.choice_parities(),
            self.choice_type(),
            self.choice_status(),
            self.choice_creater(group=self.group_name),
            self.choice_createtime(sday_str),
            self.choice_solver(group=self.group_name),
            self.choice_createtime(sday_str),
            self.choice_solver(group=self.group_name),
            self.choice_methods(),
            self.choice_solvedtime(eday_str),
            self.choice_creater(group=self.group_name),
            self.choice_solvedtime(eday_str),
            self.choice_updatedtime()
        ]
        self.ee.add_row(rows)

    def preRows(self, count=1, sday='2022-8-10 12:00', eday='2022-9-1 12:00'):
        sdays = datetime.datetime.strptime(sday, '%Y-%m-%d %H:%M')
        edays = datetime.datetime.strptime(eday, '%Y-%m-%d %H:%M')
        days = (edays - sdays).days
        split_count = count // days + 1
        compute = 1
        for day in range(days):
            sday = (sdays + datetime.timedelta(days=day)).strftime('%Y-%m-%d %H:%M')
            eday = (sdays + datetime.timedelta(days=day+1)).strftime('%Y-%m-%d %H:%M')
            term_count = random.choice(range(split_count)) # 构造每次创建随机个数的bug
            for i in range(term_count):
                self.preRow(sday,eday)
                self.bug_id += 1
                compute += 1

        print("... %s 条数据创建完成！ " % compute)

    def save(self):
        self.ee.save_excel(self.filename)
        print("... excel文件保存成功：%s " % self.filename)

def gbk2312(n=1):
    sss = ''
    for i in range(n):
        head = random.randint(0xb0,0xd6)
        body = random.randint(0xa1,0xfe)
        val = f'{head:x}{body:x}'
        ss = bytes.fromhex(val).decode('gb2312')
        sss += ss
    # print(sss)
    return sss

def prepare():
    filenames = ['东语-线下.xlsx', '物业-线下.xlsx', '新消费-线下.xlsx', '东语-线上.xlsx', '物业-线上.xlsx', '新消费-线上.xlsx']
    startid = 1
    evry_count = 100
    fnames = filenames[0:]
    for fname in fnames:
        typestr = 'online' if '线上' in fname else 'offline'  #用于bug标题区分 线上bug还是线下bug
        evry_count = evry_count//4 if '线上' in fname else evry_count # 用于使线上bug少于线下
        pcb = preCandaoBugs(startid, filename=fname, typestr=typestr)
        pcb.preRows(evry_count, sday='2022-9-24 12:00', eday='2022-10-7 12:00')
        pcb.save()
        startid += evry_count

if __name__ == '__main__':
    prepare()
    # gbk2312(10)