import random
from pyecharts.charts import Line
from pyecharts.charts import Bar
from pyecharts.charts import Pie
from pyecharts.charts import Grid
from pyecharts.charts import Radar
from pyecharts.globals import ThemeType
from pyecharts import options as opts
from TestCenter.LogicLib import OperationDB
from TestCenter.LogicLib.Config import TC_Programs
from TestCenter.LogicLib.PublicMethods import Get_Date
from TestCenter.LogicLib.OperationDB import readTargetRate

# -------------------------- 全局参数 ---------------------------------------

def myline():
    attr = ['教师', '教授', '副教授', '博导', '硕导', '国家级奖项', '省部级奖项', '院士', '荣誉学者', '专利']
    v1 = [100, 20, 15, 50, 40, 200, 200, 4, 5, 100]
    v2 = [150, 30, 40, 50, 30, 250, 200, 1, 2, 110]
    lines = Line()
    lines.add_xaxis(attr)
    lines.add_yaxis('北京大学',v1)
    lines.add_yaxis('清华大学',v2)
    return lines

def CombiningTableDataAndPicData(title_key_tuple,all_dict,useto='pic'):
    '''根据数据和title关系，所有的数据纵列，生成列表行数据 和 图标 纵列数据'''
    # 初始化列表title
    module_fields = []
    # 初始化图表横坐标
    modules = []
    # 初始化图表 纵列数据
    yattr = {}
    # 初始化列表 行数据
    table = {}
    # 设置横坐标计数状态，第一轮计数后，就可关闭计数
    m_status = True
    for title, key in title_key_tuple:
        yattr.setdefault(key, [])
        table.setdefault(key, {'type': title, "module1": 2})

        # 分别拼装 前端列表 和 图表所有 数据
        i = 1
        for column_title, numsdict in all_dict.items():
            if m_status:
                module_fields.append(['module%s' % i, column_title])  # 列表title对应
                modules.append(column_title)  # 图表横坐标
            if useto.lower() == 'pic':
                # 图标纵列数据
                yattr[key].append(numsdict[key])
            else:
                # 列表行数据
                table[key]['module%s' % i] = "{:.2f}%".format(numsdict[key]) if "Rate" in key or "percent" in key else numsdict[key]
            i += 1
        m_status = False

    if useto.lower() == 'pic':
        # 图标纵列数据
        return yattr,modules,module_fields
    else:
        # 列表行数据
        return table,modules,module_fields

def bugline(programname='V2',type='offline',useto='pic',limit=7):
    '''近期bug统计、折线图 （每天）
    programname: 项目名称
    type： 线上、线下、全部
    useto: 用途：画图、统计
    limit: 最近几次
    '''
    programs,countss = OperationDB.getProgram(programname)
    if programname != None and programname != '' and programs == []:
        if useto=='pic':
            lines = Bar(init_opts=opts.InitOpts(width="1000px", height="330px"))
            return lines,[]
        else:
            return [],[]
    progrmid = programs.id
    date_strs = []
    for i in list(range(limit)):
        lastdays = 0 - i
        day_date = Get_Date(timetype='auto',days=lastdays)
        date_strs.append(day_date)
    xattr = used_dates = date_strs[::-1]

    off_created_dict = {'type': "迭代新增", "itera1": 3}
    off_closed_dict = {'type': "迭代解决", "itera1": 2}
    on_created_dict = {'type': "线上新增", "itera1": 3}
    on_closed_dict = {'type': "线上解决", "itera1": 2}
    yattr = {
        'off_created_nums':[],
        'off_closed_nums':[],
        'on_created_nums':[],
        'on_closed_nums':[],
    }
    days_list = []
    i = 1
    for day_str in used_dates:
        off_created_nums = OperationDB.readBugNumsAccordCondition({'program': progrmid,'type_owner':'offline','create_time__startswith':day_str})
        off_closed_nums1 = OperationDB.readBugNumsAccordCondition({'program': progrmid, 'status': '已关闭','type_owner':'offline','create_time__startswith':day_str})
        off_closed_nums2 = OperationDB.readBugNumsAccordCondition({'program': progrmid, 'status': '已解决','type_owner':'offline','create_time__startswith':day_str})
        off_closed_nums3 = OperationDB.readBugNumsAccordCondition({'program': progrmid, 'status': 'closed','type_owner':'offline','create_time__startswith':day_str})
        off_closed_nums = off_closed_nums1 + off_closed_nums2 + off_closed_nums3
        on_created_nums = OperationDB.readBugNumsAccordCondition({'program': progrmid,'type_owner':'online','create_time__startswith':day_str})
        on_closed_nums1 = OperationDB.readBugNumsAccordCondition({'program': progrmid, 'status': '已关闭','type_owner':'online','create_time__startswith':day_str})
        on_closed_nums2 = OperationDB.readBugNumsAccordCondition({'program': progrmid, 'status': '已解决','type_owner':'online','create_time__startswith':day_str})
        on_closed_nums3 = OperationDB.readBugNumsAccordCondition({'program': progrmid, 'status': 'closed','type_owner':'online','create_time__startswith':day_str})
        on_closed_nums = on_closed_nums1 + on_closed_nums2 + on_closed_nums3
        if useto.lower() == 'pic':
            if type == 'offline':
                yattr['off_created_nums'].append(off_created_nums)
                yattr['off_closed_nums'].append(off_closed_nums)
            elif type == 'online':
                yattr['on_created_nums'].append(on_created_nums)
                yattr['on_closed_nums'].append(on_closed_nums)
            else:
                yattr['off_created_nums'].append(off_created_nums)
                yattr['off_closed_nums'].append(off_closed_nums)
                yattr['on_created_nums'].append(on_created_nums)
                yattr['on_closed_nums'].append(on_closed_nums)
        else:
            if type == 'offline':
                off_created_dict['itera%s' % i] = off_created_nums
                off_closed_dict['itera%s' % i] = off_closed_nums
            elif type == 'online':
                on_created_dict['itera%s' % i] = on_created_nums
                on_closed_dict['itera%s' % i] = on_closed_nums
            else:
                off_created_dict['itera%s' % i] = off_created_nums
                off_closed_dict['itera%s' % i] = off_closed_nums
                on_created_dict['itera%s' % i] = on_created_nums
                on_closed_dict['itera%s' % i] = on_closed_nums
        days_list.append(['itera%s' % i, day_str])
        i += 1
    if useto.lower() == 'pic':
        lines = Line(init_opts=opts.InitOpts(width="1000px",height="330px"))
        lines.add_xaxis(xattr)
        if type == 'offline':
            lines.add_yaxis('迭代新增bug', yattr['off_created_nums'])
            lines.add_yaxis('迭代解决bug', yattr['off_closed_nums'])
        elif type == 'online':
            lines.add_yaxis('线上新增bug', yattr['on_created_nums'])
            lines.add_yaxis('线上解决bug', yattr['on_closed_nums'])
        else:
            lines.add_yaxis('迭代新增bug', yattr['off_created_nums'])
            lines.add_yaxis('迭代解决bug', yattr['off_closed_nums'])
            lines.add_yaxis('线上新增bug', yattr['on_created_nums'])
            lines.add_yaxis('线上解决bug', yattr['on_closed_nums'])
        return lines,days_list
    else:
        if type == 'offline':
            data = [off_created_dict,off_closed_dict]
        elif type == 'online':
            data = [on_created_dict,on_closed_dict]
        else:
            data = [off_created_dict,off_closed_dict,on_created_dict,on_closed_dict]
        return data,days_list

def bugline_iteration(programname='V2',type='offline',useto='pic',limit=7):
    '''历史迭代统计、折线图
    programname: 项目名称
    type： 线上、线下、全部
    useto: 用途：画图、统计
    limit: 最近几次
    '''
    programs,countss = OperationDB.getProgram(programname)
    if programname != None and programname != '' and programs == []:
        if useto=='pic':
            lines = Bar(init_opts=opts.InitOpts(width="1000px", height="330px"))
            return lines,[]
        else:
            return [],[]
    progrmid = programs.id
    iterations = OperationDB.readIterationsAccordProgramID(progrmid,limit)
    iteration_ids = iterations['ids']
    xattr = iteration_versions = iterations['versions']
    off_created_dict = {'type': "迭代新增", "itera1": 3}
    off_closed_dict = {'type': "迭代解决", "itera1": 2}
    off_percent_dict = {'type': "迭代解决率", "itera1": 2}
    on_created_dict = {'type': "线上新增", "itera1": 3}
    on_closed_dict = {'type': "线上解决", "itera1": 2}
    on_percent_dict = {'type': "线上解决率", "itera1": 2}
    yattr = {
        'off_created_nums':[],
        'off_closed_nums':[],
        'off_percent_nums':[],
        'on_created_nums':[],
        'on_closed_nums':[],
        'on_percent_nums':[],
    }
    versions = []
    i = 1
    for id_version in zip(iteration_ids, iteration_versions):
        id = id_version[0]
        version = id_version[1]
        off_created_nums = OperationDB.readBugNumsAccordCondition({'iteration': id,'type_owner':'offline'})
        off_closed_nums1 = OperationDB.readBugNumsAccordCondition({'iteration': id, 'status': '已关闭','type_owner':'offline'})
        off_closed_nums2 = OperationDB.readBugNumsAccordCondition({'iteration': id, 'status': '已解决','type_owner':'offline'})
        off_closed_nums3 = OperationDB.readBugNumsAccordCondition({'iteration': id, 'status': 'closed','type_owner':'offline'})
        off_closed_nums = off_closed_nums1 + off_closed_nums2 + off_closed_nums3
        on_created_nums = OperationDB.readBugNumsAccordCondition({'iteration': id,'type_owner':'online'})
        on_closed_nums1 = OperationDB.readBugNumsAccordCondition({'iteration': id, 'status': '已关闭','type_owner':'online'})
        on_closed_nums2 = OperationDB.readBugNumsAccordCondition({'iteration': id, 'status': '已解决','type_owner':'online'})
        on_closed_nums3 = OperationDB.readBugNumsAccordCondition({'iteration': id, 'status': 'closed','type_owner':'online'})
        on_closed_nums = on_closed_nums1 + on_closed_nums2 + on_closed_nums3
        if useto.lower() == 'pic':
            if type == 'offline':
                yattr['off_created_nums'].append(off_created_nums)
                yattr['off_closed_nums'].append(off_closed_nums)
                if off_created_nums <= 0:
                    yattr['off_percent_nums'].append("100")
                else:
                    yattr['off_percent_nums'].append(float("{:.2f}".format(int(off_closed_nums) / int(off_created_nums) * 100)))
            elif type == 'online':
                yattr['on_created_nums'].append(on_created_nums)
                yattr['on_closed_nums'].append(on_closed_nums)
                if on_created_nums <= 0:
                    yattr['on_percent_nums'].append("100")
                else:
                    yattr['on_percent_nums'].append(float("{:.2f}".format(int(on_closed_nums) / int(on_created_nums) * 100)))
            else:
                yattr['off_created_nums'].append(off_created_nums)
                yattr['off_closed_nums'].append(off_closed_nums)
                if off_created_nums <= 0:
                    yattr['off_percent_nums'].append("100")
                else:
                    yattr['off_percent_nums'].append(float("{:.2f}".format(int(off_closed_nums) / int(off_created_nums) * 100)))
                yattr['on_created_nums'].append(on_created_nums)
                yattr['on_closed_nums'].append(on_closed_nums)
                if on_created_nums <= 0:
                    yattr['on_percent_nums'].append("100")
                else:
                    yattr['on_percent_nums'].append(float("{:.2f}".format(int(on_closed_nums) / int(on_created_nums) * 100)))
        else:
            if type == 'offline':
                off_created_dict['itera%s' % i] = off_created_nums
                off_closed_dict['itera%s' % i] = off_closed_nums
                if int(off_created_nums) <= 0:
                    off_percent_dict['itera%s' % i] = "100%"
                else:
                    off_percent_dict['itera%s' % i] = "{:.2f}%".format((int(off_closed_nums) / int(off_created_nums)) * 100)
            elif type == 'online':
                on_created_dict['itera%s' % i] = on_created_nums
                on_closed_dict['itera%s' % i] = on_closed_nums
                if int(on_created_nums) <= 0:
                    on_percent_dict['itera%s' % i] = "100%"
                else:
                    on_percent_dict['itera%s' % i] = "{:.2f}%".format((int(on_closed_nums) / int(on_created_nums)) * 100)
            else:
                off_created_dict['itera%s' % i] = off_created_nums
                off_closed_dict['itera%s' % i] = off_closed_nums
                if int(off_created_nums) <= 0:
                    off_percent_dict['itera%s' % i] = "100%"
                else:
                    off_percent_dict['itera%s' % i] = "{:.2f}%".format((int(off_closed_nums) / int(off_created_nums)) * 100)
                on_created_dict['itera%s' % i] = on_created_nums
                on_closed_dict['itera%s' % i] = on_closed_nums
                if int(on_created_nums) <= 0:
                    on_percent_dict['itera%s' % i] = "100%"
                else:
                    on_percent_dict['itera%s' % i] = "{:.2f}%".format((int(on_closed_nums) / int(on_created_nums)) * 100)
        versions.append(['itera%s' % i, version])
        i += 1
    if useto.lower() == 'pic':
        lines = Line(init_opts=opts.InitOpts(width="1000px",height="330px"))
        lines.add_xaxis(xattr)
        if type == 'offline':
            lines.add_yaxis('迭代新增bug', yattr['off_created_nums'])
            lines.add_yaxis('迭代解决bug', yattr['off_closed_nums'])
        elif type == 'online':
            lines.add_yaxis('线上新增bug', yattr['on_created_nums'])
            lines.add_yaxis('线上解决bug', yattr['on_closed_nums'])
        else:
            lines.add_yaxis('迭代新增bug', yattr['off_created_nums'])
            lines.add_yaxis('迭代解决bug', yattr['off_closed_nums'])
            lines.add_yaxis('线上新增bug', yattr['on_created_nums'])
            lines.add_yaxis('线上解决bug', yattr['on_closed_nums'])
        return lines,versions
    else:
        if type == 'offline':
            data = [off_created_dict,off_closed_dict,off_percent_dict]
        elif type == 'online':
            data = [on_created_dict,on_closed_dict,on_percent_dict]
        else:
            data = [off_created_dict,off_closed_dict,off_percent_dict,on_created_dict,on_closed_dict,on_percent_dict]
        return data,versions

def bugBar_mudle(versionname,programname='V2',type='offline',useto='pic'):
    '''缺陷模块统计、柱状图
        programname: 项目名称
        type： 线上、线下、全部   offline/online/all
        useto: 用途：画图、统计  pic/data
        versionID: 迭代版本id
    '''
    programs,countss = OperationDB.getProgram(programname)
    if programname != None and programname != '' and programs == []:
        if useto=='pic':
            bars = Bar(init_opts=opts.InitOpts(width="1100px", height="330px"))
            return bars,[]
        else:
            return [],[]
    progrm_id = programs.id
    iteration,icount = OperationDB.get_iteration(progrm_id,version=versionname)
    if icount == 0:
        if useto=='pic':
            bars = Bar(init_opts=opts.InitOpts(width="1100px", height="330px"))
            return bars,[]
        else:
            return [],[]
    iteration_id = iteration.id
    module_fields = []
    modules = []
    off_created_dict = {'type': "迭代新增", "module1": 3}
    off_closed_dict = {'type': "迭代解决", "module1": 2}
    on_created_dict = {'type': "线上新增", "module1": 3}
    on_closed_dict = {'type': "线上解决", "module1": 2}
    yattr = {
        'off_created_nums':[],
        'off_closed_nums':[],
        'on_created_nums':[],
        'on_closed_nums':[],
    }
    all_dict = {}
    all_bugs,all_count = OperationDB.readBugsFromDB(limit=9999,condition={'iteration': iteration_id})
    i = 1
    for bug in all_bugs:
        offon = bug['type_owner']
        status = bug['status']
        modulename = bug['bug_moudle']
        if modulename == '' or modulename == None or modulename == 'null'  or modulename == 'Null':
            modulename = '其他'
        #初始化模块分类地字典
        if modulename not in all_dict.keys():
            all_dict[modulename] = {
                'off_created_nums': 0,
                'off_closed_nums': 0,
                'on_created_nums': 0,
                'on_closed_nums': 0,
            }
        # 模块分类后 bug计数
        if offon == 'offline':
            all_dict[modulename]['off_created_nums'] += 1
            if status == '已关闭' or status == '已解决' or status == 'closed':
                all_dict[modulename]['off_closed_nums'] += 1
        else:
            all_dict[modulename]['on_created_nums'] += 1
            if status == '已关闭' or status == '已解决' or status == 'closed':
                all_dict[modulename]['on_closed_nums'] += 1
    for m,numsdict in all_dict.items():
        module_fields.append(['module%s' % i, m])
        modules.append(m)
        if useto.lower() == 'pic':
            if type == 'offline':
                yattr['off_created_nums'].append(numsdict['off_created_nums'])
                yattr['off_closed_nums'].append(numsdict['off_closed_nums'])
            elif type == 'online':
                yattr['on_created_nums'].append(numsdict['on_created_nums'])
                yattr['on_closed_nums'].append(numsdict['on_closed_nums'])
            else:
                yattr['off_created_nums'].append(numsdict['off_created_nums'])
                yattr['off_closed_nums'].append(numsdict['off_closed_nums'])
                yattr['on_created_nums'].append(numsdict['on_created_nums'])
                yattr['on_closed_nums'].append(numsdict['on_closed_nums'])
        else:
            if type == 'offline':
                off_created_dict['module%s' % i] = numsdict['off_created_nums']
                off_closed_dict['module%s' % i] = numsdict['off_closed_nums']
            elif type == 'online':
                on_created_dict['module%s' % i] = numsdict['on_created_nums']
                on_closed_dict['module%s' % i] = numsdict['on_closed_nums']
            else:
                off_created_dict['module%s' % i] = numsdict['off_created_nums']
                off_closed_dict['module%s' % i] = numsdict['off_closed_nums']
                on_created_dict['module%s' % i] = numsdict['on_created_nums']
                on_closed_dict['module%s' % i] = numsdict['on_closed_nums']
        i += 1
    if useto.lower() == 'pic':
        bars = Bar(init_opts=opts.InitOpts(width="1100px",height="330px"))
        bars.add_xaxis(modules)
        if type == 'offline':
            bars.add_yaxis('迭代新增', yattr['off_created_nums'])
            bars.add_yaxis('迭代解决', yattr['off_closed_nums'])
        elif type == 'online':
            bars.add_yaxis('线上新增', yattr['on_created_nums'])
            bars.add_yaxis('线上解决', yattr['on_closed_nums'])
        else:
            bars.add_yaxis('迭代新增', yattr['off_created_nums'])
            bars.add_yaxis('迭代解决', yattr['off_closed_nums'])
            bars.add_yaxis('线上新增', yattr['on_created_nums'])
            bars.add_yaxis('线上解决', yattr['on_closed_nums'])
        return bars,module_fields
    else:
        if type == 'offline':
            data = [off_created_dict,off_closed_dict]
        elif type == 'online':
            data = [on_created_dict,on_closed_dict]
        else:
            data = [off_created_dict,off_closed_dict,on_created_dict,on_closed_dict]
        return data,module_fields

def bugBar_total(programname='V2',type='offline',useto='pic'):
    '''总体缺陷统计、柱状图
        programname: 项目名称
        type： 线上、线下、全部   offline/online/all
        useto: 用途：画图、统计  pic/data
    '''
    programs,countss = OperationDB.getProgram(programname)
    if programname != None and programname != '' and programname != '所有' and programs == []:
        if useto=='pic':
            bars = Bar(init_opts=opts.InitOpts(width="1100px", height="330px"))
            return bars,[]
        else:
            return [],[]
    if programname == '所有':
        old_bugs, old_count = OperationDB.readSonProgramCount()
        total_dict = {}
        for one_line in old_bugs:
            f_id = str(one_line['parent_program_id'])
            f_info = OperationDB.getProgramCondition({"id":f_id})
            f_name = f_info[0].name
            if f_id in total_dict.keys():
                total_dict[f_id]['offline_total_no'] += int(one_line['offline_total_no'])
                total_dict[f_id]['offline_resloved_no'] += int(one_line['offline_resloved_no'])
                total_dict[f_id]['online_total_no'] += int(one_line['online_total_no'])
                total_dict[f_id]['online_resloved_no'] += int(one_line['online_resloved_no'])
            else:
                total_dict[f_id] = {
                    'offline_total_no':int(one_line['offline_total_no']),
                    'offline_resloved_no':int(one_line['offline_resloved_no']),
                    'online_total_no':int(one_line['online_total_no']),
                    'online_resloved_no':int(one_line['online_resloved_no']),
                    'name':f_name,
                }
        all_bugs = []
        all_count = 0
        for key,one_dict in total_dict.items():
            all_bugs.append(one_dict)
            all_count += 1
    else:
        progrm_id = programs.id
        all_bugs, all_count = OperationDB.readSonProgramCount({"parent_program_id":progrm_id})

    module_fields = []
    modules = []
    off_created_dict = {'type': "迭代总计新增", "module1": 3}
    off_closed_dict = {'type': "迭代总计解决", "module1": 2}
    off_percent_dict = {'type': "迭代解决率", "module1": "50%"}
    on_created_dict = {'type': "线上总计新增", "module1": 3}
    on_closed_dict = {'type': "线上总计解决", "module1": 2}
    on_percent_dict = {'type': "线上解决率", "module1": "50%"}
    yattr = {
        'off_created_nums':[],
        'off_closed_nums':[],
        'off_percent_nums':[],
        'on_created_nums':[],
        'on_closed_nums':[],
        'on_percent_nums':[],
    }
    i = 1
    data = []
    for bug in all_bugs:
        modules.append(bug['name'])
        modulename = 'module%s' % i
        module_fields.append([modulename, bug['name']])
        if useto.lower() == 'pic':
            yattr['off_created_nums'].append(bug['offline_total_no'])
            yattr['off_closed_nums'].append(bug['offline_resloved_no'])
            if int(bug['offline_total_no']) <= 0:
                yattr['off_percent_nums'].append("100")
            else:
                yattr['off_percent_nums'].append(float("{:.2f}".format(int(bug['offline_resloved_no']) / int(bug['offline_total_no']) * 100)))
            yattr['on_created_nums'].append(bug['online_total_no'])
            yattr['on_closed_nums'].append(bug['online_resloved_no'])
            if int(bug['online_total_no']) <= 0:
                yattr['on_percent_nums'].append("100")
            else:
                yattr['on_percent_nums'].append(float("{:.2f}".format(int(bug['online_resloved_no']) / int(bug['online_total_no']) * 100)))
        else:
            off_created_dict[modulename] = bug['offline_total_no']
            off_closed_dict[modulename] = bug['offline_resloved_no']
            if int(bug['offline_total_no']) <= 0:
                off_percent_dict[modulename] = "100%"
            else:
                off_percent_dict[modulename] = "{:.2f}%".format(int(bug['offline_resloved_no']) / int(bug['offline_total_no']) * 100)
            on_created_dict[modulename] = bug['online_total_no']
            on_closed_dict[modulename] = bug['online_resloved_no']
            if int(bug['online_total_no']) <= 0:
                on_percent_dict[modulename] = "100%"
            else:
                on_percent_dict[modulename] = "{:.2f}%".format(int(bug['online_resloved_no']) / int(bug['online_total_no']) * 100)
        i += 1
    if useto.lower() == 'pic':
        bar1 = Bar(init_opts=opts.InitOpts(width="1500px",height="330px"))
        bar1.add_xaxis(modules)
        bar1.set_global_opts(
            title_opts=opts.TitleOpts(title="缺陷总体情况",pos_top="5%",pos_left="5%"),
            legend_opts=opts.LegendOpts(type_="scroll",pos_right="1%",pos_top="10%",orient="vertical")
        )
        bar2 = Bar(init_opts=opts.InitOpts(width="1500px", height="330px",))
        bar2.add_xaxis(modules)
        bar2.set_global_opts(
            title_opts=opts.TitleOpts(title="缺陷总体解决率",pos_bottom="47%",pos_left="5%"),
            legend_opts=opts.LegendOpts(type_="scroll",pos_right="2%",pos_bottom="42%",orient="vertical"),
            yaxis_opts = opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value} %"), interval=10)
        )
        if type == 'offline':
            bar1.add_yaxis('迭代总计新增', yattr['off_created_nums'])
            bar1.add_yaxis('迭代总计解决', yattr['off_closed_nums'])
            bar2.add_yaxis('迭代解决率', yattr['off_percent_nums'], label_opts=opts.LabelOpts(formatter="{c} %"))
        elif type == 'online':
            bar1.add_yaxis('线上总计新增', yattr['on_created_nums'])
            bar1.add_yaxis('线上总计解决', yattr['on_closed_nums'])
            bar2.add_yaxis('线上解决率', yattr['on_percent_nums'], label_opts=opts.LabelOpts(formatter="{c} %"))
        else:
            bar1.add_yaxis('迭代总计新增', yattr['off_created_nums'])
            bar1.add_yaxis('迭代总计解决', yattr['off_closed_nums'])
            bar1.add_yaxis('线上总计新增', yattr['on_created_nums'])
            bar1.add_yaxis('线上总计解决', yattr['on_closed_nums'])
            bar2.add_yaxis('迭代解决率', yattr['off_percent_nums'], label_opts=opts.LabelOpts(formatter="{c} %"))
            bar2.add_yaxis('线上解决率', yattr['on_percent_nums'], label_opts=opts.LabelOpts(formatter="{c} %"))
        bars = Grid(init_opts=opts.InitOpts(width="1300px",height="440px"))
        bars.add(bar1, grid_opts=opts.GridOpts(pos_bottom="56%"))
        bars.add(bar2, grid_opts=opts.GridOpts(pos_top="56%"))
        bars.render_notebook()
        return bars,module_fields
    else:
        if type == 'offline':
            data = [off_created_dict,off_closed_dict,off_percent_dict]
        elif type == 'online':
            data = [on_created_dict,on_closed_dict,on_percent_dict]
        else:
            data = [off_created_dict,off_closed_dict,off_percent_dict,on_created_dict,on_closed_dict,on_percent_dict]
        return data, module_fields

def CombiningData_developer(iteration_id,son_program_ids):
    '''组合生产人员相关数据，用于图表呈现'''
    all_dict = {}
    # 根据表bug_detail获取bug相关情况
    all_bugs, all_count = OperationDB.readBugsFromDB(limit=9999, condition={'iteration': iteration_id})
    for bug in all_bugs:
        offon = bug['type_owner']
        status = bug['status']
        bug_owner = bug['bug_owner']
        if bug_owner == '' or bug_owner == None or bug_owner == 'null'  or bug_owner == 'Null':
            bug_owner = '其他'

        #初始化模块分类地字典
        if bug_owner not in all_dict.keys():
            all_dict[bug_owner] = {
                'off_created_nums': 0,
                'off_closed_nums': 0,
                'on_created_nums': 0,
                'on_closed_nums': 0
            }

        # 模块分类后 bug计数
        if offon == 'offline':
            all_dict[bug_owner]['off_created_nums'] += 1
            if status == '已关闭' or status == '已解决' or status == 'closed':
                all_dict[bug_owner]['off_closed_nums'] += 1
        else:
            all_dict[bug_owner]['on_created_nums'] += 1
            if status == '已关闭' or status == '已解决' or status == 'closed':
                all_dict[bug_owner]['on_closed_nums'] += 1


    # 根据表bug_developdetail获取开发人员相关情况
    developer_runInfo = OperationDB.readDeveloperInfoAccordIterationID(iteration_id,son_program_ids)

    # 全局系数比
    whole_rate = readTargetRate({'type': 'whole'}) if readTargetRate({'type': 'whole'}) is not None else 10  # 整体系数比，默认10

    all_names = set(list(all_dict.keys()) + list(developer_runInfo.keys()))
    for name in all_names:
        if name not in all_dict.keys():
            all_dict[name] = {
                'off_created_nums': 0,
                'off_closed_nums': 0,
                'on_created_nums': 0,
                'on_closed_nums': 0
            }
        if name not in developer_runInfo.keys():
            all_dict[name]['delayTestTimes_nums'] = 0
            all_dict[name]['failedSmokeCount_nums'] = 0
            all_dict[name]['reopenBugCount_nums'] = 0
            all_dict[name]['ProgramScores_nums'] = 0
            all_dict[name]['TechScores_nums'] = 0

        else:
            curOne = developer_runInfo[name]
            all_dict[name]['delayTestTimes_nums'] = int(curOne.delayTestTimes) if curOne.delayTestTimes != '' and curOne.delayTestTimes != None else 0
            all_dict[name]['failedSmokeCount_nums'] = int(curOne.failedSmokeCount) if curOne.failedSmokeCount != '' and curOne.failedSmokeCount != None else 0
            all_dict[name]['reopenBugCount_nums'] = int(curOne.reopenBugCount) if curOne.reopenBugCount != '' and curOne.reopenBugCount != None else 0
            all_dict[name]['ProgramScores_nums'] = float(curOne.ProgramScores) if curOne.ProgramScores != '' and curOne.ProgramScores != None else 0
            all_dict[name]['TechScores_nums'] = float(curOne.TechScores) if curOne.TechScores != '' and curOne.TechScores != None else 0

        #  解决率
        if all_dict[name]['off_created_nums'] != 0:
            all_dict[name]['off_percent_nums'] = float("{:.2f}".format(all_dict[name]['off_closed_nums'] / all_dict[name]['off_created_nums'] * 100))
        else:
            all_dict[name]['off_percent_nums'] = float("{:.2f}".format(100))
        # 线上解决率
        if all_dict[name]['on_created_nums'] != 0:
            all_dict[name]['on_percent_nums'] = float("{:.2f}".format(all_dict[name]['on_closed_nums'] / all_dict[name]['on_created_nums'] * 100))
        else:
            all_dict[name]['on_percent_nums'] = float("{:.2f}".format(100))

        # 综合评分，公式=基础总分 - 扣分项  （基础总分=（60% * 技术主管评分 + 40% * 项目主管评分） * 系数比；扣分项：迭代bug、线上bug、解决率、提测延期、冒烟失败、reopen缺陷次数）
        all_dict[name]['TotalScores_nums'] = 0
        # 计算基础总分
        # base_sores = (all_dict[name]['TechScores_nums'] * 0.6 + all_dict[name]['ProgramScores_nums'] * 0.4) * whole_rate # 主管评价：基础总分 = (60% * 技术主管评分 + 40% * 项目主管评分） * 系数比10
        base_sores = (all_dict[name]['TechScores_nums'] + all_dict[name]['ProgramScores_nums']) * whole_rate # 工作量+贡献评价法：基础总分 = (特殊贡献加分 + 工作量基础分） * 系数比10
        minus_sore1 = all_dict[name]['off_created_nums'] * 0.2  #扣分项1, 迭代内部bug扣分= 0.2 * bug个数
        minus_sore2 = all_dict[name]['on_created_nums'] * 2  #扣分项2, 线上bug扣分= 2 * bug个数
        minus_sore3 = all_dict[name]['delayTestTimes_nums']/4 * 0.5  #扣分项3, 提测延期扣分= 0.5 * N/4（每半天开始计算，总延迟时间 N/4h）
        minus_sore4 = all_dict[name]['failedSmokeCount_nums'] * 2  #扣分项4, 冒烟不通过扣分= 0.5 * 冒烟不通过次数
        minus_sore5 = all_dict[name]['reopenBugCount_nums'] * 2  #扣分项5, 缺陷reopen扣分= 0.5 * bug reopen次数
        minus_sore6 = 0
        # 产生bug数<=10: 解决率<90% -1；解决率<80% -3
        # 产生bug数<=20: 解决率<80% -1；解决率<70% -3
        # 产生bug数<=30: 解决率<70% -1；解决率<60% -3
        # 产生bug数>30: 解决率<60% -1；解决率<50% -3
        total_created_nums = all_dict[name]['off_created_nums'] + all_dict[name]['on_created_nums']
        total_closed_nums = all_dict[name]['off_closed_nums'] + all_dict[name]['on_closed_nums']
        bili = total_closed_nums/total_created_nums if total_created_nums!=0 else 1
        if total_created_nums < 10:
            if bili < 0.8:
                minus_sore6 = 3
            elif 0.8 <= bili < 0.9:
                minus_sore6 = 1
            else:
                minus_sore6 = 0
        elif 10 < total_created_nums <= 20:
            if bili < 0.7:
                minus_sore6 = 3
            elif 0.7 <= bili < 0.8:
                minus_sore6 = 1
            else:
                minus_sore6 = 0
        elif 20 < total_created_nums <= 30:
            if bili < 0.6:
                minus_sore6 = 3
            elif 0.6 <= bili < 0.7:
                minus_sore6 = 1
            else:
                minus_sore6 = 0
        else:
            if bili < 0.5:
                minus_sore6 = 3
            elif 0.5 <= bili < 0.6:
                minus_sore6 = 1
            else:
                minus_sore6 = 0
        # 综合评分 （基础分*系数比 - 扣分） /系数比
        minus_total = minus_sore1 + minus_sore2 + minus_sore3 + minus_sore4 + minus_sore5 + minus_sore6
        all_dict[name]['minusScores_nums'] = float("{:.2f}".format(minus_total / whole_rate))
        end_num = (base_sores - minus_total) / whole_rate
        all_dict[name]['TotalScores_nums'] = float("{:.2f}".format(end_num))
    return all_dict

def bugBar_developer(versionname,programname='V2',type='all',useto='pic'):
    '''研发质量统计、柱状图
        programname: 项目名称
        type： 线上、线下、全部   offline/online/all
        useto: 用途：画图、统计  pic/data
        versionID: 迭代版本id
    '''
    programs, countss = OperationDB.getProgram(programname)
    progrm_id = programs.id
    son_programs = TC_Programs[programname]
    son_program_ids = []

    for son_program in son_programs:
        son_ps,son_countss = OperationDB.getSonProgram(son_program)
        try:
            son_progrm_id = son_ps[0].id
            son_program_ids.append(son_progrm_id)
        except:
            pass
    if programname != None and programname != '' and programs == []:
        if useto=='pic':
            bars = Bar(init_opts=opts.InitOpts(width="1100px", height="330px"))
            return bars,[]
        else:
            return [],[]
    iteration,icount = OperationDB.get_iteration(progrm_id,version=versionname)
    if icount == 0:
        if useto=='pic':
            bars = Bar(init_opts=opts.InitOpts(width="1100px", height="330px"))
            return bars,[]
        else:
            return [],[]
    iteration_id = iteration.id
    # 定义title和all_dict中key的对应关系
    title_key_tuple = (
        ('迭代新增缺陷', 'off_created_nums'),
        ('迭代解决缺陷', 'off_closed_nums'),
        ('线上新增缺陷', 'on_created_nums'),
        ('线上解决缺陷', 'on_closed_nums'),
        ('缺陷reopen次数', 'reopenBugCount_nums'),
        ('迭代缺陷解决率', 'off_percent_nums'),
        ('线上缺陷解决率', 'on_percent_nums'),
        ('提测延期时间', 'delayTestTimes_nums'),
        ('冒烟失败次数', 'failedSmokeCount_nums'),
        ('项目主管评分', 'ProgramScores_nums'),
        ('技术主管评分', 'TechScores_nums'),
        ('质量扣分', 'minusScores_nums'),
        ('综合评分', 'TotalScores_nums')
    )
    # 获取 测试人员执行相关完整信息
    all_dict = CombiningData_developer(iteration_id,son_program_ids)
    # 分别拼装 前端列表 和 图表所有 数据
    yattrORtable, modules, module_fields = CombiningTableDataAndPicData(title_key_tuple, all_dict, useto)
    # 画图 或 集合数据列表
    if useto.lower() == 'pic':
        # 缺陷 & 测试记录
        bar1 = Bar(init_opts=opts.InitOpts(width="360px",height="330px"))
        bar1.add_xaxis(modules)
        if type == 'bug':
            bar1.set_global_opts(
                title_opts=opts.TitleOpts(title="缺陷情况", pos_top="2%", pos_left="5%"),
                legend_opts=opts.LegendOpts(type_="scroll", pos_top="2%", orient="horizontal"),
            )
        else:
            bar1.set_global_opts(
                title_opts=opts.TitleOpts(title="缺陷情况", pos_top="3%", pos_left="1%"),
                legend_opts=opts.LegendOpts(type_="scroll", pos_right="50%", pos_top="8%", orient="vertical"),
            )
        for title, key in title_key_tuple[:5]:
            bar1.add_yaxis(title, yattrORtable[key])
        # 解决率
        bar2 = Bar(init_opts=opts.InitOpts(width="1100px", height="330px"))
        bar2.add_xaxis(modules)
        if type == 'rate':
            bar2.set_global_opts(
                title_opts=opts.TitleOpts(title="解决率", pos_top="2%", pos_left="5%"),
                legend_opts=opts.LegendOpts(type_="scroll", pos_top="2%", orient="horizontal"),
                yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value} %"), interval=10)
            )
        else:
            bar2.set_global_opts(
                title_opts=opts.TitleOpts(title="解决率", pos_top="3%", pos_left="50%"),
                legend_opts=opts.LegendOpts(type_="scroll", pos_right="1%", pos_top="8%", orient="vertical"),
                yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value} %"), interval=10)
            )
        for title, key in title_key_tuple[5:7]:
            bar2.add_yaxis(title, yattrORtable[key], label_opts=opts.LabelOpts(formatter="{c} %"))
        # 主管评分
        bar3 = Bar(init_opts=opts.InitOpts(width="550px", height="330px"))
        bar3.add_xaxis(modules)
        if type == 'ctest':
            bar3.set_global_opts(
                title_opts=opts.TitleOpts(title="提测情况", pos_top="2%", pos_left="5%"),
                legend_opts=opts.LegendOpts(type_="scroll", pos_top="2%", orient="horizontal"),
            )
        else:
            bar3.set_global_opts(
                title_opts=opts.TitleOpts(title="提测情况", pos_bottom="48%", pos_left="1%"),
                legend_opts=opts.LegendOpts(type_="scroll", pos_right="50%", pos_top="54%", orient="vertical"),
            )
        for title, key in title_key_tuple[7:9]:
            bar3.add_yaxis(title, yattrORtable[key])
        # 综合评分
        bar4 = Bar(init_opts=opts.InitOpts(width="1100px", height="330px"))
        bar4.add_xaxis(modules)
        if type == 'scores':
            bar4.set_global_opts(
                title_opts=opts.TitleOpts(title="质量扣分", pos_top="2%", pos_left="5%"),
                legend_opts=opts.LegendOpts(type_="scroll", pos_top="2%", orient="horizontal"),
            )
        else:
            bar4.set_global_opts(
                title_opts=opts.TitleOpts(title="质量扣分", pos_bottom="48%", pos_left="50%"),
                legend_opts=opts.LegendOpts(type_="scroll", pos_right="3%", pos_top="54%", orient="vertical"),
            )
        for title, key in title_key_tuple[11:12]:
            bar4.add_yaxis(title, yattrORtable[key])
        #
        # # 综合评分
        # bar4 = Bar(init_opts=opts.InitOpts(width="1100px", height="330px"))
        # bar4.add_xaxis(modules)
        # if type == 'totalscores':
        #     bar4.set_global_opts(
        #         title_opts=opts.TitleOpts(title="综合评分", pos_top="2%", pos_left="5%"),
        #         legend_opts=opts.LegendOpts(type_="scroll", pos_top="2%", orient="horizontal"),
        #     )
        # else:
        #     bar4.set_global_opts(
        #         title_opts=opts.TitleOpts(title="综合评分", pos_bottom="48%", pos_left="50%"),
        #         legend_opts=opts.LegendOpts(type_="scroll", pos_right="3%", pos_top="54%", orient="vertical"),
        #     )
        # for title, key in title_key_tuple[12:]:
        #     bar4.add_yaxis(title, yattrORtable[key])

        # 组合成整个画板
        # bars = Grid(init_opts=opts.InitOpts(theme=ThemeType.DARK,width="1300px", height="660px"))
        bars = Grid(init_opts=opts.InitOpts(width="1300px", height="660px"))
        if type == 'bug':
            bars.add(bar1, grid_opts=opts.GridOpts(pos_top="10%", pos_bottom="50%", pos_right="10%", pos_left="8%"))
        elif type == 'rate':
            bars.add(bar2, grid_opts=opts.GridOpts(pos_top="10%", pos_bottom="50%", pos_right="10%", pos_left="8%"))
        elif type == 'ctest':
            bars.add(bar3, grid_opts=opts.GridOpts(pos_top="10%", pos_bottom="50%", pos_right="10%", pos_left="8%"))
        elif type == 'scores':
            bars.add(bar4, grid_opts=opts.GridOpts(pos_top="10%", pos_bottom="50%", pos_right="10%", pos_left="8%"))
        elif type == 'totalscores':
            bars.add(bar4, grid_opts=opts.GridOpts(pos_top="10%", pos_bottom="50%", pos_right="10%", pos_left="8%"))
        else:
            bars.add(bar1, grid_opts=opts.GridOpts(pos_bottom="60%", pos_right="60%",pos_left="3%"))
            bars.add(bar2, grid_opts=opts.GridOpts(pos_bottom="60%", pos_left="53%"))
            bars.add(bar3, grid_opts=opts.GridOpts(pos_top="54%", pos_right="60%", pos_left="4%"))
            bars.add(bar4, grid_opts=opts.GridOpts(pos_top="54%", pos_left="53%"))
        bars.render_notebook()
        return bars,module_fields
    else:
        data = []
        for title, key in title_key_tuple:
            data.append(yattrORtable[key])
        return data,module_fields

def CombiningData_tester(iteration_id,son_program_ids):
    '''组合测试人员相关数据，用于图表呈现'''
    all_dict = {}
    # 根据表bug_detail获取bug相关情况
    all_bugs, all_count = OperationDB.readBugsFromDB(limit=9999, condition={'iteration': iteration_id})
    for bug in all_bugs:
        offon = bug['type_owner']
        status = bug['status']
        bug_creater = bug['bug_creater']
        if bug_creater == '' or bug_creater == None or bug_creater == 'null' or bug_creater == 'Null':
            bug_creater = '其他'
        # 初始化模块分类地字典
        if bug_creater not in all_dict.keys():
            all_dict[bug_creater] = {
                'off_created_nums': 0,
                'off_closed_nums': 0,
                'on_created_nums': 0,
                'on_closed_nums': 0,
                'lost_BugCount_nums': 0,
                'reviewCasesCount_nums': 0,
                'createdCasesCount_nums': 0,
                'passReviewCount_nums': 0,
                'failedReviewCount_nums': 0,
                'notReviewCount_nums': 0,
                'passRunCount_nums': 0,
                'failedRunCount_nums': 0,
                'blockedRunCount_nums': 0,
                'notRunCount_nums': 0,
                'case_ReviewRate_nums': 0,
                'case_RunRate_nums': 0,
                'case_PassRate_nums': 0,
                'case_ValuableRate_nums': 0,
                'case_BugRate_nums': 0,
                'bug_DetectionRate_nums': 0,
                'lost_BugRate_nums': 0
            }
        # 模块分类后 bug计数
        if offon == 'offline':
            all_dict[bug_creater]['off_created_nums'] += 1
            if status == '已关闭' or status == '已解决' or status == 'closed':
                all_dict[bug_creater]['off_closed_nums'] += 1
        else:
            all_dict[bug_creater]['on_created_nums'] += 1
            if status == '已关闭' or status == '已解决' or status == 'closed':
                all_dict[bug_creater]['on_closed_nums'] += 1
    # 根据表bug_testdetail获取测试人员执行相关情况
    testers_runInfo = OperationDB.readTesterRunInfoAccordIterationID(iteration_id,son_program_ids)

    # 将“其他”人的数据 均分给每一个人的分母  同时增加其他人这列
    other_cur_totalcases_count = 0
    if "其他" in testers_runInfo.keys() and "其他" not in all_dict.keys():
        g_u_count = len(testers_runInfo.keys()) - 1 if len(testers_runInfo.keys()) >= 2 else 1
        other = testers_runInfo["其他"]
        other_passRunCount = int(other.passRunCount) / g_u_count
        other_failedRunCount = int(other.failedRunCount) / g_u_count
        other_blockedRunCount = int(other.blockedRunCount) / g_u_count
        other_notRunCount = int(other.notRunCount) / g_u_count
        other_cur_totalcases_count = other_passRunCount + other_failedRunCount + other_blockedRunCount + other_notRunCount

    # 全局系数比
    whole_rate = readTargetRate({'type': 'whole'}) if readTargetRate({'type': 'whole'}) is not None else 10 # 整体系数比，默认10

    all_names = set(list(all_dict.keys()) + list(testers_runInfo.keys()))
    for name in all_names:
        if name not in all_dict.keys():
            all_dict[name] = {
                'off_created_nums': 0,
                'off_closed_nums': 0,
                'on_created_nums': 0,
                'on_closed_nums': 0
            }
        if name not in testers_runInfo.keys():
            all_dict[name]['lost_BugCount_nums'] = 0
            all_dict[name]['passRunCount_nums'] = 0
            all_dict[name]['failedRunCount_nums'] = 0
            all_dict[name]['blockedRunCount_nums'] = 0
            all_dict[name]['notRunCount_nums'] = 0
            all_dict[name]['reviewCasesCount_nums'] = 0
            all_dict[name]['createdCasesCount_nums'] = 0
            all_dict[name]['passReviewCount_nums'] = 0
            all_dict[name]['failedReviewCount_nums'] = 0
            all_dict[name]['notReviewCount_nums'] = 0
            all_dict[name]['testDelayTime_nums'] = 0
            all_dict[name]['autoFinishRate_nums'] = 0
            all_dict[name]['TechScores_nums'] = 0
            all_dict[name]['ProgramScores_nums'] = 0
            all_dict[name]['minusScores_nums'] = 0
        else:
            curOne = testers_runInfo[name]
            all_dict[name]['lost_BugCount_nums'] = int(curOne.lost_BugCount) if curOne.lost_BugCount != '' and curOne.lost_BugCount != None else 0
            all_dict[name]['passRunCount_nums'] = int(curOne.passRunCount) if curOne.passRunCount != '' and curOne.passRunCount != None else 0
            all_dict[name]['failedRunCount_nums'] = int(curOne.failedRunCount) if curOne.failedRunCount != '' and curOne.failedRunCount != None else 0
            all_dict[name]['blockedRunCount_nums'] = int(curOne.blockedRunCount) if curOne.blockedRunCount != '' and curOne.blockedRunCount != None else 0
            all_dict[name]['notRunCount_nums'] = int(curOne.notRunCount) if curOne.notRunCount != '' and curOne.notRunCount != None else 0
            all_dict[name]['reviewCasesCount_nums'] = int(curOne.reviewCasesCount) if curOne.reviewCasesCount != '' and curOne.reviewCasesCount != None else 0
            all_dict[name]['createdCasesCount_nums'] = int(curOne.createdCasesCount) if curOne.createdCasesCount != '' and curOne.createdCasesCount != None else 0
            all_dict[name]['passReviewCount_nums'] = int(curOne.passReviewCount) if curOne.passReviewCount != '' and curOne.passReviewCount != None else 0
            all_dict[name]['failedReviewCount_nums'] = int(curOne.failedReviewCount) if curOne.failedReviewCount != '' and curOne.failedReviewCount != None else 0
            all_dict[name]['notReviewCount_nums'] = int(curOne.notReviewCount) if curOne.notReviewCount != '' and curOne.notReviewCount != None else 0
            all_dict[name]['testDelayTime_nums'] = int(curOne.testDelayTime) if curOne.testDelayTime != '' and curOne.testDelayTime != None else 0
            all_dict[name]['autoFinishRate_nums'] = int(curOne.autoFinishRate) if curOne.autoFinishRate != '' and curOne.autoFinishRate != None else 0
            all_dict[name]['ProgramScores_nums'] = float(curOne.ProgramScores) if curOne.ProgramScores != '' and curOne.ProgramScores != None else 0
            all_dict[name]['TechScores_nums'] = float(curOne.TechScores) if curOne.TechScores != '' and curOne.TechScores != None else 0

        cur_totalreview_count = all_dict[name]['passReviewCount_nums'] + all_dict[name]['failedReviewCount_nums'] + all_dict[name]['notReviewCount_nums']
        # 用例评审通过率
        if cur_totalreview_count != 0:
            all_dict[name]['case_ReviewRate_nums'] = float("{:.2f}".format(all_dict[name]['passReviewCount_nums'] / cur_totalreview_count * 100))
            minus4 = False
        else:
            all_dict[name]['case_ReviewRate_nums'] = float("{:.2f}".format(0))
            minus4 = True

        cur_totalcases_count = all_dict[name]['passRunCount_nums'] + all_dict[name]['failedRunCount_nums'] + all_dict[name]['blockedRunCount_nums'] + all_dict[name]['notRunCount_nums'] + other_cur_totalcases_count
        cur_runcases_count = all_dict[name]['passRunCount_nums'] + all_dict[name]['failedRunCount_nums'] + all_dict[name]['blockedRunCount_nums']

        # 用例执行率
        if cur_totalcases_count != 0:
            all_dict[name]['case_RunRate_nums'] = float("{:.2f}".format(cur_runcases_count / cur_totalcases_count * 100))
            minus5 = False
        else:
            all_dict[name]['case_RunRate_nums'] = float("{:.2f}".format(0))
            minus5 = True

        # 执行通过率
        if cur_runcases_count != 0:
            all_dict[name]['case_PassRate_nums'] = float(
                "{:.2f}".format(all_dict[name]['passRunCount_nums'] / cur_totalcases_count * 100))
        else:
            all_dict[name]['case_PassRate_nums'] = float("{:.2f}".format(100))

        # 高效用例
        if cur_runcases_count != 0:
            all_dict[name]['case_ValuableRate_nums'] = float("{:.2f}".format(all_dict[name]['off_created_nums'] / cur_runcases_count * 100))  # 高效用例价值率 = 新增迭代bug/执行用例数 * 100 %
        else:
            all_dict[name]['case_ValuableRate_nums'] = float("{:.2f}".format(0))  # 高效用例价值率 = 新增迭代bug/执行用例数 * 100 %

        # 用例缺陷匹配率
        comeTotal = all_dict[name]['failedRunCount_nums'] + all_dict[name]['off_created_nums']
        if comeTotal != 0:
            min_num = min([all_dict[name]['failedRunCount_nums'], all_dict[name]['off_created_nums']])
            all_dict[name]['case_BugRate_nums'] = float("{:.2f}".format(min_num / comeTotal * 2 * 100))  # 缺陷用例比 = min_num / ( 新增迭代bug + 失败用例数) * 2 * 100 %
        else:
            all_dict[name]['case_BugRate_nums'] = float("{:.2f}".format(100))  # 用例缺陷匹配率 =  |1 - 新增迭代bug / 失败用例数| * 100 %

        # bug探测率
        total_bug = all_dict[name]['off_created_nums'] + all_dict[name]['on_created_nums']
        totalAndlost_bug = total_bug + all_dict[name]['lost_BugCount_nums']
        if total_bug != 0:
            all_dict[name]['bug_DetectionRate_nums'] = float("{:.2f}".format(all_dict[name]['off_created_nums'] / total_bug * 100))  # bug探测率  线下bug/线上+线下
        else:
            all_dict[name]['bug_DetectionRate_nums'] = float("{:.2f}".format(100))  # bug探测率  线下bug/线上+线下
        if totalAndlost_bug != 0:
            all_dict[name]['lost_BugRate_nums'] = float("{:.2f}".format(all_dict[name]['lost_BugCount_nums'] / totalAndlost_bug * 100))  # 漏测率 漏测bug/ 线上 + 线下 + 漏测
        else:
            all_dict[name]['lost_BugRate_nums'] = float("{:.2f}".format(100))  # 漏测率 漏测bug/ 线上 + 线下 + 漏测

        # 综合评分，公式=基础总分 - 扣分项  （基础总分=（60% * 技术主管评分 + 40% * 项目主管评分） * 系数比；扣分项：线上bug、漏测bug、测试延期、用例评审通过率、用例执行率、自动化达成率）
        all_dict[name]['TotalScores_nums'] = 0
        # 计算基础总分
        # base_sores = (all_dict[name]['TechScores_nums'] * 0.6 + all_dict[name]['ProgramScores_nums'] * 0.4) * whole_rate  # 主管评价法：基础总分 = (60% * 技术主管评分 + 40% * 项目主管评分） * 系数比10
        base_sores = (all_dict[name]['TechScores_nums'] + all_dict[name]['ProgramScores_nums']) * whole_rate  # 工作量+贡献评价法： 基础总分 = (特殊贡献加分 +工作量完成基础分） * 系数比10
        minus_sore1 = all_dict[name]['on_created_nums'] * 2  # 扣分项1, 线上bug扣分= 2 * bug个数
        minus_sore2 = all_dict[name]['lost_BugCount_nums'] * 4  # 扣分项2, 漏测bug扣分= 4 * bug个数
        minus_sore3 = all_dict[name]['testDelayTime_nums']/4 * 0.5  # 扣分项3, 测试完成延期扣分= 0.5 * N/4（每半天开始计算，总延迟时间 N/4h）

        # 扣分项4, 用例评审通过率 <100% -0.5 、>90% -2 、 >80% -3、 >60% -5
        if 90 <= all_dict[name]['case_ReviewRate_nums'] < 100:
            minus_sore4 = 0.5
        elif 80 <= all_dict[name]['case_ReviewRate_nums'] < 90:
            minus_sore4 = 2
        elif 60 <= all_dict[name]['case_ReviewRate_nums'] < 80:
            minus_sore4 = 3
        else:
            minus_sore4 = 5
        if minus4:
            minus_sore4 = 0

        # 扣分项5, 用例执行率 >90% -0.5 、 >70% -2、 >50% -5、 -10
        if 90 <= all_dict[name]['case_ReviewRate_nums'] < 100:
            minus_sore5 = 0.5
        elif 70 <= all_dict[name]['case_ReviewRate_nums'] < 90:
            minus_sore5 = 2
        elif 50 <= all_dict[name]['case_ReviewRate_nums'] < 70:
            minus_sore5 = 5
        else:
            minus_sore5 = 10
        if minus5:
            minus_sore5 = 0

        minus_sore6 = 0
        # # 扣分项6, 自动化达成率 >90% -0.5 、 >70% -1、 >50% -2、 -5   (暂时不启用)
        # if 90 <= all_dict[name]['autoFinishRate_nums'] < 100:
        #     minus_sore6 = 0.5
        # elif 70 <= all_dict[name]['autoFinishRate_nums'] < 90:
        #     minus_sore6 = 1
        # elif 50 <= all_dict[name]['autoFinishRate_nums'] < 70:
        #     minus_sore6 = 2
        # else:
        #     minus_sore6 = 5
        # 综合评分 （基础分*系数比 - 扣分） /系数比
        minus_total = minus_sore1 + minus_sore2 + minus_sore3 + minus_sore4 + minus_sore5 + minus_sore6
        all_dict[name]['minusScores_nums'] = float("{:.2f}".format(minus_total / whole_rate))
        end_num = (base_sores - minus_total) / whole_rate
        all_dict[name]['TotalScores_nums'] = float("{:.2f}".format(end_num))
    return all_dict

def bugBar_tester(versionname,programname='V2',type='all',useto='pic'):
    '''测试质量统计、柱状图
        programname: 项目名称
        type： 线上、线下、全部   offline/online/all
        useto: 用途：画图、统计  pic/data
        versionID: 迭代版本id
    '''
    programs, countss = OperationDB.getProgram(programname)
    progrm_id = programs.id
    son_programs = TC_Programs[programname]
    son_program_ids = []

    for son_program in son_programs:
        son_ps,son_countss = OperationDB.getSonProgram(son_program)
        try:
            son_progrm_id = son_ps[0].id
            son_program_ids.append(son_progrm_id)
        except:
            pass
    if programname != None and programname != '' and programs == []:
        if useto=='pic':
            bars = Bar(init_opts=opts.InitOpts(width="1100px", height="330px"))
            return bars,[]
        else:
            return [],[]
    iteration,icount = OperationDB.get_iteration(progrm_id,version=versionname)
    if icount == 0:
        if useto=='pic':
            bars = Bar(init_opts=opts.InitOpts(width="1100px", height="330px"))
            return bars,[]
        else:
            return [],[]
    iteration_id = iteration.id
    # 定义title和all_dict中key的对应关系
    title_key_tuple = (
        ('迭代提交缺陷', 'off_created_nums'),
        ('迭代验证缺陷', 'off_closed_nums'),
        ('线上提交缺陷', 'on_created_nums'),
        ('线上验证缺陷', 'on_closed_nums'),
        ('漏测缺陷', 'lost_BugCount_nums'),
        ('测试完成延期', 'testDelayTime_nums'),
        ('评审他人用例', 'reviewCasesCount_nums'),
        ('新增用例', 'createdCasesCount_nums'),
        ('评审通过用例', 'passReviewCount_nums'),
        ('评审不通过用例', 'failedReviewCount_nums'),
        ('未评审用例', 'notReviewCount_nums'),
        ('通过用例', 'passRunCount_nums'),
        ('失败用例', 'failedRunCount_nums'),
        ('阻塞用例', 'blockedRunCount_nums'),
        ('未执行用例', 'notRunCount_nums'),
        ('评审通过率', 'case_ReviewRate_nums'),
        ('用例执行率', 'case_RunRate_nums'),
        ('用例通过率', 'case_PassRate_nums'),
        ('高效用例占比', 'case_ValuableRate_nums'),
        ('缺陷用例比', 'case_BugRate_nums'),
        ('缺陷探测率', 'bug_DetectionRate_nums'),
        ('缺陷漏测率', 'lost_BugRate_nums'),
        ('项目主管评分', 'ProgramScores_nums'),
        ('技术主管评分', 'TechScores_nums'),
        ('质量扣分', 'minusScores_nums'),
        ('综合评分', 'TotalScores_nums')
    )
    # 获取 测试人员执行相关完整信息
    all_dict = CombiningData_tester(iteration_id,son_program_ids)
    # 分别拼装 前端列表 和 图表所有 数据
    yattrORtable, modules, module_fields = CombiningTableDataAndPicData(title_key_tuple, all_dict, useto)
    # 画图 或 集合数据列表
    if useto.lower() == 'pic':
        # 缺陷
        bar1 = Bar(init_opts=opts.InitOpts(width="360px",height="330px"))
        bar1.add_xaxis(modules)
        if type == 'bug':
            bar1.set_global_opts(
                title_opts=opts.TitleOpts(title="缺陷情况", pos_top="2%", pos_left="5%"),
                legend_opts=opts.LegendOpts(type_="scroll", pos_top="2%", orient="horizontal"),
            )
        else:
            bar1.set_global_opts(
                title_opts=opts.TitleOpts(title="缺陷情况", pos_top="3%", pos_left="1%"),
                legend_opts=opts.LegendOpts(type_="scroll", pos_right="51%", pos_top="8%", orient="vertical"),
            )
        for title, key in title_key_tuple[:6]:
            bar1.add_yaxis(title, yattrORtable[key])

        # 用例
        bar2 = Bar(init_opts=opts.InitOpts(width="360px", height="330px"))
        bar2.add_xaxis(modules)
        if type == 'case':
            bar2.set_global_opts(
                title_opts=opts.TitleOpts(title="用例情况", pos_top="2%", pos_left="5%"),
                legend_opts=opts.LegendOpts(type_="scroll", pos_top="2%", orient="horizontal"),
            )
        else:
            bar2.set_global_opts(
                title_opts=opts.TitleOpts(title="用例情况", pos_top="3%", pos_left="50%"),
                legend_opts=opts.LegendOpts(type_="scroll", pos_right="0%", pos_top="8%", orient="vertical"),
            )
        for title, key in title_key_tuple[6:15]:
            bar2.add_yaxis(title, yattrORtable[key])
        # 百分比
        bar3 = Bar(init_opts=opts.InitOpts(width="360px", height="330px"))
        bar3.add_xaxis(modules)
        if type == 'rate':
            bar3.set_global_opts(
                title_opts=opts.TitleOpts(title="百分比", pos_top="2%", pos_left="5%"),
                legend_opts=opts.LegendOpts(type_="scroll", pos_top="2%", orient="horizontal"),
                yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value} %"), interval=10)
            )
        else:
            bar3.set_global_opts(
                title_opts=opts.TitleOpts(title="百分比", pos_top="35%", pos_left="1%"),
                legend_opts=opts.LegendOpts(type_="scroll", pos_right="51%", pos_top="40%", orient="vertical"),
                yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value} %"), interval=10)
            )
        for title, key in title_key_tuple[15:22]:
            bar3.add_yaxis(title, yattrORtable[key], label_opts=opts.LabelOpts(formatter="{c} %"))
            # bar3.add_yaxis(title, yattrORtable[key], label_opts=opts.LabelOpts(formatter="{c} %"),itemstyle_opts=opts.ItemStyleOpts(color='green'),)

        # 主管评分
        bar4 = Bar(init_opts=opts.InitOpts(width="360px", height="330px"))
        bar4.add_xaxis(modules)
        if type == 'scores':
            bar4.set_global_opts(
                title_opts=opts.TitleOpts(title="质量扣分", pos_top="2%", pos_left="5%"),
                legend_opts=opts.LegendOpts(type_="scroll", pos_top="2%", orient="horizontal"),
            )
        else:
            bar4.set_global_opts(
                title_opts=opts.TitleOpts(title="质量扣分", pos_top="35%", pos_left="50%"),
                legend_opts=opts.LegendOpts(type_="scroll", pos_right="0%", pos_top="40%", orient="vertical"),
            )
        for title, key in title_key_tuple[24:25]:
            bar4.add_yaxis(title, yattrORtable[key])

        # 综合评分
        bar5 = Bar(init_opts=opts.InitOpts(width="1100px", height="330px"))
        bar5.add_xaxis(modules)
        if type == 'totalscores':
            bar5.set_global_opts(
                title_opts=opts.TitleOpts(title="综合评分", pos_top="2%", pos_left="5%"),
                legend_opts=opts.LegendOpts(type_="scroll", pos_top="2%", orient="horizontal"),
            )
        else:
            bar5.set_global_opts(
                title_opts=opts.TitleOpts(title="综合评分", pos_top="70%", pos_left="1%"),
                legend_opts=opts.LegendOpts(type_="scroll", pos_left="50%", pos_top="68%", orient="horizontal"),
            )
        for title, key in title_key_tuple[25:]:
            bar5.add_yaxis(title, yattrORtable[key])

        # 组合成整个画板
        # bars = Grid(init_opts=opts.InitOpts(theme=ThemeType.DARK,width="1300px", height="660px"))
        bars = Grid(init_opts=opts.InitOpts(width="1300px", height="990px"))
        if type == 'bug':
            bars.add(bar1, grid_opts=opts.GridOpts(pos_top="8%", pos_bottom="65%", pos_right="10%", pos_left="8%"))
        elif type == 'case':
            bars.add(bar2, grid_opts=opts.GridOpts(pos_top="8%", pos_bottom="65%", pos_right="10%", pos_left="8%"))
        elif type == 'rate':
            bars.add(bar3, grid_opts=opts.GridOpts(pos_top="8%", pos_bottom="65%", pos_right="10%", pos_left="8%"))
        elif type == 'scores':
            bars.add(bar4, grid_opts=opts.GridOpts(pos_top="8%", pos_bottom="65%", pos_right="10%", pos_left="8%"))
        elif type == 'totalscores':
            bars.add(bar5, grid_opts=opts.GridOpts(pos_top="8%", pos_bottom="65%", pos_right="10%", pos_left="8%"))
        else:
            bars.add(bar1, grid_opts=opts.GridOpts(pos_top="8%", pos_bottom="70%", pos_right="60%",pos_left="3%"))
            bars.add(bar2, grid_opts=opts.GridOpts(pos_top="8%", pos_bottom="70%", pos_left="53%"))
            bars.add(bar3, grid_opts=opts.GridOpts(pos_top="39%", pos_bottom="37%", pos_right="60%", pos_left="4%"))
            bars.add(bar4, grid_opts=opts.GridOpts(pos_top="39%", pos_bottom="37%", pos_left="53%"))
            # bars.add(bar5, grid_opts=opts.GridOpts(pos_top="72%"))
        bars.render_notebook()

        return bars,module_fields
    else:
        data = []
        for title, key in title_key_tuple:
            data.append(yattrORtable[key])
        return data,module_fields

def bugBar_scores(versionname,programname='V2',type='all',useto='pic'):
    '''评分统计、柱状图
        programname: 项目名称
        versionID: 迭代版本id
        type： 全部、开发、测试   all/developer/tester
        useto: 用途：画图、统计  pic/data
    '''
    son_programs = []
    program_ids = []
    if programname == '所有':
        programs, countss = OperationDB.getProgram()
        for program in programs:
            t_programname = program.name
            t_programid = program.id
            program_ids += str(t_programid)
            son_programs += TC_Programs[t_programname]
    else:
        programs, countss = OperationDB.getProgram(programname)
        t_programid = programs.id
        program_ids += str(t_programid)
        son_programs += TC_Programs[programname]

    son_program_ids = []
    for son_program in son_programs:
        son_ps,son_countss = OperationDB.getSonProgram(son_program)
        try:
            son_progrm_id = son_ps[0].id
            son_program_ids.append(son_progrm_id)
        except:
            pass
    if programname != None and programname != '' and programs == []:
        if useto=='pic':
            bars = Bar(init_opts=opts.InitOpts(width="1100px", height="330px"))
            return bars,[]
        else:
            return [],[]

    # 定义title和all_dict中key的对应关系
    title_key_tuple = (
        # ('项目主管评分', 'ProgramScores_nums'),
        # ('技术主管评分', 'TechScores_nums'),
        ('基础评分', 'ProgramScores_nums'),
        ('贡献加分', 'TechScores_nums'),
        ('质量扣分', 'minusScores_nums'),
        ('综合评分', 'TotalScores_nums')
    )

    # 获取所有制定产品对应迭代
    all_dict = {}
    icount = 0
    for program_id in program_ids:
        iteration, iicount = OperationDB.get_iteration(program_id,version=versionname)
        icount += iicount
        iteration_id = iteration.id
        if type == 'developer':
            # 获取 开发人员执行相关完整信息
            all_dict_dev = CombiningData_developer(iteration_id,son_program_ids)
            all_dict.update(all_dict_dev)
        elif type == 'tester':
            # 获取 测试人员执行相关完整信息
            all_dict_test = CombiningData_tester(iteration_id,son_program_ids)
            all_dict.update(all_dict_test)
        else:# 获取 开发人员执行相关完整信息
            all_dict_dev = CombiningData_developer(iteration_id,son_program_ids)
            # 获取 测试人员执行相关完整信息
            all_dict_test = CombiningData_tester(iteration_id,son_program_ids)
            all_dict.update(**all_dict_dev)
            all_dict.update(**all_dict_test)

    if icount == 0:
        if useto=='pic':
            bars = Bar(init_opts=opts.InitOpts(width="1100px", height="330px"))
            return bars,[]
        else:
            return [],[]
    # 分别拼装 前端列表 和 图表所有 数据
    yattrORtable, modules, module_fields = CombiningTableDataAndPicData(title_key_tuple, all_dict, useto)
    # 画图 或 集合数据列表
    if useto.lower() == 'pic':
        # 缺陷 & 测试记录
        bar1 = Bar(init_opts=opts.InitOpts(width="1100px",height="330px"))
        bar1.add_xaxis(modules)
        bar1.set_global_opts(
            # title_opts=opts.TitleOpts(title="主管评分", pos_top="2%", pos_left="5%"),
            title_opts=opts.TitleOpts(title="基础总分", pos_top="2%", pos_left="5%"),
            legend_opts=opts.LegendOpts(type_="scroll", pos_top="2%", orient="horizontal"),
        )
        for title, key in title_key_tuple[:3]:
            bar1.add_yaxis(title, yattrORtable[key])
        # 解决率
        bar2 = Bar(init_opts=opts.InitOpts(width="1100px", height="330px"))
        bar2.add_xaxis(modules)
        bar2.set_global_opts(
            title_opts=opts.TitleOpts(title="综合评分", pos_top="47%", pos_left="5%"),
            legend_opts=opts.LegendOpts(type_="scroll", pos_top="47%", orient="horizontal"),
        )
        for title, key in title_key_tuple[3:]:
            bar2.add_yaxis(title, yattrORtable[key])

        # 组合成整个画板
        # bars = Grid(init_opts=opts.InitOpts(theme=ThemeType.DARK,width="1300px", height="660px"))
        bars = Grid(init_opts=opts.InitOpts(width="1300px", height="660px"))
        bars.add(bar1, grid_opts=opts.GridOpts(pos_top="10%", pos_bottom="60%", pos_right="10%", pos_left="8%"))
        bars.add(bar2, grid_opts=opts.GridOpts(pos_top="55%", pos_bottom="5%", pos_right="10%", pos_left="8%"))
        bars.render_notebook()
        return bars,module_fields
    else:
        data = []
        for title, key in title_key_tuple:
            data.append(yattrORtable[key])
        return data,module_fields

def bugRadar_scores(versionname,programname='V2',type='all',useto='pic'):
    '''评分统计、柱状图
        programname: 项目名称
        versionID: 迭代版本id
        type： 全部、开发、测试   all/developer/tester
        useto: 用途：画图、统计  pic/data
    '''
    son_programs = []
    program_ids = []
    if programname == '所有':
        programs, countss = OperationDB.getProgram()
        for program in programs:
            t_programname = program.name
            t_programid = program.id
            program_ids += str(t_programid)
            son_programs += TC_Programs[t_programname]
    else:
        programs, countss = OperationDB.getProgram(programname)
        t_programid = programs.id
        program_ids += str(t_programid)
        son_programs += TC_Programs[programname]

    son_program_ids = []
    for son_program in son_programs:
        son_ps,son_countss = OperationDB.getSonProgram(son_program)
        try:
            son_progrm_id = son_ps[0].id
            son_program_ids.append(son_progrm_id)
        except:
            pass
    if programname != None and programname != '' and programs == []:
        if useto=='pic':
            radars = Radar(init_opts=opts.InitOpts(width="1100px", height="330px"))
            return radars,[]
        else:
            return [],[]

    # 定义title和all_dict中key的对应关系
    title_key_tuple = (
        # ('项目主管评分', 'ProgramScores_nums'),
        # ('技术主管评分', 'TechScores_nums'),
        ('基础评分', 'ProgramScores_nums'),
        ('贡献加分', 'TechScores_nums'),
        ('质量扣分', 'minusScores_nums'),
        ('综合评分', 'TotalScores_nums')
    )

    # 获取所有制定产品对应迭代
    all_dict = {}
    icount = 0
    for program_id in program_ids:
        iteration, iicount = OperationDB.get_iteration(program_id,version=versionname)
        icount += iicount
        iteration_id = iteration.id
        if type == 'developer':
            # 获取 开发人员执行相关完整信息
            all_dict_dev = CombiningData_developer(iteration_id,son_program_ids)
            all_dict.update(all_dict_dev)
        elif type == 'tester':
            # 获取 测试人员执行相关完整信息
            all_dict_test = CombiningData_tester(iteration_id,son_program_ids)
            all_dict.update(all_dict_test)
        else:# 获取 开发人员执行相关完整信息
            all_dict_dev = CombiningData_developer(iteration_id,son_program_ids)
            # 获取 测试人员执行相关完整信息
            all_dict_test = CombiningData_tester(iteration_id,son_program_ids)
            all_dict.update(**all_dict_dev)
            all_dict.update(**all_dict_test)

    if icount == 0:
        if useto=='pic':
            bars = Bar(init_opts=opts.InitOpts(width="1100px", height="330px"))
            return bars,[]
        else:
            return [],[]
    # 分别拼装 前端列表 和 图表所有 数据
    yattrORtable, modules, module_fields = CombiningTableDataAndPicData(title_key_tuple, all_dict, useto)
    # 画图 或 集合数据列表
    if useto.lower() == 'pic':
        c_schema = [
            {"name": "技术能力", "max": 100, "min": 5},
            {"name": "沟通协作", "max": 100, "min": 20},
            {"name": "学习创新", "max": 100, "min": 5},
            {"name": "积极性", "max": 120},
            {"name": "责任心", "max": 10},
            {"name": "执行力", "max": 10},
        ]

        radars = Radar()
        radars.add_schema(schema=c_schema)
        radars.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        # radars.set_global_opts(title_opts=opts.TitleOpts(title="绩效能力图"))
        radars.set_global_opts(
            title_opts=opts.TitleOpts(title="绩效能力图", pos_top="2%", pos_left="5%"),
            legend_opts=opts.LegendOpts(type_="scroll", pos_top="2%", orient="horizontal"),
        )

        # 下面就是具体的渲染了。
        all_data_attr = {
            '云资源': [[78, 96, 75, 99, 8, 5.5]],
            '云产品': [[60, 88, 85, 40, 7, 6]]
        }

        color_code1 = '#4587E7'
        color_code2 = '#66ff66'
        # 不超过11个人
        if len(all_data_attr) <= 11:
            color_list = ['red', 'orange', 'yellow', 'green', 'cyan', 'blue', 'purple', 'gray', 'pink', 'brown', 'black']
            i = 0
            for key in all_data_attr.keys():
                attr = all_data_attr[key]
                color_str = color_list[i]
                radars.add(key, attr, color=color_str, areastyle_opts=opts.AreaStyleOpts(opacity=0.1), )
                i += 1
        else:
            # 超过11个人
            i = 0
            for key in all_data_attr.keys():
                attr = all_data_attr[key]
                color_code = random.randint(1, 16777215)  # 0xffffff == 1677215
                new_color_code = hex(color_code)
                color_str = '#' + new_color_code.lstrip('0x').zfill(6)
                radars.add(key, attr, color=color_str, areastyle_opts=opts.AreaStyleOpts(opacity=0.1), )
                i += 1

        return radars,module_fields
    else:
        data = []
        for title, key in title_key_tuple:
            data.append(yattrORtable[key])
        return data,module_fields

def bugPie_type(versionname,programname='V2',type='offline',useto='pic'):
    '''缺陷类型统计、饼图
        programname: 项目名称
        type： 线上、线下、全部   offline/online/all
        useto: 用途：画图、统计  pic/data
        versionID: 迭代版本id
    '''
    pie_width = '800px'
    pie_height = '400px'
    programs,countss = OperationDB.getProgram(programname)
    if programname != None and programname != '' and programs == []:
        if useto=='pic':
            pies = Pie(init_opts=opts.InitOpts(width=pie_width, height=pie_height))
            return pies,[]
        else:
            return [],[]
    progrm_id = programs.id
    iteration,icount = OperationDB.get_iteration(progrm_id,version=versionname)
    if icount == 0:
        if useto=='pic':
            pies = Pie(init_opts=opts.InitOpts(width=pie_width, height=pie_height))
            return pies,[]
        else:
            return [],[]
    iteration_id = iteration.id
    type_fields = []
    types = []
    off_created_dict = {'type': "迭代新增", "type1": 3}
    # off_closed_dict = {'type': "迭代解决", "type1": 2}
    on_created_dict = {'type': "线上新增", "type1": 3}
    # on_closed_dict = {'type': "线上解决", "type1": 2}
    yattr = {
        'off_created_nums':[],
        # 'off_closed_nums':[],
        'on_created_nums':[],
        # 'on_closed_nums':[],
    }
    all_dict = {}
    all_bugs,all_count = OperationDB.readBugsFromDB(limit=9999,condition={'iteration': iteration_id})
    i = 1
    for bug in all_bugs:
        offon = bug['type_owner']
        status = bug['status']
        typename = bug['bug_type']
        if typename == '' or typename == None or typename == 'null'  or typename == 'Null':
            typename = '其他'
        #初始化模块分类地字典
        if typename not in all_dict.keys():
            all_dict[typename] = {
                'off_created_nums': 0,
                # 'off_closed_nums': 0,
                'on_created_nums': 0,
                # 'on_closed_nums': 0,
            }
        # 模块分类后 bug计数
        if offon == 'offline':
            all_dict[typename]['off_created_nums'] += 1
            # if status == '已关闭' or status == '已解决' or status == 'closed':
            #     all_dict[typename]['off_closed_nums'] += 1
        else:
            all_dict[typename]['on_created_nums'] += 1
            # if status == '已关闭' or status == '已解决' or status == 'closed':
            #     all_dict[typename]['on_closed_nums'] += 1
    for t,numsdict in all_dict.items():
        type_fields.append(['type%s' % i, t])
        types.append(t)
        if useto.lower() == 'pic':
            if type == 'offline':
                yattr['off_created_nums'].append(numsdict['off_created_nums'])
                # yattr['off_closed_nums'].append(numsdict['off_closed_nums'])
            elif type == 'online':
                yattr['on_created_nums'].append(numsdict['on_created_nums'])
                # yattr['on_closed_nums'].append(numsdict['on_closed_nums'])
            else:
                yattr['off_created_nums'].append(numsdict['off_created_nums'])
                # yattr['off_closed_nums'].append(numsdict['off_closed_nums'])
                yattr['on_created_nums'].append(numsdict['on_created_nums'])
                # yattr['on_closed_nums'].append(numsdict['on_closed_nums'])
        else:
            if type == 'offline':
                off_created_dict['type%s' % i] = numsdict['off_created_nums']
                # off_closed_dict['type%s' % i] = numsdict['off_closed_nums']
            elif type == 'online':
                on_created_dict['type%s' % i] = numsdict['on_created_nums']
                # on_closed_dict['type%s' % i] = numsdict['on_closed_nums']
            else:
                off_created_dict['type%s' % i] = numsdict['off_created_nums']
                # off_closed_dict['type%s' % i] = numsdict['off_closed_nums']
                on_created_dict['type%s' % i] = numsdict['on_created_nums']
                # on_closed_dict['type%s' % i] = numsdict['on_closed_nums']
        i += 1
    if useto.lower() == 'pic':
        if type == 'offline':
            pies = Pie(init_opts=opts.InitOpts(width=pie_width,height=pie_height))
            pies.add('迭代新增', [list(z) for z in zip(types, yattr['off_created_nums'])],center=["50%", "50%"])
        elif type == 'online':
            pies = Pie(init_opts=opts.InitOpts(width=pie_width,height=pie_height))
            pies.add('线上新增', [list(z) for z in zip(types, yattr['on_created_nums'])],center=["50%", "50%"])
        else:
            pie1 = Pie(init_opts=opts.InitOpts(theme=ThemeType.ROMA))
            pie1.add('迭代新增', [list(z) for z in zip(types, yattr['off_created_nums'])],center=["30%", "60%"])
            pie1.set_global_opts(title_opts=opts.TitleOpts(title="迭代新增", subtitle="迭代内新增bug数", pos_left='7%'))
            pie2 = Pie(init_opts=opts.InitOpts(theme=ThemeType.ROMA))
            pie2.add('线上新增', [list(z) for z in zip(types, yattr['on_created_nums'])],center=["70%", "60%"])
            pie2.set_global_opts(title_opts=opts.TitleOpts(title="线上新增", subtitle="上线后新增bug数", pos_right='7%'))
            pies = Grid()
            pies.add(pie1,grid_opts=opts.GridOpts(pos_left="55%"))
            pies.add(pie2,grid_opts=opts.GridOpts(pos_right="55%"))
            pies.render_notebook()
        return pies,type_fields
    else:
        if type == 'offline':
            data = [off_created_dict]
        elif type == 'online':
            data = [on_created_dict]
        else:
            data = [off_created_dict,on_created_dict]
        return data,type_fields