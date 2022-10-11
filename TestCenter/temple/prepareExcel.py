# coding:gbk
# author:chenliang
# write time:2022-09-24

import os,time,datetime
import xlwt,xlrd
import random

class editExcel(object):
    """��������������׼������ƽ̨��bug���� excel���ֶβ��������ֶ�"""
    def __init__(self):
        self.book = xlwt.Workbook(encoding='utf-8', style_compression=0)
        self.row_no = 0

    def insert_title(self, table_name='aa', titles=[]):
        self.sheet = self.book.add_sheet(table_name, cell_overwrite_ok=True)  # ���е�aa�����ű������
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
        nfile = r'%s' % filepath   # ���ַ���ǰ��r������Ϊraw�ַ����������Ͳ��ᴦ�����е�ת���ˡ����򣬿��ܻᱨ��
        self.book.save(nfile)


    def writeExcel(self):
        """дʾ��"""
        book=xlwt.Workbook(encoding='utf-8',style_compression = 0)
        # ����һ��sheet����һ��sheet�����ӦExcel�ļ��е�һ�ű��
        # �ڵ��������Ҽ��½�һ��Excel�ļ������оͰ���sheet1��sheet2��sheet3���ű�
        sheet=book.add_sheet('aa',cell_overwrite_ok = True)  # ���е�aa�����ű������
        # ���aa���������
        sheet.write(0,0,'EnglishName')  # ���е�'0,0'ָ�����еĵ�Ԫ��'EnglishName'����õ�Ԫд�������
        sheet.write(1,0,'Marcovaldo')
        txt1='��������'
        sheet.write(0,1,txt1.decode('utf-8'))  # �˴���Ҫ�������ַ��������unicode�룬����ᱨ��
        txt2='����߶�'
        sheet.write(1,1,txt2.decode('utf-8'))
        # ��󣬽����ϲ������浽ָ����Excel�ļ���
        book.save(r'e:\try1.xlsx')  # ���ַ���ǰ��r������Ϊraw�ַ����������Ͳ��ᴦ�����е�ת���ˡ����򣬿��ܻᱨ��

    def readExcel(self):
        """��ʾ��"""
        excel_path = os.path.normpath("E:\\WorkSpace\\MyTools\\��ά��������\\eas����֮��ƥ���Ա����ϵ����.xls")
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
    """׼������ƽ̨��bug���� excel���ֶβ��������ֶ�"""

    def __init__(self, bug_id=1, group_name='����', filename='����001.xlsx', typestr='offline'):
        self.titles = ['Bug���', '����ģ��', 'Bug����', '���س̶�', '���ȼ�', 'Bug����', 'Bug״̬', '��˭����', '��������', 'ָ�ɸ�', 'ָ������', '�����', '�������',
              '�������', '��˭�ر�', '�ر�����', '�޸�����']
        self.ee = editExcel()
        self.ee.insert_title('����', self.titles)
        self.bug_id = bug_id
        self.filename = filename
        self.group_name = group_name
        self.ownType = typestr

    def choice_moudle(self):
        mudles = ['���߽�̸',"����","�û�����"]
        self.moudle = random.choice(mudles)
        return self.moudle

    def choice_bugtitle(self):
        rantiles = gbk2312(random.choice(range(40)[10:]))
        title = '��������' if self.ownType=='online' else '���Ի���'
        self.bug_name = "��%s��%s %s" % (title, rantiles,self.bug_id)
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
        types = ['��˴������','ǰ�˴������','��������','��ά����',"����������","�������","������"]
        self.type = random.choice(types)
        return self.type

    def choice_status(self):
        status_all = ['������','������','���´�',"�ѽ��",'�ѹر�',"�ѽ��",'�ѹر�',"�ѽ��",'�ѹر�',"�ѽ��",'�ѹر�']
        self.status = random.choice(status_all)
        return self.status

    def choice_creater(self, group='����'):
        if group == '����':
            creaters = ['����','����']
        elif group == '��ҵ':
            creaters = ['�ſ�', '��ǫǫ']
        elif group == '������':
            creaters = ['����', '��ٲ']
        else:
            creaters = ['����', '����']
        self.creater = random.choice(creaters)
        return self.creater

    def choice_solver(self, group='����'):
        if group == '����':
            solvers = ['�˶�ɽ','����ε','����','��Ѽ�']
        elif group == '��ҵ':
            solvers = ['����˳', '����ΰ',"���ֹ�","����"]
        elif group == '������':
            solvers = ['������', '��С��','��ѿ�',"����"]
        else:
            solvers = ['����', '����']
        self.solver = random.choice(solvers)
        return self.solver

    def choice_methods(self):
        methods = ['���޸�', '����', '�����',"������"]
        self.method = random.choice(methods)
        return self.method

    def choice_createtime(self,sday_str='2022-8-1 12:00'):
        self.create_time = sday_str
        return self.create_time

    def choice_solvedtime(self,eday_str='2022-8-2 12:00'):
        self.solvedtime = eday_str if self.status in ['�ѹر�',"�ѽ��"] else ''
        return self.solvedtime

    def choice_updatedtime(self):
        self.updatedtime = self.solvedtime if self.status in ['�ѹر�',"�ѽ��"] else self.create_time
        return self.updatedtime

    def preRow(self,sday_str='2022-8-1 12:00',eday_str='2022-8-2 12:00'):
        # ˳�����Ҫ
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
            term_count = random.choice(range(split_count)) # ����ÿ�δ������������bug
            for i in range(term_count):
                self.preRow(sday,eday)
                self.bug_id += 1
                compute += 1

        print("... %s �����ݴ�����ɣ� " % compute)

    def save(self):
        self.ee.save_excel(self.filename)
        print("... excel�ļ�����ɹ���%s " % self.filename)

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
    filenames = ['����-����.xlsx', '��ҵ-����.xlsx', '������-����.xlsx', '����-����.xlsx', '��ҵ-����.xlsx', '������-����.xlsx']
    startid = 1
    evry_count = 100
    fnames = filenames[0:]
    for fname in fnames:
        typestr = 'online' if '����' in fname else 'offline'  #����bug�������� ����bug��������bug
        evry_count = evry_count//4 if '����' in fname else evry_count # ����ʹ����bug��������
        pcb = preCandaoBugs(startid, filename=fname, typestr=typestr)
        pcb.preRows(evry_count, sday='2022-9-24 12:00', eday='2022-10-7 12:00')
        pcb.save()
        startid += evry_count

if __name__ == '__main__':
    prepare()
    # gbk2312(10)