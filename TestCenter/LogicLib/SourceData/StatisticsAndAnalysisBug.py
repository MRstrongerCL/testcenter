# coding:utf-8
# author:chenliang
# time:20200413
# desc: 统计TB上导出来的bug（excel）
'''修改记录：
    20200420：新建 -陈亮
'''
import os
import xlrd
import xlwt
import csv
from TestCenter.LogicLib.PublicMethods import Utf8_To_Unicode

TONG_JI_DICT = {
    "标题":"",
    "任务类型":"",
    "执行者":"",
    "严重程度":"",
    "标签":"",
    "缺陷类型":"",
    "缺陷Owner":"",
    "创建者":"",
    "创建时间":"",
    "更新时间":"",
    "完成时间":"",
    "功能模块":"",
    "任务状态":""
}

# 禅道映射表
TITLE_SPECIAL_DICT_ZENTAO = {
    'Bug标题':'标题',
    'Bug编号':'任务ID',
    '所属模块':'功能模块',
    '创建日期':'创建时间',
    '由谁创建':'创建者',
    'Bug类型':'缺陷类型',
    '解决者':'缺陷Owner',
    'Bug状态':'任务状态',
    '关闭日期':'完成时间',
    '修改日期':'更新时间',
    '严重程度':'严重程度',
    '优先级':'优先级'
}

# 禅道接口映射表
TITLE_SPECIAL_DICT_ZENTAO_API = {
    'title':'标题',
    'id':'任务ID',
    'module':'功能模块',
    'openedDate':'创建时间',
    'openedBy':'创建者',
    'type':'缺陷类型',
    'resolvedBy':'缺陷Owner',
    'status':'任务状态',
    'closedDate':'完成时间',
    'lastEditedDate':'更新时间',
    'severity':'严重程度',
    'pri':'优先级'
}

def sum_dict(a,b):
    '''合并两个字典，相同key对应value相加（value可为整数/浮点数/字符串/列表）'''
    temp = dict()
    # python3,dict_keys类似set； | 并集
    for key in a.keys()| b.keys():
        #根据业务需求修改下面方法，
        temp[key] = sum([d.get(key, 0) for d in (a, b)])
    return temp

class StatisticsAndAnalysisBug(object):
    def __init__(self,filepath='',writestatus=True):
        self.filepath = filepath
        if filepath.endswith('.csv'):
            self.book = csv.reader(open(filepath,'r'))
            self.sheetcount = 1
            self.filetype = 'csv'
        else:
            self.book = xlrd.open_workbook(filepath)
            self.sheetcount = len(self.book.sheets())
            self.filetype = 'xlsx'
        if writestatus:
            self.write_book = xlwt.Workbook(encoding='utf-8',style_compression=0)
        self.all_return_dict = {
            'all_bug_lines': [],
            'all_bug_count': {},
            'owner_create': {},
            'owner_close': {},
            'type_create': {},
            'type_close': {},
            'moudle_create': {},
            'moudle_close': {},
            'creater': {}
        }

    def initCurSheet(self,sheetno=0,sheetname=''):
        if sheetname == '' or sheetname == None:
            if self.filetype == 'csv':
                self.sheet = list(self.book)
                sheetname = os.path.split(self.filepath)[-1].strip('.csv')
                self.nrows = len(self.sheet)
                self.ncols = len(self.sheet[0])
            else:
                self.sheet = self.book.sheet_by_index(sheetno)
                sheetname = self.sheet.name.encode('utf-8')
                self.nrows = self.sheet.nrows
                self.ncols = self.sheet.ncols
        print("===========》sheet名称：%s,  %s行，%s列" % (str(sheetname),self.nrows,self.ncols))
        self.initDict()

    def initDict(self):
        if self.filetype == 'csv':
            oneline = self.sheet[0]
        else:
            oneline = self.sheet.row_values(0)
        index = 0
        self.index_dict_row = {}
        self.index_dict_col = {}
        for one in oneline:
            one = one.lstrip('"').rstrip('"')
            if one in TITLE_SPECIAL_DICT_ZENTAO.keys():
                one = TITLE_SPECIAL_DICT_ZENTAO[Utf8_To_Unicode(one)]
                # one = u'%s' % one
            self.index_dict_row.setdefault(str(index),one)
            self.index_dict_col.setdefault(one,index)
            index += 1
        self.index_dict_row.setdefault(str(index), u'任务类型')
        self.index_dict_col.setdefault(u'任务类型', index)
        return self.index_dict_row

    def OnlineCount(self,stime='2020-03-30 00:42:14',etime='2020-04-20 23:42:14'):
        pass

    def MainCount(self,stime='2020-03-30 00:42:14',etime='2020-04-20 23:42:14'):
        self.start_time = stime
        self.end_time = etime
        title_index = self.index_dict_col[u"标题"]
        thirdid_index = self.index_dict_col[u"任务ID"]
        status_index = self.index_dict_col[u"任务状态"]
        Severity_index = self.index_dict_col[u"严重程度"]
        priority_index = self.index_dict_col[u"优先级"]
        taskType_index = self.index_dict_col[u"任务类型"]
        createTime_index = self.index_dict_col[u"创建时间"]
        closeTime_index = self.index_dict_col[u"完成时间"]
        bugCreator_index = self.index_dict_col[u"创建者"]
        self.bugCreator_count = {}
        bugType_index = self.index_dict_col[u"缺陷类型"]
        self.bugType_create_count = {}
        self.bugType_close_count = {}
        bugOwner_index = self.index_dict_col[u"缺陷Owner"]
        self.bugOwener_create_count = {}
        self.bugOwener_close_count = {}
        bugMoudle_index = self.index_dict_col[u"功能模块"]
        self.bugMoudle_create_count = {}
        self.bugMoudle_close_count = {}
        if self.filetype == 'csv':
            cur_cols = []
            for i in self.sheet[1:]:
                cur_cols.append(u'缺陷')
        else:
            cur_cols = self.sheet.col_values(taskType_index,start_rowx=1)
        total_bug_count = 0
        create_bug_count = 0
        close_bug_count = 0
        cur_index = 1 #第一行是 标题栏，因此索引从1开始
        for one in cur_cols:
            # print(one)
            # print(cur_index)
            if one == u'缺陷':
                # 总bug计数
                total_bug_count +=1
                # 获取缺陷bug这一行完整数据
                if self.filetype == 'csv':
                    cur_line = self.sheet[cur_index]
                else:
                    cur_line = self.sheet.row_values(cur_index)
                cur_stime = cur_line[createTime_index]
                cur_etime = cur_line[closeTime_index]
                create_in = close_in = False
                # 时间区间范围内，新建多少bug
                if cur_stime > stime and cur_stime<=etime :
                    create_bug_count += 1
                    create_in = True
                # 时间区间范围内，完成多少bug
                if cur_etime > stime and cur_stime<=etime :
                    close_bug_count += 1
                    close_in = True
                # 统计bug对应研发，共产生多少个bug
                bugType = cur_line[bugType_index]
                bugOwner = cur_line[bugOwner_index]
                if bugOwner == '' or bugOwner == None:
                    bugOwner = u"空"
                if create_in or close_in:
                    # 生成这一行数据字典
                    line_dict = {
                        u"标题": cur_line[title_index],
                        u"任务ID": cur_line[thirdid_index],
                        u"任务状态": cur_line[status_index],
                        u"严重程度": cur_line[Severity_index],
                        u"优先级": cur_line[priority_index],
                        u"任务类型": cur_line[taskType_index],
                        u"创建时间": cur_stime,
                        u"完成时间": cur_etime,
                        u"创建者": cur_line[bugCreator_index].split('(')[0],  #获取到的名字格式为胡红(accounts_5f07fadbe835c600206e6930@mail.teambition.com)
                        u"缺陷类型": cur_line[bugType_index],
                        u"缺陷Owner": cur_line[bugOwner_index],
                        u"功能模块": cur_line[bugMoudle_index]
                    }
                    # 累计添加行
                    self.all_return_dict['all_bug_lines'].append(line_dict)
                if create_in:
                    if bugType != u'非问题':
                        if bugOwner not in self.bugOwener_create_count.keys():
                            self.bugOwener_create_count.setdefault(bugOwner,1)
                        else:
                            new_count = self.bugOwener_create_count[bugOwner] + 1
                            self.bugOwener_create_count[bugOwner] = new_count
                # 解决多少个bug
                if close_in:
                    if bugType != u'非问题':
                        if bugOwner not in self.bugOwener_close_count.keys():
                            self.bugOwener_close_count.setdefault(bugOwner,1)
                        else:
                            new_count = self.bugOwener_close_count[bugOwner] + 1
                            self.bugOwener_close_count[bugOwner] = new_count
                # 统计缺陷类型对应bug数
                if bugType == '' or bugType == None:
                    bugType = u"空"
                # else:
                #     bugType = bugType.encode('utf-8')
                if create_in:
                    if bugType not in self.bugType_create_count.keys():
                        self.bugType_create_count.setdefault(bugType,1)
                    else:
                        new_count = self.bugType_create_count[bugType] + 1
                        self.bugType_create_count[bugType] = new_count
                if close_in:
                    if bugType not in self.bugType_close_count.keys():
                        self.bugType_close_count.setdefault(bugType,1)
                    else:
                        new_count = self.bugType_close_count[bugType] + 1
                        self.bugType_close_count[bugType] = new_count
                # 统计缺陷创建人对应bug数
                bugCreator = cur_line[bugCreator_index]
                if bugCreator == '' or bugCreator == None:
                    bugCreator = u"空"
                else:
                    bugCreator = bugCreator.split('(')[0]
                if create_in:
                    if bugCreator not in self.bugCreator_count.keys():
                        self.bugCreator_count.setdefault(bugCreator, 1)
                    else:
                        new_count = self.bugCreator_count[bugCreator] + 1
                        self.bugCreator_count[bugCreator] = new_count
                # 统计缺陷功能模块对应bug数
                bugMoudle = cur_line[bugMoudle_index]
                if bugMoudle == '' or bugMoudle == None:
                    bugMoudle = u"空"
                if create_in:
                    if bugMoudle not in self.bugMoudle_create_count.keys():
                        self.bugMoudle_create_count.setdefault(bugMoudle, 1)
                    else:
                        new_count = self.bugMoudle_create_count[bugMoudle] + 1
                        self.bugMoudle_create_count[bugMoudle] = new_count
                if close_in:
                    if bugMoudle not in self.bugMoudle_close_count.keys():
                        self.bugMoudle_close_count.setdefault(bugMoudle, 1)
                    else:
                        new_count = self.bugMoudle_close_count[bugMoudle] + 1
                        self.bugMoudle_close_count[bugMoudle] = new_count

            cur_index += 1
        self.all_bug_count = {"总bug数":total_bug_count,"期间新增bug数":create_bug_count,"期间解决bug数":close_bug_count}
        # 用于接口调用，就不打印了
        # for key,value in self.all_bug_count.items():
        #     print("%s: %s" % (key,value))
        # print("期间研发产生对应bug数------》")
        # for key,value in self.bugOwener_create_count.items():
        #     print("%s: %s" % (key,value))
        # print("期间研发解决对应bug数------》")
        # for key,value in self.bugOwener_close_count.items():
        #     print("%s: %s" % (key,value))
        # print("期间研发产生bug,类型统计------》")
        # for key, value in self.bugType_create_count.items():
        #     print("%s: %s" % (key, value))
        # print("期间研发解决bug，类型统计------》")
        # for key, value in self.bugType_close_count.items():
        #     print("%s: %s" % (key, value))
        # print("期间产出的bug，功能模块统计------》")
        # for key, value in self.bugMoudle_create_count.items():
        #     print("%s: %s" % (key, value))
        # print("期间解决的bug，功能模块统计------》")
        # for key, value in self.bugMoudle_close_count.items():
        #     print("%s: %s" % (key, value))
        # print("期间测试提交bug数统计------》")
        # for key, value in self.bugCreator_count.items():
        #     print("%s: %s" % (key, value))
        self.all_return_dict['all_bug_count'] = sum_dict(self.all_bug_count,self.all_return_dict['all_bug_count'])
        self.all_return_dict['owner_create'] = sum_dict(self.bugOwener_create_count,self.all_return_dict['owner_create'])
        self.all_return_dict['owner_close'] = sum_dict(self.bugOwener_close_count,self.all_return_dict['owner_close'])
        self.all_return_dict['type_create'] = sum_dict(self.bugType_create_count,self.all_return_dict['type_create'])
        self.all_return_dict['type_close'] = sum_dict(self.bugType_close_count,self.all_return_dict['type_close'])
        self.all_return_dict['moudle_create'] = sum_dict(self.bugMoudle_create_count,self.all_return_dict['moudle_create'])
        self.all_return_dict['moudle_close'] = sum_dict(self.bugMoudle_close_count,self.all_return_dict['moudle_close'])
        self.all_return_dict['creater'] = sum_dict(self.bugCreator_count,self.all_return_dict['creater'])

    def writeDate2Excel(self,filepath=''):
        sheetname = self.sheet.name
        self.wsheet = self.write_book.add_sheet(sheetname,cell_overwrite_ok = True)

        index_row = 0
        # 写筛选日期
        self.wsheet.write(index_row,0,'%s - %s' % (self.start_time,self.end_time))
        index_row +=1
        # 写期间新增bug
        self.wsheet.write(index_row,0,'期间新增bug数')
        self.wsheet.write(index_row,1,self.all_bug_count['期间新增bug数'])
        index_row += 1
        # 写期间解决bug数
        self.wsheet.write(index_row,0,'期间解决bug数')
        self.wsheet.write(index_row,1,self.all_bug_count['期间解决bug数'])
        index_row += 1
        # 写对应研发新增解决的bug数
        self.wsheet.write(index_row, 0, "姓名")
        self.wsheet.write(index_row+1, 0, "新增bug数")
        self.wsheet.write(index_row+2, 0, "解决bug数")
        keys = list(set(self.bugOwener_create_count.keys()) | set(self.bugOwener_close_count.keys()))
        col_index = 1
        for key in keys:
            self.wsheet.write(index_row,col_index,key)
            if self.bugOwener_create_count.has_key(key):
                self.wsheet.write(index_row+1, col_index, self.bugOwener_create_count[key])
            if self.bugOwener_close_count.has_key(key):
                self.wsheet.write(index_row+2, col_index, self.bugOwener_close_count[key])
            col_index +=1
        index_row += 3
        # 写对应bug类型新增解决bug数
        self.wsheet.write(index_row, 0, "类型")
        self.wsheet.write(index_row + 1, 0, "新增bug数")
        self.wsheet.write(index_row + 2, 0, "解决bug数")
        keys = list(set(self.bugType_create_count.keys()) | set(self.bugType_close_count.keys()))
        col_index = 1
        for key in keys:
            self.wsheet.write(index_row, col_index, key)
            if self.bugType_create_count.has_key(key):
                self.wsheet.write(index_row + 1, col_index, self.bugType_create_count[key])
            if self.bugType_close_count.has_key(key):
                self.wsheet.write(index_row + 2, col_index, self.bugType_close_count[key])
            col_index += 1
        index_row += 3
        # 写对应bug类型新增解决bug数
        self.wsheet.write(index_row, 0, "功能模块")
        self.wsheet.write(index_row + 1, 0, "新增bug数")
        self.wsheet.write(index_row + 2, 0, "解决bug数")
        keys = list(set(self.bugMoudle_create_count.keys()) | set(self.bugMoudle_close_count.keys()))
        col_index = 1
        for key in keys:
            self.wsheet.write(index_row, col_index, key)
            if self.bugMoudle_create_count.has_key(key):
                self.wsheet.write(index_row + 1, col_index, self.bugMoudle_create_count[key])
            if self.bugMoudle_close_count.has_key(key):
                self.wsheet.write(index_row + 2, col_index, self.bugMoudle_close_count[key])
            col_index += 1
        index_row += 3
        # 写对应测试人员提交bug数
        self.wsheet.write(index_row, 0, "姓名")
        self.wsheet.write(index_row + 1, 0, "提交bug数")
        keys = self.bugCreator_count.keys()
        col_index = 1
        for key in keys:
            if self.bugCreator_count.has_key(key):
                self.wsheet.write(index_row, col_index, key)
                self.wsheet.write(index_row+1, col_index, self.bugCreator_count[key])
            col_index +=1
        # 保存excel
        self.write_book.save(filepath)

class StatisticsBugFromList(object):
    '''根据bug列表统计
    列表如：[{"标题":"【审批管理】页面排版不整齐","项目":"营收系统【项目迭代开发】","创建时间":"12/30/20"}]
    '''
    specialtitle = {}  #用于替换为tongji中的key的标准名称
    tongji = list(TONG_JI_DICT.keys())

    @classmethod
    def handle_module(cls,s_module_str):
        '''梳理功能模块 /移动端/消息（#234） ---> 消息（#234）'''
        try:
            t_module_str = s_module_str.split('/')[-1]
        except:
            t_module_str = s_module_str
        return t_module_str

    @classmethod
    def handle_time(cls,s_time_str,add_end_time='head'):
        '''处理时间字符串 7/15/21 --> 2021-07-15 00:00:01'''
        try:
            if '/' in s_time_str:
                ee = s_time_str.split(' ')[0].split('/')
                if len(ee[0]) <= 2:
                    if add_end_time == 'head':
                        t_timestr = "20{}-{:0>2}-{:0>2} 00:01".format(ee[2], ee[0], ee[1])
                    else:
                        t_timestr = "20{}-{:0>2}-{:0>2} 23:59".format(ee[2], ee[0], ee[1])
                else:
                    t_timestr = s_time_str
            else:
                if '0000-00' in s_time_str:
                    t_timestr = '3000-01-01 23:59'
                else:
                    t_timestr = s_time_str
        except:
            if add_end_time == 'head':
                t_timestr = '2000-01-01 00:01'
            else:
                t_timestr = '3000-01-01 23:59'
        return t_timestr

    @classmethod
    def StatisticsAll(cls,buglist=[], stime='',etime=''):
        '''返回数据库所需bug列表 (teamBition中bug的字段)'''
        # 判断excel字段是否齐全

        newbuglist = []
        # 换key的名称，主要针对 v3-功能模块、v2-功能模块，统一换成 功能模块
        for oneline in buglist:
            # 创建者删除多余字符
            try:
                oneline["创建者"] = oneline["创建者"].split('(')[0]
            except:
                pass
            # 兼容没有时间的bug
            try:
                if '/' in oneline["创建时间"]:
                    ss = oneline["创建时间"].split(' ')[0].split('/')
                    cur_stime = oneline["创建时间"] = "20{}-{:0>2}-{:0>2} 00:01".format(ss[2],ss[0],ss[1])
                else:
                    cur_stime = oneline["创建时间"]
            except:
                cur_stime = '2000-01-01 00:01'
            try:
                if '/' in oneline["修改日期"]:
                    ee = oneline["修改日期"].split(' ')[0].split('/')
                    cur_utime = oneline["修改日期"]  = "20{}-{:0>2}-{:0>2} 23:59".format(ee[2],ee[0],ee[1])
                else:
                    cur_utime = oneline["修改日期"]
            except:
                cur_utime = '3000-01-01 23:59'
            try:
                if '/' in oneline["完成时间"]:
                    ee = oneline["完成时间"].split(' ')[0].split('/')
                    cur_etime = oneline["完成时间"]  = "20{}-{:0>2}-{:0>2} 23:59".format(ee[2],ee[0],ee[1])
                else:
                    cur_etime = oneline["完成时间"]
            except:
                cur_etime = '3000-01-01 23:59'
            if cur_stime>stime and cur_stime<etime:
                create_in = True
            else:
                create_in = False
            # if cur_etime>stime and cur_etime<etime:
            #     close_in = True
            # else:
            #     close_in = False
            # if create_in or close_in:
            # 只以当前迭代新增为基础统计（排除当前迭代解决的以往的bug）
            if create_in:
                for key in oneline.keys():
                    if cls.specialtitle != {}:
                        for skey,value in cls.specialtitle.items():
                            if skey in key:
                                oneline.setdefault(value, oneline.pop(key))
                newbuglist.append(oneline)
        return newbuglist

    @classmethod
    def StatisticsAll_zentao(cls,buglist=[], stime='',etime=''):
        '''返回数据库所需bug列表 (禅道中bug的字段)'''
        # 判断excel字段是否齐全
        cls.specialtitle = TITLE_SPECIAL_DICT_ZENTAO
        newbuglist = []
        # 换key的名称，主要针对 v3-功能模块、v2-功能模块，统一换成 功能模块
        for oneline in buglist:
            # 创建者删除多余字符
            try:
                oneline["由谁创建"] = oneline["由谁创建"].split('(')[0]
            except:
                pass
            # 兼容没有时间的bug
            cur_stime = oneline["创建日期"] = cls.handle_time(oneline["创建日期"],add_end_time='head')
            oneline["修改日期"] = cls.handle_time(oneline["修改日期"],add_end_time='end')
            try:
                cur_etime = oneline["关闭日期"] = cls.handle_time(oneline["关闭日期"],add_end_time='end')
            except:
                cur_etime = oneline["关闭日期"] = ''
            oneline['所属模块'] = cls.handle_module(oneline['所属模块'])
            if cur_stime>=stime and cur_stime<=etime:
                create_in = True
            else:
                create_in = False
            # if cur_etime>=stime and cur_etime<=etime:
            #     close_in = True
            # else:
            #     close_in = False
            # if create_in or close_in:
            # 只以当前迭代新增为基础统计（排除当前迭代解决的以往的bug）
            if create_in:
                newline = {}
                for key in oneline.keys():
                    if cls.specialtitle != {}:
                        for skey,value in cls.specialtitle.items():
                            if skey in key:
                                newline.setdefault(value, oneline[key])
                                break
                newbuglist.append(newline)
        return newbuglist

    @classmethod
    def StatisticsAll_zentao_api(cls,buglist=[],bugfields={},userdict={},stime='',etime=''):
        '''返回数据库所需bug列表 (禅道中bug的字段)'''
        # 判断excel字段是否齐全
        cls.specialtitle = TITLE_SPECIAL_DICT_ZENTAO_API
        bugtype_dict = bugfields['categories']
        bugmoudle_dict = bugfields['modules']
        newbuglist = []
        # 换key的名称，主要针对 v3-功能模块、v2-功能模块，统一换成 功能模块
        for oneline in buglist:
            for key in oneline.keys():
                if cls.specialtitle != {}:
                    for skey,value in cls.specialtitle.items():
                        if skey in key:
                            oneline.setdefault(value, oneline.pop(key))
                            break
                            # 创建者删除多余字符
            try:
                oneline["创建者"] = userdict[oneline["创建者"]]
            except:
                pass
            try:
                oneline["功能模块"] = bugmoudle_dict[oneline["功能模块"]]
            except:
                pass
            try:
                oneline["缺陷类型"] = bugtype_dict[oneline["缺陷类型"]]
            except:
                pass
            try:
                if oneline['缺陷Owner'] == '':
                    oneline["缺陷Owner"] = userdict[oneline["assignedTo"]]
                else:
                    oneline["缺陷Owner"] = userdict[oneline["缺陷Owner"]]
            except:
                pass
            # 兼容没有时间的bug
            cur_stime = oneline["创建时间"] = cls.handle_time(oneline["创建时间"], add_end_time='head')
            oneline["更新时间"] = cls.handle_time(oneline["更新时间"], add_end_time='end')
            cur_etime = oneline["完成时间"] = cls.handle_time(oneline["完成时间"], add_end_time='end')
            oneline['功能模块'] = cls.handle_module(oneline['功能模块'])

            if cur_stime >= stime and cur_stime <= etime:
                create_in = True
            else:
                create_in = False
            # if cur_etime >= stime and cur_etime <= etime:
            #     close_in = True
            # else:
            #     close_in = False
            # if create_in or close_in:
            # 只以当前迭代新增为基础统计（排除当前迭代解决的以往的bug）
            if create_in:
                title = oneline["标题"]
                if ("线上环境" in title) or ("生产环境" in title) or ("prod" in title) or ("【线上】" in title):
                    oneline["lineType"] = 'online'
                else:
                    oneline["lineType"] = 'offline'
                if oneline["缺陷类型"] == '' or oneline["缺陷类型"] == None:
                    oneline["缺陷类型"] = "其他"
                if oneline["功能模块"] == '' or oneline["功能模块"] == None:
                    oneline["功能模块"] = "其他"
                newbuglist.append(oneline)
        return newbuglist

    @classmethod
    def Statistics_total_zentaoEXCEL(cls, buglist=[]):
        '''根据标准bug列表，计算出 总共多少bug、已解决多少bug'''
        on_total = 0
        on_resolved = 0
        off_total = 0
        off_resolved = 0
        for bug in buglist:
            status = bug["任务状态"]
            title = bug["标题"]
            if "线上环境" in title or "生产环境" in title or "prod" in title or "【线上】" in title:
                on_total += 1
                if status == '已解决' or status == '已关闭' or status == 'closed':
                    on_resolved += 1
            else:
                off_total += 1
                if status == '已解决' or status == '已关闭' or status == 'closed':
                    off_resolved += 1
        return on_total,on_resolved,off_total,off_resolved

    @classmethod
    def Statistics_total_zentoAPI(cls, buglist=[]):
        '''根据标准bug列表，计算出 总共多少bug、已解决多少bug'''
        on_total = 0
        on_resolved = 0
        off_total = 0
        off_resolved = 0
        for bug in buglist:
            status = bug["status"]
            title = bug["title"]
            if "线上环境" in title or "生产环境" in title or "prod" in title or "【线上】" in title:
                on_total += 1
                if status == '已解决' or status == '已关闭' or status == 'closed':
                    on_resolved += 1
            else:
                off_total += 1
                if status == '已解决' or status == '已关闭' or status == 'closed':
                    off_resolved += 1
        return on_total,on_resolved,off_total,off_resolved

def statisticsANDoutput():
    inputfile_path=u'【营收系统【线上缺陷反馈】】任务信息表_20201010.xlsx'
    outputfile_path=u'统计_营收系统_线上_20201010.xlsx'
    start_time = '2020-08-22 08:00:14'
    end_time = '2020-10-11 08:30:14'
    sab = StatisticsAndAnalysisBug(filepath=inputfile_path)
    for i in range(sab.sheetcount):
        sab.initCurSheet(i)
        sab.MainCount(stime=start_time,etime=end_time)
        sab.writeDate2Excel(filepath=outputfile_path)

def ReadBugExcel(inputfile_path='',start_time='2020-08-22 08:00:14',end_time='2021-10-11 08:30:14'):
    '''用于其他模块调用并返回bug统计结果'''
    sab = StatisticsAndAnalysisBug(filepath=inputfile_path,writestatus=False)
    for i in range(sab.sheetcount):
        sab.initCurSheet(i)
        sab.MainCount(stime=start_time,etime=end_time)
    return sab.all_return_dict

if __name__ == '__main__':
    # statisticsANDoutput()
    a = ReadBugExcel(inputfile_path='D:\\Temple\\HSH-东语移动用户端-所有Bug.csv')
    print(a)

