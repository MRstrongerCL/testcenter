# -*- coding:utf-8 -*-
# chenliang

import os
from .PublicMethods import Get_Next_Time
from .PublicMethods import str_2_int,str_2_float
from Bug.models import *
from .SourceData.StatisticsAndAnalysisBug import ReadBugExcel
from django.db.models import Count
from django.db.models import Q


# 数据库操作(非专用于接口调用)
def readExcelAndWrite2DB(filepath=None):
    filepath = os.path.join(os.getcwd(),'TestCenter\\temple\\项目内bug.xlsx')
    rdict = ReadBugExcel(filepath)
    all_bugs = rdict.get('all_bug_lines')
    for bug in all_bugs[0:]:
        test1 = detail(
            title=bug['标题'],
            third_id=bug['任务ID'],
            Severity=bug['严重程度'],
            priority=bug['优先级'],
            bug_type=bug['缺陷类型'],
            bug_moudle=bug['功能模块'],
            bug_owner=bug['缺陷Owner'],
            bug_creater=bug['创建者'],
            create_time=bug['创建时间'],
            update_time=bug['更新时间'],
            finish_time=bug['完成时间'],
            status=bug['任务状态'],
        )
        test1.save()

# 数据库操作(接口调用)
def bugListWrite2DB(buglist=[],iterationid=None,program=None,type='offline',methods='file'):
    # print("---------> 开始写数据库 bug_detail")
    if not iterationid:
        iterationid = ''
    itera = iteration.objects.filter(id=iterationid)[0]
    itera_stime = itera.start_time
    itera_etime = itera.end_time
    program_id = itera.program_id
    cur_time = Get_Next_Time()
    # if not (itera_stime < cur_time <itera_etime):
    #     print("已经超过迭代起止时间，不允许修改 bug详情")
    #     return False
    if not program:
        program = ''
    for bug in buglist:
        keys = bug.keys()
        if '标题' in keys:
            title = bug['标题']
        else:
            title = ''
        if '任务ID' in keys:
            third_id = bug['任务ID']
        else:
            third_id = ''
        if '严重程度' in keys:
            Severity = bug['严重程度']
        else:
            Severity = ''
        if '优先级' in keys:
            priority = bug['优先级']
        else:
            priority = ''
        if '缺陷类型' in keys:
            bug_type = bug['缺陷类型']
        else:
            bug_type = ''
        if '功能模块' in keys:
            bug_moudle = bug['功能模块']
        else:
            bug_moudle = ''
        if '缺陷Owner' in keys:
            bug_owner = bug['缺陷Owner']
        else:
            bug_owner = ''
        if '创建者' in keys:
            bug_creater = bug['创建者']
        else:
            bug_creater = ''
        if '创建时间' in keys:
            create_time = bug['创建时间']
        else:
            create_time = ''
        if '更新时间' in keys:
            update_time = bug['更新时间']
        else:
            update_time = ''
        if '完成时间' in keys:
            finish_time = bug['完成时间']
        else:
            finish_time = ''
        if '任务状态' in keys:
            status = bug['任务状态']
        else:
            status = ''
        if third_id=='' or third_id==None:
            if title=='' or title==None:
                res_count = 0
            else:
                res = detail.objects.filter(title=title, program=program_id)
                res_count = len(res)
        else:
            res = detail.objects.filter(third_id=third_id, program=program_id)
            res_count = len(res)

        # 获取问题归属线上还是线下
        if type == 'all':
            line_type = bug['lineType']
        else:
            line_type = type
        # 通过api方式获取的bug数据，线上问题归属到上期迭代（如果以每周统计，可以注释）
        if line_type == 'online' and methods == 'api':
            # 获取上期迭代id（用于线上问题记录）
            last_id = '0' # 第一个迭代统计的线上问题 固定为第0个迭代的线上bug, 加上program_id可以识别出来
            ids = iteration.objects.filter(program_id=program_id).order_by("-end_time")
            lcount = len(ids)
            if lcount > 1:
                for i in list(range(lcount)):
                    if str(iterationid) == str(ids[i].id) and i != (lcount-1):
                        last_ids = ids[i + 1]
                        last_id = last_ids.id
                        break
            iteration_id = last_id
        else:
            iteration_id = iterationid
        if res_count > 0:
            status_list = res.values_list('status')
            old_status = status_list[0][0]
            old_iterration_id = res[0].iteration
            if (status == old_status) and ( str(iteration_id) == str(old_iterration_id)):
                continue  #此条数据已经写过数据库，跳过
            else:
                # 更新数据
                res.update(
                    Severity=Severity,
                    priority=priority,
                    bug_type=bug_type,
                    bug_moudle=bug_moudle,
                    bug_owner=bug_owner,
                    bug_creater=bug_creater,
                    update_time=update_time,
                    finish_time=finish_time,
                    status=status,
                    iteration=iterationid,
                    program=program,
                    type_owner=line_type
                )
                continue
        test1 = detail(
            title=title,
            third_id=third_id,
            Severity=Severity,
            priority=priority,
            bug_type=bug_type,
            bug_moudle=bug_moudle,
            bug_owner=bug_owner,
            bug_creater=bug_creater,
            create_time=create_time,
            update_time=update_time,
            finish_time=finish_time,
            status=status,
            iteration=iterationid,
            program=program,
            type_owner=line_type
        )
        test1.save()

def getProgram(program_name=None):
    '''查询父项目'''
    pro = program.objects.filter(name=program_name)
    count = len(pro)
    if count == 0:
        return [],0
    return pro[0],count

def getProgramCondition(condition={},true_or_false=True):
    '''查询项目'''
    if true_or_false:
        pro = program.objects.filter(**condition).order_by('-id')
    else:
        pro = program.objects.exclude(**condition).order_by('-id')
    count = len(pro)
    if count == 0:
        return [],0
    return pro[0],count

def getSonProgram(program_name=None):
    '''查询子项目'''
    pro = son_program.objects.filter(name=program_name)
    count = len(pro)
    if count == 0:
        return None,0
    return pro,count

def get_iteration(programId=None,version=None):
    '''查询项目'''
    itera = iteration.objects.filter(program_id=programId,version=version)
    count = len(itera)
    if count == 0:
        return [],0
    return itera[0],count

def getIterations(condition={},true_or_false=True,limit=None):
    '''查询迭代表'''
    if true_or_false:
        result = iteration.objects.filter(**condition, ).order_by('-id')
    else:
        result = iteration.objects.exclude(**condition).order_by('-id')
    ids = []
    versions = []
    count = len(result)
    if limit == None:
        end = count
    else:
        end = int(limit)
    for one in result[0:end]:
        ids.append(one.id)
        versions.append(one.version)
    if count == 0:
        return [],[],0
    return ids,versions,count

def writeProgram(program_name):
    pro,count = getProgram(program_name)
    if count == 0:
        prog = program(name=program_name)
        prog.save()
        id = prog.id
    else:
        id = pro.id
    return id

def writeSonProgram(program_name,parentID,on_t_no=0, on_r_no=0, off_t_no=0,off_r_no=0):
    pro,count = getSonProgram(program_name)
    up_time = Get_Next_Time()
    if count == 0:
        prog = son_program(
            name=program_name,
            parent_program_id=parentID,
            online_total_no=on_t_no,
            online_resloved_no=on_r_no,
            offline_total_no=off_t_no,
            offline_resloved_no=off_r_no,
            update_time=up_time
        )
        prog.save()
        id = prog.id
    else:
        on_t_no +=int(pro[0].online_total_no)
        off_t_no +=int(pro[0].offline_total_no)
        on_r_no +=int(pro[0].online_resloved_no)
        off_r_no +=int(pro[0].offline_resloved_no)
        pro.update(
            online_total_no=on_t_no,
            online_resloved_no=on_r_no,
            offline_total_no=off_t_no,
            offline_resloved_no=off_r_no,
            update_time=up_time
        )
        id = pro[0].id
    return id

def updateTestDetail(conditionDict,updateDict,true_or_false=True):
    '''
    更新testdetail表
    :param conditionDict:条件字段
    :param updateDict:更新字段
    :param true_or_false: 正向筛选还事福安想筛选
    :return:
    '''
    if true_or_false:
        tds = testdetail.objects.filter(**conditionDict).order_by('-id')
    else:
        tds = testdetail.objects.exclude(**conditionDict).order_by('-id')
    count = len(tds)
    cur_time = Get_Next_Time()
    updateDict.update({"update_time": cur_time})
    if count == 0:
        itera = iteration.objects.filter(id=conditionDict["iteration_id"])[0]
        itera_stime = itera.start_time
        itera_etime = itera.end_time
        updateDict['s_time'] = itera_stime
        updateDict['e_time'] = itera_etime
        updateDict.update(conditionDict)
        ntds = testdetail(**updateDict)
        ntds.save()
        id = ntds.id
    else:
        tds.update(**updateDict)
        id = tds[0].id
    return id

def updateDevDetail(conditionDict,updateDict,true_or_false=True):
    '''
    更新ddevelopdetail表
    :param conditionDict:条件字段
    :param updateDict:更新字段
    :param true_or_false: 正向筛选还事福安想筛选
    :return:
    '''
    if true_or_false:
        tds = developdetail.objects.filter(**conditionDict).order_by('-id')
    else:
        tds = developdetail.objects.exclude(**conditionDict).order_by('-id')
    count = len(tds)
    cur_time = Get_Next_Time()
    updateDict.update({"update_time": cur_time})
    if count == 0:
        itera = iteration.objects.filter(id=conditionDict["iteration_id"])[0]
        itera_stime = itera.start_time
        itera_etime = itera.end_time
        updateDict['s_time'] = itera_stime
        updateDict['e_time'] = itera_etime
        updateDict.update(conditionDict)
        ntds = developdetail(**updateDict)
        ntds.save()
        id = ntds.id
    else:
        tds.update(**updateDict)
        id = tds[0].id
    return id

def writeTestDetail(iterationID,son_programID,stime, etime, cases):
    '''
    写入用例执行数据
    :param iterationID:
    :param stime:
    :param etime:
    :param cases:
    :return:
    '''
    itera = iteration.objects.filter(id=iterationID)[0]
    itera_stime = itera.start_time
    itera_etime = itera.end_time
    cur_time = Get_Next_Time()
    if not (itera_stime < cur_time <itera_etime):
        print("已经超过迭代起止时间，不允许修改 测试执行情况")
        return False
    for case in cases:
        runner = case['runner']
        tds = testdetail.objects.filter(tester=runner,iteration_id=iterationID,son_program_id=son_programID)
        count = len(tds)
        if count == 0:
            tds = testdetail(
                tester=runner,
                iteration_id=iterationID,
                son_program_id=son_programID,
                passRunCount=case['passRunCount'],
                failedRunCount=case['failedRunCount'],
                blockedRunCount=case['blockedRunCount'],
                notRunCount=case['notRunCount'],
                passReviewCount=case['passReviewCount'],
                failedReviewCount=case['failedReviewCount'],
                notReviewCount=case['notReviewCount'],
                createdCasesCount=case['createdCasesCount'],
                reviewCasesCount=case['reviewCasesCount'],
                update_time=cur_time,
                s_time=stime,
                e_time=etime,
                offline_BugCount='',
                online_BugCount=''
            )
            tds.save()
        else:
            tds.update(
                passRunCount=case['passRunCount'],
                failedRunCount=case['failedRunCount'],
                blockedRunCount=case['blockedRunCount'],
                notRunCount=case['notRunCount'],
                passReviewCount=case['passReviewCount'],
                failedReviewCount=case['failedReviewCount'],
                notReviewCount=case['notReviewCount'],
                createdCasesCount=case['createdCasesCount'],
                reviewCasesCount=case['reviewCasesCount'],
                update_time=cur_time,
                s_time=stime,
                e_time=etime,
                offline_BugCount='',
                online_BugCount=''

            )
    return True

def write_iteration(version,program_id,stime='',etime=''):
    if not version or not program_id or not stime or not etime:
        print("have no enough prams,check iteration、program_id、start_time、end_time...")
        return False
    itera, count = get_iteration(program_id,version)
    if count == 0:
        ctime_str = Get_Next_Time()
        set_iteration = iteration(
            version=version,
            program_id=program_id,
            start_time=stime,
            end_time=etime,
            create_time=ctime_str
        )
        set_iteration.save()
        id = set_iteration.id
    else:
        id = itera.id
    return id

def updateRate(conditionDict,updateDict,true_or_false=True):
    '''
    更新系数比表
    :param conditionDict:条件字段
    :param updateDict:更新字段
    :param true_or_false: 正向筛选还事福安想筛选
    :return:
    '''
    if true_or_false:
        tds = rate.objects.filter(**conditionDict).order_by('-id')
    else:
        tds = rate.objects.exclude(**conditionDict).order_by('-id')
    count = len(tds)
    cur_time = Get_Next_Time()
    updateDict.update({"update_time": cur_time})
    if count == 0:
        updateDict.update(conditionDict)
        ntds = rate(**updateDict)
        ntds.save()
        id = ntds.id
    else:
        tds.update(**updateDict)
        id = tds[0].id
    return id

def readTargetRate(condition={},true_or_false=True):
    '''获取制定类型的系数比'''
    rlist = []
    if true_or_false:
        all_queryset = rate.objects.filter(**condition).order_by('-id')
    else:
        all_queryset = rate.objects.exclude(**condition).order_by('-id')
    allcount = len(all_queryset)
    if allcount == 0:
        return None
    else:
        id = all_queryset[0].id
        rate_no = float(all_queryset[0].rateNum)
    return rate_no

def readSonProgramCount(condition={},true_or_false=True):
    '''查询子项目记录的总计bug情况
    conditon：dict 条件
    true_or_false: bool 条件控制，正向选择、反向选择
    '''
    rlist = []
    if true_or_false:
        all_queryset = son_program.objects.filter(**condition).order_by('-id')
    else:
        all_queryset = son_program.objects.exclude(**condition).order_by('-id')
    allcount = len(all_queryset)
    for one in all_queryset:
        onedict = {
            "id": one.id,
            "name": one.name,
            "parent_program_id": one.parent_program_id,
            "online_total_no": one.online_total_no,
            "online_resloved_no": one.online_resloved_no,
            "offline_total_no": one.offline_total_no,
            "offline_resloved_no": one.offline_resloved_no,
        }
        rlist.append(onedict)
    return rlist,allcount

def readBugsFromDB(key=None,page=1,limit=1000,condition={},true_or_false=True):
    '''查询bug列表返回
    key: string 模糊查询关键字
    page：int 第几页
    limit：int 查询多少条
    conditon：dict 条件
    true_or_false: bool 条件控制，正向选择、反向选择
    '''
    rlist = []
    page = int(page)
    limit = int(limit)
    start_index = (page - 1) * limit
    end_index = page * limit
    if key == None or key == '':
        # result = detail.objects.values("id", "title", "iteration", "bug_owner", "bug_creater", "bug_moudle", "status")
        # result = detail.objects.all().order_by('-id')[:limit]
        if true_or_false:
            result = detail.objects.filter(**condition,).order_by('-id')
        else:
            result = detail.objects.exclude(**condition).order_by('-id')
        count = len(result)
        if count == 0:
            return [], count
        for one in result[start_index:end_index]:
            version = iteration.objects.filter(id=one.iteration)[0].version
            onedict = {
                "id": one.id,
                "title": one.title,
                "iteration": version,
                "bug_owner": one.bug_owner,
                "bug_creater": one.bug_creater,
                "bug_closer": one.bug_closer,
                "bug_moudle": one.bug_moudle,
                "bug_type": one.bug_type,
                "type_owner": one.type_owner,
                "status": one.status
            }
            rlist.append(onedict)
    else:
        try:
            result0 = detail.objects.filter(id=key).filter(**condition,).order_by('-id')
        except:
            result0 = []
        result1 = detail.objects.filter(title__contains=key).filter(**condition,).order_by('-id')
        result2 = detail.objects.filter(bug_moudle__contains=key).filter(**condition,).order_by('-id')
        result3 = detail.objects.filter(bug_type__contains=key).filter(**condition,).order_by('-id')
        result4 = detail.objects.filter(bug_owner__contains=key).filter(**condition,).order_by('-id')
        result5 = detail.objects.filter(bug_creater__contains=key).filter(**condition,).order_by('-id')
        result6 = detail.objects.filter(bug_closer__contains=key).filter(**condition,).order_by('-id')
        result7 = detail.objects.filter(status__contains=key).filter(**condition,).order_by('-id')
        try:
            itera = iteration.objects.filter(version=key)[0]
            itera_id = itera.id
            result8 = detail.objects.filter(iteration=itera_id).filter(**condition,).order_by('-id')
        except:
            result8 = []
        result9 = detail.objects.filter(type_owner=key).filter(**condition,).order_by('-id')
        result = list(result0) + list(result1) + list(result2) + list(result3) + list(result4) + list(result5) + list(result6) + list(result7) + list(result8) + list(result9)
        count = len(result)
        if count == 0:
            return [], count
        for one in result[start_index:end_index]:
            version = iteration.objects.filter(id=one.iteration)[0].version
            onedict = {
                "id": one.id,
                "title": one.title,
                "iteration": version,
                "bug_owner": one.bug_owner,
                "bug_creater": one.bug_creater,
                "bug_closer": one.bug_closer,
                "bug_moudle": one.bug_moudle,
                "bug_type": one.bug_type,
                "type_owner": one.type_owner,
                "status": one.status
            }
            rlist.append(onedict)
    return rlist,count

def readIterationsAccordProgramID(program_id,limit=7):
    '''根据项目id读取迭代id和版本号'''
    result = iteration.objects.filter(program_id=program_id).order_by('-end_time')[:limit]
    count = len(result)
    rdict = {"ids":[], "versions":[], 'start_times':[], 'end_times':[]}
    if count != 0:
        for one in result:
            rdict["ids"].insert(0,one.id)
            rdict["versions"].insert(0,one.version)
            rdict["start_times"].insert(0,one.start_time)
            rdict["end_times"].insert(0,one.end_time)
    return rdict

def readBugNumsAccordCondition(condition,true_or_false=True):
    '''根据条件读取bug数目'''
    if true_or_false:
        nums = detail.objects.filter(**condition).aggregate(nums_id=Count('id',distinct=True))
    else:
        nums = detail.objects.exclude(**condition).aggregate(nums_id=Count('id',distinct=True))
    return nums['nums_id']

def readTesterRunInfoAccordIterationID(iterationID,son_program_ids,limit=50):
    '''根据迭代id读取测试人员执行数据'''
    mifilter = Q()
    for son_program_id in son_program_ids:
        mifilter = mifilter | Q(iteration_id=iterationID,son_program_id=son_program_id)
    result = testdetail.objects.filter(mifilter)[:limit]
    count = len(result)
    rdict = {}
    if count != 0:
        for one in result:
            name = one.tester
            if name not in rdict.keys():
                rdict[name] = one
            else:
               rdict[name].passRunCount = str(str_2_int(rdict[name].passRunCount) + str_2_int(one.passRunCount))
               rdict[name].failedRunCount = str(str_2_int(rdict[name].failedRunCount) + str_2_int(one.failedRunCount))
               rdict[name].blockedRunCount = str(str_2_int(rdict[name].blockedRunCount) + str_2_int(one.blockedRunCount))
               rdict[name].notRunCount = str(str_2_int(rdict[name].notRunCount) + str_2_int(one.notRunCount))
               rdict[name].offline_BugCount = str(str_2_int(rdict[name].offline_BugCount) + str_2_int(one.offline_BugCount))
               rdict[name].online_BugCount = str(str_2_int(rdict[name].online_BugCount) + str_2_int(one.online_BugCount))
               rdict[name].lost_BugCount = str(str_2_int(rdict[name].lost_BugCount) + str_2_int(one.lost_BugCount))
               rdict[name].failedReviewCount = str(str_2_int(rdict[name].failedReviewCount) + str_2_int(one.failedReviewCount))
               rdict[name].notReviewCount = str(str_2_int(rdict[name].notReviewCount) + str_2_int(one.notReviewCount))
               rdict[name].passReviewCount = str(str_2_int(rdict[name].passReviewCount) + str_2_int(one.passReviewCount))
               rdict[name].createdCasesCount = str(str_2_int(rdict[name].createdCasesCount) + str_2_int(one.createdCasesCount))
               rdict[name].reviewCasesCount = str(str_2_int(rdict[name].reviewCasesCount) + str_2_int(one.reviewCasesCount))
               rdict[name].ProgramScores = str(max(str_2_float(rdict[name].ProgramScores), str_2_float(one.ProgramScores)))
               rdict[name].TechScores = str(max(str_2_float(rdict[name].TechScores), str_2_float(one.TechScores)))
    return rdict

def readDeveloperInfoAccordIterationID(iterationID,son_program_ids,limit=50):
    '''根据迭代id读取开发人员执行数据'''
    mifilter = Q()
    for son_program_id in son_program_ids:
        mifilter = mifilter | Q(iteration_id=iterationID,son_program_id=son_program_id)
    result = developdetail.objects.filter(mifilter)[:limit]
    count = len(result)
    rdict = {}
    if count != 0:
        for one in result:
            name = one.developer
            if name not in rdict.keys():
                rdict[name] = one
            else:
               rdict[name].reopenBugCount = str(str_2_int(rdict[name].reopenBugCount) + str_2_int(one.reopenBugCount))
               rdict[name].failedSmokeCount = str(str_2_int(rdict[name].failedSmokeCount) + str_2_int(one.failedSmokeCount))
               rdict[name].delayTestTimes = str(str_2_int(rdict[name].delayTestTimes) + str_2_int(one.delayTestTimes))
               rdict[name].ProgramScores = str(max(str_2_float(rdict[name].ProgramScores), str_2_float(one.ProgramScores)))
               rdict[name].TechScores = str(max(str_2_float(rdict[name].TechScores), str_2_float(one.TechScores)))
    return rdict
