# coding:utf-8
import json
import traceback
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.views import APIView
from django.db import transaction
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib.auth.models import User,Group
from TestCenter.LogicLib import OperationDB
from TestCenter.LogicLib.SourceData.StatisticsAndAnalysisBug import TONG_JI_DICT
from TestCenter.LogicLib.SourceData.StatisticsAndAnalysisBug import TITLE_SPECIAL_DICT_ZENTAO
from TestCenter.LogicLib.SourceData.StatisticsAndAnalysisBug import StatisticsBugFromList
from TestCenter.LogicLib.BusinessFunc.mycharts import myline,bugline,bugline_iteration,bugBar_mudle,bugPie_type,bugBar_developer,bugBar_tester,bugBar_total,bugBar_scores,bugRadar_scores
from TestCenter.LogicLib.Zentao.ZentaoManage import returnBugsInfo,returnRunCases
from TestCenter.LogicLib.Config import *


def response_as_json(data):
    json_str = json.dumps(data)
    response = HttpResponse(
        json_str,
        content_type="application/json",
    )
    response["Access-Control-Allow-Origin"] = "*"
    return response

def json_response(data, code=0, msg='success'):
    try:
        length = len(data['series'])
    except:
        length = len(data)
    data = {
        "code": code,
        "msg": msg,
        "data": data,
        "data_length":length
    }
    return response_as_json(data)

def json_error(error_string="error", code=500, **kwargs):
    data = {
        "code": code,
        "msg": error_string,
        "data": {}
    }
    data.update(kwargs)
    return response_as_json(data)

def returnKey(dictobject,target_str):
    '''根据value包含指定字符船，返回其key值'''
    for key,value in dictobject.items():
        if target_str in value:
            return key

@login_required
def buglist(request):
    contextdict = {}
    contextdict['quality_style'] = 'color: #fff;font-weight:bold'
    contextdict['view_v2'] = 'layui-nav-itemed'
    contextdict['bug_v2_style'] = 'background-color: #009688;color: #fff;'
    contextdict['programs'] = json.dumps(list(TC_Programs.keys()))
    return render(request, 'quality/buglist.html', context=contextdict)

@permission_required('Bug.view_program')
@login_required
def total(request):
    root_programs = list(TC_Programs.keys())
    root_programs.insert(0,"所有")
    if 'offonline' in request.GET and request.GET['offonline']:
        offonline = request.GET['offonline']
    else:
        offonline = 'offline'
    if 'program' in request.GET and request.GET['program']:
        program_name = request.GET['program']
    else:
        program_name = "所有"
    bar, module_fields = bugBar_total(program_name, offonline, useto='pic')
    contextdict = {}
    contextdict['quality_style'] = 'color: #fff;font-weight:bold'
    contextdict['view_v2'] = 'layui-nav-itemed'
    contextdict['total_v2_style'] = 'background-color: #009688;color: #fff;'
    data,programs = bugBar_total(program_name, offonline, useto='data')
    if programs != []:
        contextdict['myechart'] = bar.render_embed()
    contextdict['modules_fileds'] = json.dumps(module_fields)
    contextdict['labels'] = json.dumps(programs[::-1])
    contextdict['programs'] = json.dumps(root_programs)
    return render(request, 'quality/total.html', context=contextdict)

@permission_required('Bug.view_program')
@login_required
def total_update(request):
    '''更新总体统计图表'''
    if 'program' in request.GET and request.GET['program']:
        program_name = request.GET['program']
    else:
        program_name = '所有'
    if 'offonline' in request.GET and request.GET['offonline']:
        offonline = request.GET['offonline']
    else:
        offonline = 'offline'
    try:
        bar, programs = bugBar_total(program_name,offonline,useto='pic')
        bar_base = bar.dump_options_with_quotes()
        re_bar = json.loads(bar_base)
    except:
        re_bar = ''
    return json_response(re_bar)

@permission_required('Bug.view_program')
@login_required
def query_bugs_total(request):
    request.encoding = 'utf-8'
    if 'program' in request.GET and request.GET['program']:
        program_name = request.GET['program']
    else:
        program_name = '所有'
    if 'offonline' in request.GET and request.GET['offonline']:
        offonline = request.GET['offonline']
    else:
        offonline = 'offline'
    try:
        data, programs = bugBar_total(program_name,offonline, useto='data')
        code = 0
        totalcount = len(programs)
        message = 'success'
    except Exception as e:
        code = 1001
        totalcount = 0
        data = []
        programs = []
        message = 'error:查询失败,' + str(e)
    rdict = {
        'code': code,
        'count': totalcount,
        'data': data,
        'labels': programs,
        'msg': message
    }
    return_json = json.dumps(rdict)
    return HttpResponse(return_json)

@permission_required('Bug.change_detail')
@login_required
def manage_setting(request):
    contextdict = {}
    contextdict['quality_style'] = 'color: #fff;font-weight:bold'
    contextdict['view_v2'] = 'layui-nav-itemed'
    contextdict['mange_v2_style'] = 'background-color: #009688;color: #fff;'
    contextdict['import_v2_title_class'] = 'layui-this'
    contextdict['import_v2_title_style'] = 'color: #009688;font-weight: 750;'
    contextdict['programs'] = json.dumps(TC_Programs)
    if request.user.has_perm("Bug.add_detail") and request.user.has_perm("Bug.add_detail"):
        contextdict['import_v2_title_class'] = 'layui-this'
        contextdict['import_v2_title_style'] = 'color: #009688;font-weight: 750;'
        contextdict['import_v2_title_show'] = 'layui-show'
    elif request.user.has_perm("Bug.change_developdetail") and request.user.has_perm("Bug.delete_developdetail"):
        contextdict['import_v2_title_class2'] = 'layui-this'
        contextdict['import_v2_title_style2'] = 'color: #009688;font-weight: 750;'
        contextdict['import_v2_title_show2'] = 'layui-show'
    elif request.user.has_perm("Bug.add_testdetail") and request.user.has_perm("Bug.add_developdetail") and request.user.has_perm("Bug.delete_testdetail") and request.user.has_perm("Bug.delete_developdetail"):
        contextdict['import_v2_title_class3'] = 'layui-this'
        contextdict['import_v2_title_style3'] = 'color: #009688;font-weight: 750;'
        contextdict['import_v2_title_show3'] = 'layui-show'
    else:
        contextdict['import_v2_title_class'] = 'layui-this'
        contextdict['import_v2_title_style'] = 'color: #009688;font-weight: 750;'
        contextdict['import_v2_title_show'] = 'layui-show'
    # group = Group.objects.filter(name__contains="测试")[0]
    # users = group.user_set.all()
    # 取用户 职能 & 项目 的交集
    cur_user = request.user
    cur_group_set = Group.objects.filter(user=cur_user)
    ptusers = []
    a2 = ()
    for cgroup in cur_group_set:
        cusers = cgroup.user_set.all()
        if "管理" not in cgroup.name and "主管" not in cgroup.name and "组长" not in cgroup.name:
            a1 = []
            for cu in cusers:
                a1.append(cu.first_name)
            a2 = set(a1)
            ptusers.append(a2)
    for a3 in ptusers:
        a2 = a2 & a3
    ptuserslist = list(a2)
    users = User.objects.filter(groups__name="测试")
    userlist = [user.first_name for user in users]
    dusers = User.objects.filter(groups__name="开发")
    duserlist = [user.first_name for user in dusers]
    contextdict['users'] = json.dumps(userlist)
    contextdict['dusers'] = json.dumps(duserlist)
    contextdict['pusers'] = json.dumps(ptuserslist)
    contextdict['tusers'] = json.dumps(ptuserslist)
    return render(request, 'quality/reportmanage.html', context=contextdict)

@permission_required('Bug.view_detail')
@login_required
def queryBugList(request):
    request.encoding = 'utf-8'
    if 'keywords' in request.GET and request.GET['keywords']:
        message = '你搜索的内容为: ' + request.GET['keywords']
        keys = request.GET['keywords']
    else:
        message = '你提交了空表单'
        keys = ''
    page = request.GET['page']
    limit = request.GET['limit']
    if 'program_name' in request.GET:
        program_name = request.GET['program_name']
    else:
        program_name = Default_Program
    #  暂时未用迭代参数
    if 'version' in request.GET:
        version = request.GET['version']
    else:
        version = None
    # -------------------------
    try:
        conditions = {}
        if program_name != None and program_name != '':
            program,count1 = OperationDB.getProgram(program_name)
            if count1 != 0:
                program_id = program.id
                conditions.setdefault('program', program_id)
            else:
                rdict = {
                    'code': 0,
                    'count': 0,
                    'data': [],
                    'msg': "没有此项目"
                }
                return_json = json.dumps(rdict)
                return HttpResponse(return_json)
        else:
            program_id = None
        if version:
            iterations,count2 = OperationDB.get_iteration(program_id,version)
            iterration_id = iterations.id
            conditions.setdefault("iteration",iterration_id)
        data,totalcount = OperationDB.readBugsFromDB(keys,page,limit,conditions,true_or_false=True)
        code = 0
    except Exception as e:
        code = 1001
        totalcount = 0
        data = []
        message = 'error:查询失败\n'+ str(e)
    rdict = {
        'code': code,
        'count': totalcount,
        'data': data,
        'msg': message
    }
    return_json = json.dumps(rdict)
    return HttpResponse(return_json)

@permission_required('Bug.add_program')
@login_required
@transaction.atomic
def addProgram(request):
    if 'program_name' in request.POST:
        program_son_name = request.POST['program_name']
        try:
            program_name = returnKey(TC_Programs,program_son_name)
        except:
            rjson = json.dumps({'code': 1003, 'msg': 'TC_Programs have no program_son_name : %s !' % program_son_name})
            return HttpResponse(rjson)
    else:
        rjson = json.dumps({'code': 1003, 'msg': 'have no this param : programe_name !'})
        return HttpResponse(rjson)
    program_id = OperationDB.writeProgram(program_name)
    # son_program_id = OperationDB.writeSonProgram(program_son_name,program_id)
    if not program_id:
        rjson = json.dumps({'code': 1004, 'msg': 'write program or get program_id error!'})
    else:
        rjson = json.dumps({'code': 0, 'msg': "success",'data':{'id':program_id}})
    return HttpResponse(rjson)

@permission_required('Bug.add_iteration')
@login_required
@transaction.atomic
def addIteration(request):
    for key in ['iteration','program','s_time','e_time']:
        if key not in request.POST:
            rjson = json.dumps({'code':1002,"msg":"have no params: %s" % key})
            return HttpResponse(rjson)
    program_son_name = request.POST['program']
    root_program_name = returnKey(TC_Programs, program_son_name)
    iteration_version = request.POST['iteration']
    s_time = request.POST['s_time'] + ' 00:01'
    e_time = request.POST['e_time'] + ' 23:59'
    # 初始化项目
    program, count = OperationDB.getProgram(root_program_name)
    if count != 0:
        program_id = program.id
    else:
        rjson = json.dumps({'code': 1004, 'msg': 'db have no this program: %s' % program})
        return HttpResponse(rjson)
    iteration_id = OperationDB.write_iteration(iteration_version, program_id,s_time, e_time)
    if not iteration_id:
        rjson = json.dumps({'code': 1004, 'msg': 'write iteration or get iteration_id error!'})
    else:
        rjson = json.dumps({'code': 0, 'msg': "success",'data':{'id':iteration_id}})
    return HttpResponse(rjson)

@permission_required('Bug.add_detail')
@login_required
@transaction.atomic
def readExcelAndWrite(request):
    '''将读取excel的数据写入数据库、迭代初始化、项目初始化'''
    # print("------------> 已进入接口 readExcelAndWrite")
    # 判断参数是否完整
    for key in ['filestr','iteration','s_time','e_time','type','program']:
        if key not in request.POST:
            rjson = json.dumps({'code':1002,"msg":"have no params: %s" % key})
            return HttpResponse(rjson)
    files = request.POST['filestr']
    iterationstr = request.POST['iteration']
    s_time = request.POST['s_time'] + ' 00:01'
    e_time = request.POST['e_time'] + ' 23:59'
    son_program_name = request.POST['program']
    root_program_name = returnKey(TC_Programs, son_program_name)
    type = request.POST['type']
    filelist = json.loads(files)
    # 默认返回
    rjson = json.dumps({'code': 1001, 'msg':"请求错误"})
    # 初始化项目
    program,count = OperationDB.getProgram(root_program_name)
    if count != 0:
        program_id = program.id
    else:
        rjson = json.dumps({'code': 1004, 'msg': 'db have no this program: %s' % root_program_name})
        return HttpResponse(rjson)
    # 初始化迭代
    itera,icount = OperationDB.get_iteration(program_id,iterationstr)
    if icount != 0:
        iteration_id = itera.id
    else:
        rjson = json.dumps({'code': 1004, 'msg': 'db have no this iteration version: %s' % iterationstr})
        return HttpResponse(rjson)
    # 判断excel字段是否齐全
    for key in filelist[0].keys():
        count = 0
        for targetkey in TONG_JI_DICT:
            if key == targetkey or key in TITLE_SPECIAL_DICT_ZENTAO.keys():  #兼容各组功能模块名称不一样
                count += 1
        if count == 0 and key in TONG_JI_DICT:
            rjson = json.dumps({'code': 1003, "msg": "Excel title wrong！ have no one of these key: %s" % TITLE_SPECIAL_DICT_ZENTAO.keys()})
            return HttpResponse(rjson)
    # 换key的名称，
    try:
        newfilelist = StatisticsBugFromList.StatisticsAll_zentao(filelist,s_time,e_time)
        on_total, on_resolved, off_total, off_resolved = StatisticsBugFromList.Statistics_total_zentaoEXCEL(newfilelist)
        # 更新子项目bug统计
        OperationDB.writeSonProgram(son_program_name, program_id, on_total,on_resolved,off_total,off_resolved)
        if newfilelist != []:
            OperationDB.bugListWrite2DB(newfilelist,iteration_id,program_id,type)
        rjson = json.dumps({'code': 0, 'msg':"success"})
    except Exception as e:
        rjson = json.dumps({'code': 1004, 'msg': str(e)})
    return HttpResponse(rjson)

@permission_required('Bug.add_detail')
@login_required
@transaction.atomic
def readApiAndWrite(request):
    '''将读取Api的数据写入数据库、迭代初始化、项目初始化'''
    # print("------------> 已进入接口 readExcelAndWrite")
    # 判断参数是否完整
    for key in ['methods','iteration','s_time','e_time','type','program']:
        if key not in request.POST:
            rjson = json.dumps({'code':1002,"msg":"have no params: %s" % key})
            return HttpResponse(rjson)
    methods = request.POST['methods']
    iterationstr = request.POST['iteration']
    s_time = request.POST['s_time'] + ' 00:01'
    e_time = request.POST['e_time'] + ' 23:59'
    son_program_name = request.POST['program']
    root_program_name = returnKey(TC_Programs, son_program_name)
    type = request.POST['type']
    # 默认返回
    rjson = json.dumps({'code': 1001, 'msg':"请求错误"})
    # 初始化项目
    program,count = OperationDB.getProgram(root_program_name)
    if count != 0:
        program_id = program.id
    else:
        rjson = json.dumps({'code': 1004, 'msg': 'db have no this program: %s' % root_program_name})
        return HttpResponse(rjson)
    # 初始化迭代
    itera,icount = OperationDB.get_iteration(program_id,iterationstr)
    if icount != 0:
        iteration_id = itera.id
    else:
        rjson = json.dumps({'code': 1004, 'msg': 'db have no this iteration version: %s' % iterationstr})
        return HttpResponse(rjson)
    if methods == 'zentao':
        #  来源禅道
        pro_name = to_zentao_programs[son_program_name]
        buglist,on_total,on_resolved,off_total,off_resolved = returnBugsInfo(programName=pro_name,s_time=s_time,e_time=e_time)
        if buglist == []:
            rjson = json.dumps({'code': 0, 'msg': "没有符合条件的bug导入"})
            return HttpResponse(rjson)
    else:
        rjson = json.dumps({'code': 1005, 'msg': 'have no this methods api: %s' % methods})
        return HttpResponse(rjson)
    # 判断excel字段是否齐全
    for key in buglist[0].keys():
        count = 0
        for targetkey in TONG_JI_DICT:
            if key == targetkey or key in TITLE_SPECIAL_DICT_ZENTAO.keys():  #兼容各组功能模块名称不一样
                count += 1
        if count == 0 and key in TONG_JI_DICT:
            rjson = json.dumps({'code': 1003, "msg": "Excel title wrong！ have no one of these key: %s" % TITLE_SPECIAL_DICT_ZENTAO.keys()})
            return HttpResponse(rjson)

    # 写数据库
    try:
        # 更新子项目bug统计
        OperationDB.writeSonProgram(son_program_name, program_id, on_total,on_resolved,off_total,off_resolved)
        # 写入数据库详细bug
        OperationDB.bugListWrite2DB(buglist,iteration_id,program_id,type,methods='api')
        rjson = json.dumps({'code': 0, 'msg':"success"})
    except Exception as e:
        rjson = json.dumps({'code': 1004, 'msg': str(e)})
    return HttpResponse(rjson)

@permission_required('Bug.change_testdetail')
@login_required
@transaction.atomic
def addRuncases(request):
    '''将读取Api的用例执行数据写入数据库'''
    for key in ['methods','iteration','s_time','e_time','program']:
        if key not in request.POST:
            rjson = json.dumps({'code':1002,"msg":"have no params: %s" % key})
            return HttpResponse(rjson)
    methods = request.POST['methods']
    iterationstr = request.POST['iteration']
    s_time = request.POST['s_time'] + ' 00:01'
    e_time = request.POST['e_time'] + ' 23:59'
    son_program_name = request.POST['program']
    root_program_name = returnKey(TC_Programs, son_program_name)
    # 默认返回
    rjson = json.dumps({'code': 1001, 'msg':"请求错误"})
    # 初始化项目
    program,count = OperationDB.getProgram(root_program_name)
    son_program,son_count = OperationDB.getSonProgram(son_program_name)
    if count != 0:
        program_id = program.id
    else:
        rjson = json.dumps({'code': 1004, 'msg': 'db have no this program: %s' % root_program_name})
        return HttpResponse(rjson)
    if son_count != 0:
        son_program_id = son_program[0].id
    else:
        rjson = json.dumps({'code': 1004, 'msg': 'db have no this son_program: %s' % son_program_name})
        return HttpResponse(rjson)
    # 初始化迭代
    itera,icount = OperationDB.get_iteration(program_id,iterationstr)
    if icount != 0:
        iteration_id = itera.id
    else:
        rjson = json.dumps({'code': 1004, 'msg': 'db have no this iteration version: %s' % iterationstr})
        return HttpResponse(rjson)
    if methods == 'zentao':
        #  来源禅道
        zentao_programe_name = to_zentao_programs[son_program_name]
        cases = returnRunCases(zentao_programe_name,stime=s_time,etime=e_time)
        if cases == []:
            rjson = json.dumps({'code': 0, 'msg': "没有符合条件的用例执行数据导入"})
            return HttpResponse(rjson)
    else:
        rjson = json.dumps({'code': 1005, 'msg': 'have no this methods api: %s' % methods})
        return HttpResponse(rjson)

    # 写数据库
    try:
        # 更新testdetail表
        OperationDB.writeTestDetail(iteration_id, son_program_id, s_time, e_time, cases)
        rjson = json.dumps({'code': 0, 'msg':"success"})
    except Exception as e:
        rjson = json.dumps({'code': 1004, 'msg': str(e)})
    return HttpResponse(rjson)

@permission_required('Bug.change_testdetail')
@permission_required('Bug.view_testdetail')
@login_required
@transaction.atomic
def updateTesterInfo(request):
    '''将读取Api的用例执行数据写入数据库'''
    for key in ['tester', 'program', 'iteration', 'lostcount','testdelaytime','autofinishrate', 's_time', 'e_time']:
        if key not in request.POST:
            rjson = json.dumps({'code':1002,"msg":"have no params: %s" % key})
            return HttpResponse(rjson)
    tester = request.POST['tester']
    lostcount = request.POST['lostcount']
    testdelaytime = request.POST['testdelaytime']
    autofinishrate = request.POST['autofinishrate']
    iterationstr = request.POST['iteration']
    s_time = request.POST['s_time'] + ' 00:01'
    e_time = request.POST['e_time'] + ' 23:59'
    son_program_name = request.POST['program']
    root_program_name = returnKey(TC_Programs, son_program_name)
    # 默认返回
    rjson = json.dumps({'code': 1001, 'msg':"请求错误"})
    # 初始化项目
    program,count = OperationDB.getProgram(root_program_name)
    son_program,son_count = OperationDB.getSonProgram(son_program_name)
    if count != 0:
        program_id = program.id
    else:
        rjson = json.dumps({'code': 1004, 'msg': 'db have no this program: %s' % root_program_name})
        return HttpResponse(rjson)
    if son_count != 0:
        son_program_id = son_program[0].id
    else:
        rjson = json.dumps({'code': 1004, 'msg': 'db have no this son_program: %s' % son_program_name})
        return HttpResponse(rjson)
    # 初始化迭代
    itera,icount = OperationDB.get_iteration(program_id,iterationstr)
    if icount != 0:
        iteration_id = itera.id
    else:
        rjson = json.dumps({'code': 1004, 'msg': 'db have no this iteration version: %s' % iterationstr})
        return HttpResponse(rjson)
    try:
        condition = {"iteration_id": iteration_id, "son_program_id": son_program_id,"tester": tester}
        update = {}
        if lostcount != None:
            lostcount = int(lostcount)
            update["lost_BugCount"] = lostcount
        if testdelaytime != None:
            testdelaytime = int(testdelaytime)
            update["testDelayTime"] = testdelaytime
        if autofinishrate != None:
            autofinishrate = int(autofinishrate)
            update["autoFinishRate"] = autofinishrate
    except:
        rjson = json.dumps({'code': 1005, 'msg': 'lostcount type is not int'})
        return HttpResponse(rjson)

    # 写数据库
    try:
        # 更新testdetail表
        OperationDB.updateTestDetail(condition,update)
        rjson = json.dumps({'code': 0, 'msg':"success"})
    except Exception as e:
        rjson = json.dumps({'code': 1004, 'msg': str(e)})
    return HttpResponse(rjson)

@permission_required('Bug.change_developdetail')
@permission_required('Bug.view_developdetail')
@login_required
@transaction.atomic
def updateDeveloperInfo(request):
    '''录入开发人员数据写入数据库'''
    for key in ['developer', 'program', 'iteration', 'delaytime', 'smokefailed', 'reopentimes', 's_time', 'e_time']:
        if key not in request.POST:
            rjson = json.dumps({'code':1002,"msg":"have no params: %s" % key})
            return HttpResponse(rjson)
    developer = request.POST['developer']
    delaytime = request.POST['delaytime']
    smokefailed = request.POST['smokefailed']
    reopentimes = request.POST['reopentimes']
    iterationstr = request.POST['iteration']
    s_time = request.POST['s_time'] + ' 00:01'
    e_time = request.POST['e_time'] + ' 23:59'
    son_program_name = request.POST['program']
    root_program_name = returnKey(TC_Programs, son_program_name)
    # 默认返回
    rjson = json.dumps({'code': 1001, 'msg':"请求错误"})
    # 初始化项目
    program,count = OperationDB.getProgram(root_program_name)
    son_program,son_count = OperationDB.getSonProgram(son_program_name)
    if count != 0:
        program_id = program.id
    else:
        rjson = json.dumps({'code': 1004, 'msg': 'db have no this program: %s' % root_program_name})
        return HttpResponse(rjson)
    if son_count != 0:
        son_program_id = son_program[0].id
    else:
        rjson = json.dumps({'code': 1004, 'msg': 'db have no this son_program: %s' % son_program_name})
        return HttpResponse(rjson)
    # 初始化迭代
    itera,icount = OperationDB.get_iteration(program_id,iterationstr)
    if icount != 0:
        iteration_id = itera.id
    else:
        rjson = json.dumps({'code': 1004, 'msg': 'db have no this iteration version: %s' % iterationstr})
        return HttpResponse(rjson)
    try:
        condition = {"iteration_id": iteration_id, "son_program_id": son_program_id,"developer": developer}
        update = {}
        if delaytime != None:
            delaytime = int(delaytime)
            update["delayTestTimes"] = delaytime
        if smokefailed != None:
            smokefailed = int(smokefailed)
            update["failedSmokeCount"] = smokefailed
        if reopentimes != None:
            reopentimes = int(reopentimes)
            update["reopenBugCount"] = reopentimes
    except:
        rjson = json.dumps({'code': 1005, 'msg': 'data type is not int'})
        return HttpResponse(rjson)

    # 写数据库
    try:
        # 更新testdetail表
        OperationDB.updateDevDetail(condition,update)
        rjson = json.dumps({'code': 0, 'msg':"success"})
    except Exception as e:
        rjson = json.dumps({'code': 1004, 'msg': str(e)})
    return HttpResponse(rjson)

@permission_required('Bug.change_detail')
@login_required
@transaction.atomic
def updateProgramTechScores(request):
    '''基础分评估：根据项目主管、技术主管 主观评分'''
    for key in ['user', 'program', 'iteration', 'pscores', 'tscores','s_time', 'e_time']:
        if key not in request.POST:
            rjson = json.dumps({'code':1002,"msg":"have no params: %s" % key})
            return HttpResponse(rjson)
    username = request.POST['user']
    program_scores = request.POST['pscores']
    tech_scores = request.POST['tscores']
    if 'techScoreDesc' not in request.POST:
        p_score_Desc = '没有说明'
    else:
        p_score_Desc = request.POST['techScoreDesc']
    if 'programScoreDesc' not in request.POST:
        t_score_Desc = '没有说明'
    else:
        t_score_Desc = request.POST['programScoreDesc']
    iterationstr = request.POST['iteration']
    s_time = request.POST['s_time'] + ' 00:01'
    e_time = request.POST['e_time'] + ' 23:59'
    son_program_name = request.POST['program']
    root_program_name = returnKey(TC_Programs, son_program_name)
    # 默认返回
    rjson = json.dumps({'code': 1001, 'msg':"请求错误"})
    # 初始化项目
    program,count = OperationDB.getProgram(root_program_name)
    son_program,son_count = OperationDB.getSonProgram(son_program_name)
    if count != 0:
        program_id = program.id
    else:
        rjson = json.dumps({'code': 1004, 'msg': 'db have no this program: %s' % root_program_name})
        return HttpResponse(rjson)
    if son_count != 0:
        son_program_id = son_program[0].id
    else:
        rjson = json.dumps({'code': 1004, 'msg': 'db have no this son_program: %s' % son_program_name})
        return HttpResponse(rjson)
    # 初始化迭代
    itera,icount = OperationDB.get_iteration(program_id,iterationstr)
    if icount != 0:
        iteration_id = itera.id
    else:
        rjson = json.dumps({'code': 1004, 'msg': 'db have no this iteration version: %s' % iterationstr})
        return HttpResponse(rjson)

    users = User.objects.filter(groups__name__contains="测试")
    userlist = [user.first_name for user in users]
    dusers = User.objects.filter(groups__name__contains="开发")
    duserlist = [user.first_name for user in dusers]
    try:
        if username in userlist:
            condition = {"iteration_id": iteration_id, "son_program_id": son_program_id,"tester": username}
        else:
            condition = {"iteration_id": iteration_id, "son_program_id": son_program_id,"developer": username}
        update = {'programScoreDescription': p_score_Desc, 'techScoreDescription': t_score_Desc}
        if program_scores != None and program_scores != '':
            program_scores = float(program_scores)
            update["ProgramScores"] = program_scores
        if tech_scores != None and tech_scores != '':
            tech_scores = float(tech_scores)
            update["TechScores"] = tech_scores
    except:
        rjson = json.dumps({'code': 1005, 'msg': 'data type is not int'})
        return HttpResponse(rjson)

    #分数判断不能大于10
    try:
        ps = float(program_scores)
    except:
        ps = 0
    try:
        ts = float(tech_scores)
    except:
        ts = 0
    if (ps > 10) or (ts > 10):
        rjson = json.dumps({'code': 1002, 'msg': '分数不能大于10'})
        return HttpResponse(rjson)

    # 写数据库
    try:
        # 更新testdetail表
        if username in userlist:
            OperationDB.updateTestDetail(condition,update)
        else:
            OperationDB.updateDevDetail(condition, update)
        rjson = json.dumps({'code': 0, 'msg':"success"})
    except Exception as e:
        rjson = json.dumps({'code': 1004, 'msg': str(e)})
    return HttpResponse(rjson)

@permission_required('Bug.change_detail')
@login_required
@transaction.atomic
def updateProgramTechScores_new(request):
    '''基础分评估：根据工作量完成度、特殊贡献'''
    for key in ['user', 'program', 'iteration', 'pscores', 'tscores','s_time', 'e_time']:
        if key not in request.POST:
            rjson = json.dumps({'code':1002,"msg":"have no params: %s" % key})
            return HttpResponse(rjson)
    username = request.POST['user']
    base_scores = request.POST['pscores']
    tech_scores = request.POST['tscores']
    if 'techScoreDesc' not in request.POST:
        p_score_Desc = '没有说明'
    else:
        p_score_Desc = request.POST['techScoreDesc']
    if 'programScoreDesc' not in request.POST:
        t_score_Desc = '没有说明'
    else:
        t_score_Desc = request.POST['programScoreDesc']
    iterationstr = request.POST['iteration']
    s_time = request.POST['s_time'] + ' 00:01'
    e_time = request.POST['e_time'] + ' 23:59'
    son_program_name = request.POST['program']
    root_program_name = returnKey(TC_Programs, son_program_name)
    # 默认返回
    rjson = json.dumps({'code': 1001, 'msg':"请求错误"})
    # 初始化项目
    program,count = OperationDB.getProgram(root_program_name)
    son_program,son_count = OperationDB.getSonProgram(son_program_name)
    if count != 0:
        program_id = program.id
    else:
        rjson = json.dumps({'code': 1004, 'msg': 'db have no this program: %s' % root_program_name})
        return HttpResponse(rjson)
    if son_count != 0:
        son_program_id = son_program[0].id
    else:
        rjson = json.dumps({'code': 1004, 'msg': 'db have no this son_program: %s' % son_program_name})
        return HttpResponse(rjson)
    # 初始化迭代
    itera,icount = OperationDB.get_iteration(program_id,iterationstr)
    if icount != 0:
        iteration_id = itera.id
    else:
        rjson = json.dumps({'code': 1004, 'msg': 'db have no this iteration version: %s' % iterationstr})
        return HttpResponse(rjson)

    users = User.objects.filter(groups__name__contains="测试")
    userlist = [user.first_name for user in users]
    dusers = User.objects.filter(groups__name__contains="开发")
    duserlist = [user.first_name for user in dusers]
    try:
        if username in userlist:
            condition = {"iteration_id": iteration_id, "son_program_id": son_program_id,"tester": username}
        else:
            condition = {"iteration_id": iteration_id, "son_program_id": son_program_id,"developer": username}
        update = {'programScoreDescription': p_score_Desc, 'techScoreDescription': t_score_Desc}
        if base_scores != None and base_scores != '':
            base_scores = float(base_scores)
            update["ProgramScores"] = round(base_scores * 10, 1) # base_scores 是一个工作量完成百分比，因此要乘以10
        if tech_scores != None and tech_scores != '':
            tech_scores = float(tech_scores)
            update["TechScores"] = round(tech_scores, 1)
    except:
        rjson = json.dumps({'code': 1005, 'msg': 'data type is not int'})
        return HttpResponse(rjson)

    #分数判断不能大于10
    try:
        ps = float(base_scores)
    except:
        ps = 0
    try:
        ts = float(tech_scores)
    except:
        ts = 0
    if (ps > 1) :
        rjson = json.dumps({'code': 1002, 'msg': '完成工作量不能比计划工作量更大'})
        return HttpResponse(rjson)
    if (ts > 1):
        rjson = json.dumps({'code': 1002, 'msg': '加分不能大于1'})
        return HttpResponse(rjson)

    # 写数据库
    try:
        # 更新testdetail表
        if username in userlist:
            OperationDB.updateTestDetail(condition, update)
        else:
            OperationDB.updateDevDetail(condition, update)
        rjson = json.dumps({'code': 0, 'msg':"success"})
    except Exception as e:
        rjson = json.dumps({'code': 1004, 'msg': str(e)})
    return HttpResponse(rjson)

@permission_required('Bug.change_iteration')
@login_required
class iteration_update_api(APIView):
    def get(self, request, *args, **kwargs):
        if 'limit' in request.GET and request.GET['limit']:
            limit = int(request.GET['limit'])
        else:
            limit = 7
        if 'program' in request.GET and request.GET['program']:
            program_name = request.GET['program']
        else:
            program_name = Default_Program
        if 'offonline' in request.GET and request.GET['offonline']:
            offonline = request.GET['offonline']
        else:
            offonline = 'offline'
        try:
            line, versions = bugline_iteration(program_name,offonline,useto='pic',limit=limit)
            line_base = line.dump_options_with_quotes()
            re_line = json.loads(line_base)
        except:
            re_line = ''
        return json_response(re_line)

@permission_required('Bug.view_iteration')
@login_required
def iteration(request):
    contextdict = {}
    if 'limit' in request.GET and request.GET['limit']:
        limit = int(request.GET['limit'])
    else:
        limit = 7
    if 'program' in request.GET and request.GET['program']:
        program_name = request.GET['program']
    else:
        program_name = Default_Program
    if 'offonline' in request.GET and request.GET['offonline']:
        offonline = request.GET['offonline']
    else:
        offonline = 'offline'
    line,versions = bugline_iteration(program_name,offonline,useto='pic',limit=limit)
    contextdict['quality_style'] = 'color: #fff;font-weight:bold'
    contextdict['view_v2'] = 'layui-nav-itemed'
    contextdict['iteration_v2_style'] = 'background-color: #009688;color: #fff;'
    contextdict['myechart'] = line.render_embed()
    contextdict['versions_fileds'] = json.dumps(versions)
    contextdict['programs'] = json.dumps(list(TC_Programs.keys()))
    return render(request,'quality/iteration.html',contextdict)

@permission_required('Bug.change_iteration')
@login_required
def iteration_update(request):
    '''更新迭代统计图表'''
    if 'limit' in request.GET and request.GET['limit']:
        limit = int(request.GET['limit'])
    else:
        limit = 7
    if 'program' in request.GET and request.GET['program']:
        program_name = request.GET['program']
    else:
        program_name = Default_Program
    if 'offonline' in request.GET and request.GET['offonline']:
        offonline = request.GET['offonline']
    else:
        offonline = 'offline'
    try:
        line, versions = bugline_iteration(program_name,offonline,useto='pic',limit=limit)
        line_base = line.dump_options_with_quotes()
        re_line = json.loads(line_base)
    except:
        re_line = ''
    return json_response(re_line)

@permission_required('Bug.view_iteration')
@login_required
def query_bugs_iteration(request):
    request.encoding = 'utf-8'
    if 'limit' in request.GET and request.GET['limit']:
        limit = int(request.GET['limit'])
    else:
        limit = 7
    if 'program' in request.GET and request.GET['program']:
        program_name = request.GET['program']
    else:
        program_name = Default_Program
    if 'offonline' in request.GET and request.GET['offonline']:
        offonline = request.GET['offonline']
    else:
        offonline = 'offline'
    try:
        data,versions = bugline_iteration(program_name,type=offonline,useto='data',limit=limit)
        code = 0
        totalcount = len(versions)
        message = 'success'
    except Exception as e:
        code = 1001
        totalcount = 0
        data = []
        versions = []
        message = 'error:查询失败\n' + str(e)
    rdict = {
        'code': code,
        'count': totalcount,
        'data': data,
        'versions': versions,
        'msg': message
    }
    return_json = json.dumps(rdict)
    return HttpResponse(return_json)

@permission_required('Bug.view_detail')
@login_required
def recently(request):
    contextdict = {}
    if 'limit' in request.GET and request.GET['limit']:
        limit = int(request.GET['limit'])
    else:
        limit = 7
    if 'program' in request.GET and request.GET['program']:
        program_name = request.GET['program']
    else:
        program_name = Default_Program
    if 'offonline' in request.GET and request.GET['offonline']:
        offonline = request.GET['offonline']
    else:
        offonline = 'offline'
    line,versions = bugline(program_name,offonline,useto='pic',limit=limit)
    contextdict['quality_style'] = 'color: #fff;font-weight:bold'
    contextdict['view_v2'] = 'layui-nav-itemed'
    contextdict['recently_v2_style'] = 'background-color: #009688;color: #fff;'
    contextdict['myechart'] = line.render_embed()
    contextdict['versions_fileds'] = json.dumps(versions)
    contextdict['programs'] = json.dumps(list(TC_Programs.keys()))
    return render(request,'quality/recently.html',contextdict)

@permission_required('Bug.view_detail')
@login_required
def recently_update(request):
    '''更新迭代统计图表'''
    if 'limit' in request.GET and request.GET['limit']:
        limit = int(request.GET['limit'])
    else:
        limit = 7
    if 'program' in request.GET and request.GET['program']:
        program_name = request.GET['program']
    else:
        program_name = Default_Program
    if 'offonline' in request.GET and request.GET['offonline']:
        offonline = request.GET['offonline']
    else:
        offonline = 'offline'
    try:
        line, versions = bugline(program_name,offonline,useto='pic',limit=limit)
        line_base = line.dump_options_with_quotes()
        re_line = json.loads(line_base)
    except:
        re_line = ''
    return json_response(re_line)

@permission_required('Bug.view_detail')
@login_required
def query_bugs_recently(request):
    request.encoding = 'utf-8'
    if 'limit' in request.GET and request.GET['limit']:
        limit = int(request.GET['limit'])
    else:
        limit = 7
    if 'program' in request.GET and request.GET['program']:
        program_name = request.GET['program']
    else:
        program_name = Default_Program
    if 'offonline' in request.GET and request.GET['offonline']:
        offonline = request.GET['offonline']
    else:
        offonline = 'offline'
    try:
        data,versions = bugline(program_name,type=offonline,useto='data',limit=limit)
        code = 0
        totalcount = len(versions)
        message = 'success'
    except Exception as e:
        code = 1001
        totalcount = 0
        data = []
        versions = []
        message = 'error:查询失败\n' + str(e)
    rdict = {
        'code': code,
        'count': totalcount,
        'data': data,
        'versions': versions,
        'msg': message
    }
    return_json = json.dumps(rdict)
    return HttpResponse(return_json)

@permission_required('Bug.view_iteration')
@login_required
def getIterations(request):
    for key in ['program']:
        if key not in request.GET:
            rjson = json.dumps({'code':1002,"msg":"have no params: %s" % key})
            return HttpResponse(rjson)
    program_name = request.GET['program']
    program,count = OperationDB.getProgram(program_name)
    if count != 0:
        # ids,versions,count = OperationDB.getIterations({"program_id":program.id})
        versions_dict = OperationDB.readIterationsAccordProgramID(program.id)
        ids = versions_dict['ids']
        versions = versions_dict['versions']
    else:
        versions = []
    rejson = json_response(versions[::-1])
    return HttpResponse(rejson)

@permission_required('Bug.view_iteration')
@login_required
def getRootProgramIterations(request):
    for key in ['program']:
        if key not in request.GET:
            rjson = json.dumps({'code':1002,"msg":"have no params: %s" % key})
            return HttpResponse(rjson)
    program_name = request.GET['program']
    root_program_name = returnKey(TC_Programs,program_name)
    program,count = OperationDB.getProgram(root_program_name)
    if count != 0:
        # ids,versions,count = OperationDB.getIterations({"program_id":program.id})
        versions_dict = OperationDB.readIterationsAccordProgramID(program.id)
        ids = versions_dict['ids']
        versions = versions_dict['versions']
    else:
        versions = []
    i=1
    rj = {}
    for one in versions[::-1]:
        rj[str(i)] = one
        i += 1
    rejson = json_response(rj)
    return HttpResponse(rejson)

@permission_required('Bug.view_iteration')
@login_required
def getRootProgramTargetIterationInfo(request):
    for key in ['program','iteration_name']:
        if key not in request.GET:
            rjson = json.dumps({'code':1002,"msg":"have no params: %s" % key})
            return HttpResponse(rjson)
    program_name = request.GET['program']
    iteration_name = request.GET['iteration_name']
    root_program_name = returnKey(TC_Programs,program_name)
    program,count = OperationDB.getProgram(root_program_name)
    if count != 0:
        versions_dict = OperationDB.readIterationsAccordProgramID(program.id)
        versions = versions_dict['versions']
    else:
        versions = []
    i=1
    rj = {}
    for i in list(range(len(versions))):
        if iteration_name == versions[i]:
            id = versions_dict['ids'][i]
            start_time = versions_dict['start_times'][i].split(' ')[0]
            end_time = versions_dict['end_times'][i].split(' ')[0]
            rj = {
                "id":id,
                "iteration_name":iteration_name,
                "start_time":start_time,
                "end_time":end_time,
            }
            break
    rejson = json_response(rj)
    return HttpResponse(rejson)

@permission_required('Bug.view_moudle')
@login_required
def module(request):
    if 'offonline' in request.GET and request.GET['offonline']:
        offonline = request.GET['offonline']
    else:
        offonline = 'offline'
    if 'program' in request.GET and request.GET['program']:
        program_name = request.GET['program']
    else:
        program_name = Default_Program
    program, count = OperationDB.getProgram(program_name)
    if count != 0:
        # ids,versions,count = OperationDB.getIterations({"program_id":program.id})
        versions_dict = OperationDB.readIterationsAccordProgramID(program.id)
        versions = versions_dict['versions']
    else:
        versions = []
        module_fields = []
    if versions != []:
        if 'version' in request.GET and request.GET['version']:
            version_str = request.GET['version']
        else:
            version_str = versions[::-1][0]
        bar,module_fields = bugBar_mudle(version_str,program_name,offonline,useto='pic')
    contextdict = {}
    contextdict['quality_style'] = 'color: #fff;font-weight:bold'
    contextdict['view_v2'] = 'layui-nav-itemed'
    contextdict['bugModule_v2_style'] = 'background-color: #009688;color: #fff;'
    if versions != []:
        contextdict['myechart'] = bar.render_embed()
    contextdict['modules_fileds'] = json.dumps(module_fields)
    contextdict['versions'] = json.dumps(versions[::-1])
    contextdict['programs'] = json.dumps(list(TC_Programs.keys()))
    return render(request, 'quality/module.html', contextdict)

@permission_required('Bug.view_moudle')
@login_required
def module_update(request):
    '''更新模块统计图表'''
    if 'program' in request.GET and request.GET['program']:
        program_name = request.GET['program']
    else:
        program_name = Default_Program
    program, count = OperationDB.getProgram(program_name)
    if count != 0:
        versions_dict = OperationDB.readIterationsAccordProgramID(program.id)
        versions = versions_dict['versions']
    else:
        versions = []
    if 'version' in request.GET and request.GET['version']:
        versionstr = request.GET['version']
    else:
        if versions != []:
            versionstr = versions[::-1][0]
        else:
            versionstr = ''
    if 'offonline' in request.GET and request.GET['offonline']:
        offonline = request.GET['offonline']
    else:
        offonline = 'offline'
    try:
        bar, versions = bugBar_mudle(versionstr,program_name,offonline,useto='pic')
        bar_base = bar.dump_options_with_quotes()
        re_bar = json.loads(bar_base)
    except:
        re_bar = ''
    return json_response(re_bar)

@permission_required('Bug.view_moudle')
@login_required
def query_bugs_module(request):
    request.encoding = 'utf-8'
    if 'program' in request.GET and request.GET['program']:
        program_name = request.GET['program']
    else:
        program_name = Default_Program
    program, count = OperationDB.getProgram(program_name)
    if count != 0:
        versions_dict = OperationDB.readIterationsAccordProgramID(program.id)
        versions = versions_dict['versions']
    else:
        versions = []
    if 'version' in request.GET and request.GET['version']:
        versionstr = request.GET['version']
    else:
        if versions != []:
            versionstr = versions[::-1][0]
        else:
            versionstr = ''
    if 'offonline' in request.GET and request.GET['offonline']:
        offonline = request.GET['offonline']
    else:
        offonline = 'offline'
    try:
        data, versions = bugBar_mudle(versionstr,program_name, type=offonline, useto='data')
        code = 0
        totalcount = len(versions)
        message = 'success'
    except Exception as e:
        code = 1001
        totalcount = 0
        data = []
        versions = []
        message = 'error:查询失败\n' + str(e)
    rdict = {
        'code': code,
        'count': totalcount,
        'data': data,
        'versions': versions,
        'msg': message
    }
    return_json = json.dumps(rdict)
    return HttpResponse(return_json)

@permission_required('Bug.view_developdetail')
@login_required
def developer(request):
    devtype = 'all'
    if 'offonline' in request.GET and request.GET['offonline']:
        offonline = request.GET['offonline']
    else:
        offonline = 'offline'
    if 'program' in request.GET and request.GET['program']:
        program_name = request.GET['program']
    else:
        program_name = Default_Program
    program, count = OperationDB.getProgram(program_name)
    if count != 0:
        # ids,versions,count = OperationDB.getIterations({"program_id":program.id})
        versions_dict = OperationDB.readIterationsAccordProgramID(program.id)
        versions = versions_dict['versions']
    else:
        versions = []
        module_fields = []
    if versions != []:
        if 'version' in request.GET and request.GET['version']:
            version_str = request.GET['version']
        else:
            version_str = versions[::-1][0]
        bar,module_fields = bugBar_developer(version_str,program_name,devtype,useto='pic')
    contextdict = {}
    contextdict['quality_style'] = 'color: #fff;font-weight:bold'
    contextdict['view_v2'] = 'layui-nav-itemed'
    contextdict['developQuality_v2_style'] = 'background-color: #009688;color: #fff;'
    if versions != []:
        contextdict['myechart'] = bar.render_embed()
    contextdict['modules_fileds'] = json.dumps(module_fields)
    contextdict['versions'] = json.dumps(versions[::-1])
    contextdict['programs'] = json.dumps(list(TC_Programs.keys()))
    return render(request, 'quality/developer.html', contextdict)

@permission_required('Bug.view_developdetail')
@login_required
def developer_update(request):
    '''更新模块统计图表'''
    if 'program' in request.GET and request.GET['program']:
        program_name = request.GET['program']
    else:
        program_name = Default_Program
    program, count = OperationDB.getProgram(program_name)
    if count != 0:
        versions_dict = OperationDB.readIterationsAccordProgramID(program.id)
        versions = versions_dict['versions']
    else:
        versions = []
    if 'version' in request.GET and request.GET['version']:
        versionstr = request.GET['version']
    else:
        if versions != []:
            versionstr = versions[::-1][0]
        else:
            versionstr = ''
    if 'devtype' in request.GET and request.GET['devtype']:
        devtype = request.GET['devtype']
    else:
        devtype = 'all'
    try:
        bar, versions = bugBar_developer(versionstr,program_name,devtype,useto='pic')
        bar_base = bar.dump_options_with_quotes()
        re_bar = json.loads(bar_base)
    except:
        re_bar = ''
    return json_response(re_bar)

@permission_required('Bug.view_developdetail')
@login_required
def query_bugs_developer(request):
    request.encoding = 'utf-8'
    if 'program' in request.GET and request.GET['program']:
        program_name = request.GET['program']
    else:
        program_name = Default_Program
    program, count = OperationDB.getProgram(program_name)
    if count != 0:
        versions_dict = OperationDB.readIterationsAccordProgramID(program.id)
        versions = versions_dict['versions']
    else:
        versions = []
    if 'version' in request.GET and request.GET['version']:
        versionstr = request.GET['version']
    else:
        if versions != []:
            versionstr = versions[::-1][0]
        else:
            versionstr = ''
    if 'offonline' in request.GET and request.GET['offonline']:
        offonline = request.GET['offonline']
    else:
        offonline = 'offline'
    if 'devtype' in request.GET and request.GET['devtype']:
        devtype = request.GET['devtype']
    else:
        devtype = 'all'
    try:
        data, versions = bugBar_developer(versionstr,program_name, type=devtype, useto='data')
        code = 0
        if devtype == 'bug':
            data = data[:5]
        elif devtype == 'rate':
            data = data[5:7]
        elif devtype == 'ctest':
            data = data[7:9]
        elif devtype == 'scores':
            data = data[11:12]
        elif devtype == 'totalscores':
            data = data[12:]
        else:
            data = data[:9] + data[11:12]
        totalcount = len(versions)
        message = 'success'
    except Exception as e:
        code = 1001
        totalcount = 0
        data = []
        versions = []
        message = 'error:查询失败\n' + str(e)
    rdict = {
        'code': code,
        'count': totalcount,
        'data': data,
        'versions': versions,
        'msg': message
    }
    return_json = json.dumps(rdict)
    return HttpResponse(return_json)

@permission_required('Bug.view_testdetail')
@login_required
def tester(request):
    testtype = 'all'
    if 'program' in request.GET and request.GET['program']:
        program_name = request.GET['program']
    else:
        program_name = Default_Program
    program, count = OperationDB.getProgram(program_name)
    if count != 0:
        versions_dict = OperationDB.readIterationsAccordProgramID(program.id)
        versions = versions_dict['versions']
    else:
        versions = []
        module_fields = []
    if versions != []:
        if 'version' in request.GET and request.GET['version']:
            version_str = request.GET['version']
        else:
            version_str = versions[::-1][0]
        bar,module_fields = bugBar_tester(version_str,program_name,testtype,useto='pic')
    contextdict = {}
    contextdict['quality_style'] = 'color: #fff;font-weight:bold'
    contextdict['view_v2'] = 'layui-nav-itemed'
    contextdict['testerQuality_v2_style'] = 'background-color: #009688;color: #fff;'
    if versions != []:
        contextdict['myechart'] = bar.render_embed()
    contextdict['modules_fileds'] = json.dumps(module_fields)
    contextdict['versions'] = json.dumps(versions[::-1])
    contextdict['programs'] = json.dumps(list(TC_Programs.keys()))
    return render(request, 'quality/tester.html', contextdict)

@permission_required('Bug.view_testdetail')
@login_required
def tester_update(request):
    '''更新模块统计图表'''
    if 'program' in request.GET and request.GET['program']:
        program_name = request.GET['program']
    else:
        program_name = Default_Program
    program, count = OperationDB.getProgram(program_name)
    if count != 0:
        versions_dict = OperationDB.readIterationsAccordProgramID(program.id)
        versions = versions_dict['versions']
    else:
        versions = []
    if 'version' in request.GET and request.GET['version']:
        versionstr = request.GET['version']
    else:
        if versions != []:
            versionstr = versions[::-1][0]
        else:
            versionstr = ''
    if 'testtype' in request.GET and request.GET['testtype']:
        testtype = request.GET['testtype']
    else:
        testtype = 'all'
    try:
        bar, versions = bugBar_tester(versionstr,program_name,testtype,useto='pic')
        bar_base = bar.dump_options_with_quotes()
        re_bar = json.loads(bar_base)
    except:
        re_bar = ''
    return json_response(re_bar)

@permission_required('Bug.view_testdetail')
@login_required
def query_bugs_tester(request):
    request.encoding = 'utf-8'
    if 'program' in request.GET and request.GET['program']:
        program_name = request.GET['program']
    else:
        program_name = Default_Program
    program, count = OperationDB.getProgram(program_name)
    if count != 0:
        versions_dict = OperationDB.readIterationsAccordProgramID(program.id)
        versions = versions_dict['versions']
    else:
        versions = []
    if 'version' in request.GET and request.GET['version']:
        versionstr = request.GET['version']
    else:
        if versions != []:
            versionstr = versions[::-1][0]
        else:
            versionstr = ''
    if 'testtype' in request.GET and request.GET['testtype']:
        testtype = request.GET['testtype']
    else:
        testtype = 'all'
    offonline = 'all'
    try:
        data, versions = bugBar_tester(versionstr,program_name, type=offonline, useto='data')
        code = 0
        if testtype == 'bug':
            data = data[:6]
        elif testtype == 'case':
            data = data[6:15]
        elif testtype == 'rate':
            data = data[15:22]
        elif testtype == 'scores':
            data = data[24:25]
        elif testtype == 'totalscores':
            data = data[25:]
        else:
            data = data[:22] + data[24:25]
        totalcount = len(versions)
        message = 'success'
    except Exception as e:
        code = 1001
        totalcount = 0
        data = []
        versions = []
        message = 'error:查询失败\n' + str(e)
    rdict = {
        'code': code,
        'count': totalcount,
        'data': data,
        'versions': versions,
        'msg': message
    }
    return_json = json.dumps(rdict)
    return HttpResponse(return_json)

@permission_required('Bug.view_type')
@login_required
def bugtype(request):
    if 'offonline' in request.GET and request.GET['offonline']:
        offonline = request.GET['offonline']
    else:
        offonline = 'offline'
    if 'program' in request.GET and request.GET['program']:
        program_name = request.GET['program']
    else:
        program_name = Default_Program
    program, count = OperationDB.getProgram(program_name)
    if count != 0:
        # ids,versions,count = OperationDB.getIterations({"program_id":program.id})
        versions_dict = OperationDB.readIterationsAccordProgramID(program.id)
        versions = versions_dict['versions']
    else:
        versions = []
        module_fields = []
    if versions != []:
        if 'version' in request.GET and request.GET['version']:
            version_str = request.GET['version']
        else:
            version_str = versions[::-1][0]
        pie,module_fields = bugPie_type(version_str,program_name,offonline,useto='pic')
    contextdict = {}
    contextdict['quality_style'] = 'color: #fff;font-weight:bold'
    contextdict['view_v2'] = 'layui-nav-itemed'
    contextdict['bugType_v2_style'] = 'background-color: #009688;color: #fff;'
    if versions != []:
        contextdict['myechart'] = pie.render_embed()
    contextdict['modules_fileds'] = json.dumps(module_fields)
    contextdict['versions'] = json.dumps(versions[::-1])
    contextdict['programs'] = json.dumps(list(TC_Programs.keys()))
    return render(request, 'quality/type.html', contextdict)

@permission_required('Bug.view_type')
@login_required
def type_update(request):
    '''更新缺陷类型统计图表'''
    if 'program' in request.GET and request.GET['program']:
        program_name = request.GET['program']
    else:
        program_name = Default_Program
    program, count = OperationDB.getProgram(program_name)
    if count != 0:
        versions_dict = OperationDB.readIterationsAccordProgramID(program.id)
        versions = versions_dict['versions']
    else:
        versions = []
    if 'version' in request.GET and request.GET['version']:
        versionstr = request.GET['version']
    else:
        if versions != []:
            versionstr = versions[::-1][0]
        else:
            versionstr = ''
    if 'offonline' in request.GET and request.GET['offonline']:
        offonline = request.GET['offonline']
    else:
        offonline = 'offline'
    try:
        pie, versions = bugPie_type(versionstr,program_name,offonline,useto='pic')
        bar_base = pie.dump_options_with_quotes()
        re_bar = json.loads(bar_base)
    except:
        re_bar = ''
    return json_response(re_bar)

@permission_required('Bug.view_type')
@login_required
def query_bugs_type(request):
    request.encoding = 'utf-8'
    if 'program' in request.GET and request.GET['program']:
        program_name = request.GET['program']
    else:
        program_name = Default_Program
    program, count = OperationDB.getProgram(program_name)
    if count != 0:
        versions_dict = OperationDB.readIterationsAccordProgramID(program.id)
        versions = versions_dict['versions']
    else:
        versions = []
    if 'version' in request.GET and request.GET['version']:
        versionstr = request.GET['version']
    else:
        if versions != []:
            versionstr = versions[::-1][0]
        else:
            versionstr = ''
    if 'offonline' in request.GET and request.GET['offonline']:
        offonline = request.GET['offonline']
    else:
        offonline = 'offline'
    try:
        data, versions = bugPie_type(versionstr,program_name, type=offonline, useto='data')
        code = 0
        totalcount = len(versions)
        message = 'success'
    except Exception as e:
        code = 1001
        totalcount = 0
        data = []
        versions = []
        message = 'error:查询失败\n' + str(e)
    rdict = {
        'code': code,
        'count': totalcount,
        'data': data,
        'versions': versions,
        'msg': message
    }
    return_json = json.dumps(rdict)
    return HttpResponse(return_json)

@permission_required('Bug.add_rate')
@login_required
def score_rate_setting(request):
    contextdict = {}
    contextdict['quality_style'] =  'color: #fff;font-weight:bold'
    contextdict['view_kp'] = 'layui-nav-itemed'
    contextdict['score_setting_style'] = 'background-color: #009688;color: #fff;'
    contextdict['import_v2_title_class'] = 'layui-this'
    contextdict['import_v2_title_style'] = 'color: #009688;font-weight: 750;'
    contextdict['import_v2_title_show'] = 'layui-show'
    if request.user.has_perm("Bug.add_rate"):
        contextdict['import_v2_title_class'] = 'layui-this'
        contextdict['import_v2_title_style'] = 'color: #009688;font-weight: 750;'
        contextdict['import_v2_title_show'] = 'layui-show'
    else:
        contextdict['import_v2_title_class2'] = 'layui-this'
        contextdict['import_v2_title_style2'] = 'color: #009688;font-weight: 750;'
        contextdict['import_v2_title_show2'] = 'layui-show'
    return render(request,'quality/scoreratesetting.html',contextdict)

@permission_required('Bug.add_rate')
@login_required
def updateRage(request):
    '''更新设置 全局系数比'''
    for key in ['type', 'num']:
        if key not in request.POST:
            rjson = json.dumps({'code':1002,"msg":"have no params: %s" % key})
            return HttpResponse(rjson)
    type = request.POST['type']
    num = request.POST['num']
    # 默认返回
    rjson = json.dumps({'code': 1001, 'msg':"请求错误"})
    condition = {"type": type}
    update = {"rateNum": num}
    # 写数据库
    try:
        # 更新testdetail表
        OperationDB.updateRate(condition,update)
        rjson = json.dumps({'code': 0, 'msg':"success"})
    except Exception as e:
        rjson = json.dumps({'code': 1004, 'msg': str(e)})
        traceback.print_exc()
    return HttpResponse(rjson)

@permission_required('Bug.view_detail')
@login_required
def task_score(request):
    contextdict = {}
    contextdict['quality_style'] =  'color: #fff;font-weight:bold'
    contextdict['view_kp'] = 'layui-nav-itemed'
    contextdict['task_score_style'] = 'background-color: #009688;color: #fff;'
    return render(request,'quality/taskscore.html',contextdict)

@permission_required('Bug.view_developdetail')
@permission_required('Bug.view_testdetail')
@login_required
def leader_score(request):
    contextdict = {}
    contextdict['quality_style'] =  'color: #fff;font-weight:bold'
    contextdict['view_kp'] = 'layui-nav-itemed'
    contextdict['leader_score_style'] = 'background-color: #009688;color: #fff;'
    if request.user.has_perm("Bug.add_testdetail") and request.user.has_perm("Bug.add_developdetail") and request.user.has_perm("Bug.delete_testdetail") and request.user.has_perm("Bug.delete_developdetail"):
        contextdict['import_v2_title_class3'] = 'layui-this'
        contextdict['import_v2_title_style3'] = 'color: #009688;font-weight: 750;'
        contextdict['import_v2_title_show3'] = 'layui-show'
    elif request.user.has_perm("Bug.change_developdetail") and request.user.has_perm("Bug.delete_developdetail"):
        contextdict['import_v2_title_class4'] = 'layui-this'
        contextdict['import_v2_title_style4'] = 'color: #009688;font-weight: 750;'
        contextdict['import_v2_title_show4'] = 'layui-show'
    else:
        contextdict['import_v2_title_class5'] = 'layui-this'
        contextdict['import_v2_title_style5'] = 'color: #009688;font-weight: 750;'
        contextdict['import_v2_title_show5'] = 'layui-show'
    # 取用户 职能 & 项目 的交集
    cur_user = request.user
    cur_group_set = Group.objects.filter(user=cur_user)
    ptusers = []
    a2 = ()
    for cgroup in cur_group_set:
        cusers = cgroup.user_set.all()
        if "管理" not in cgroup.name and "主管" not in cgroup.name and "组长" not in cgroup.name:
            a1 = []
            for cu in cusers:
                a1.append(cu.first_name)
            a2 = set(a1)
            ptusers.append(a2)
    for a3 in ptusers:
        a2 = a2 & a3
    ptuserslist = list(a2)
    contextdict['programs'] = json.dumps(TC_Programs)
    contextdict['pusers'] = json.dumps(ptuserslist)
    contextdict['tusers'] = json.dumps(ptuserslist)
    # return render(request,'quality/leaderscore.html',contextdict)  #采用项目主管和技术主管 主观评价法
    return render(request,'quality/basescore.html',contextdict)  #采用工作量完成度 和 附件特殊贡献加分 评价法

@permission_required('Bug.view_developdetail')
@permission_required('Bug.view_testdetail')
@login_required
def score_statistics(request):
    if 'scoretype' in request.GET and request.GET['scoretype']:
        scoretype = request.GET['scoretype']
    else:
        scoretype = 'all'
    if 'program' in request.GET and request.GET['program']:
        program_name = request.GET['program']
    else:
        program_name = Default_Program
    program, count = OperationDB.getProgram(program_name)
    if count != 0:
        versions_dict = OperationDB.readIterationsAccordProgramID(program.id)
        versions = versions_dict['versions']
    else:
        versions = []
        module_fields = []
    if versions != []:
        if 'version' in request.GET and request.GET['version']:
            version_str = request.GET['version']
        else:
            version_str = versions[::-1][0]
        bar, module_fields = bugBar_scores(version_str, program_name, scoretype, useto='pic')
    contextdict = {}
    contextdict['quality_style'] =  'color: #fff;font-weight:bold'
    contextdict['view_kp'] = 'layui-nav-itemed'
    contextdict['score_statistics_style'] = 'background-color: #009688;color: #fff;'
    if versions != []:
        contextdict['myechart'] = bar.render_embed()
    contextdict['modules_fileds'] = json.dumps(module_fields)
    contextdict['versions'] = json.dumps(versions[::-1])
    contextdict['programs'] = json.dumps(list(TC_Programs.keys()))
    return render(request, 'quality/scorestatistics.html', contextdict)

@permission_required('Bug.view_developdetail')
@permission_required('Bug.view_testdetail')
@login_required
def score_statistics_update(request):
    '''更新评分统计页'''

    if 'program' in request.GET and request.GET['program']:
        program_name = request.GET['program']
    else:
        program_name = Default_Program
    program, count = OperationDB.getProgram(program_name)
    if count != 0:
        versions_dict = OperationDB.readIterationsAccordProgramID(program.id)
        versions = versions_dict['versions']
    else:
        versions = []
    if 'version' in request.GET and request.GET['version']:
        versionstr = request.GET['version']
    else:
        if versions != []:
            versionstr = versions[::-1][0]
        else:
            versionstr = ''
    if 'scoretype' in request.GET and request.GET['scoretype']:
        scoretype = request.GET['scoretype']
    else:
        scoretype = 'all'
    try:
        bar, versions = bugBar_scores(versionstr,program_name,scoretype,useto='pic')
        bar_base = bar.dump_options_with_quotes()
        re_bar = json.loads(bar_base)
    except:
        re_bar = ''
    return json_response(re_bar)

@permission_required('Bug.view_developdetail')
@permission_required('Bug.view_testdetail')
@login_required
def performance_statistics_update(request):
    '''更新评分统计页'''

    if 'program' in request.GET and request.GET['program']:
        program_name = request.GET['program']
    else:
        program_name = Default_Program
    program, count = OperationDB.getProgram(program_name)
    if count != 0:
        versions_dict = OperationDB.readIterationsAccordProgramID(program.id)
        versions = versions_dict['versions']
    else:
        versions = []
    if 'version' in request.GET and request.GET['version']:
        versionstr = request.GET['version']
    else:
        if versions != []:
            versionstr = versions[::-1][0]
        else:
            versionstr = ''
    if 'scoretype' in request.GET and request.GET['scoretype']:
        scoretype = request.GET['scoretype']
    else:
        scoretype = 'all'
    try:
        radar, versions = bugRadar_scores(versionstr,program_name,scoretype,useto='pic')
        radar_base = radar.dump_options_with_quotes()
        re_radar = json.loads(radar_base)
    except:
        re_radar = ''
    return json_response(re_radar)

@permission_required('Bug.view_developdetail')
@permission_required('Bug.view_testdetail')
@login_required
def query_score_statistics(request):
    request.encoding = 'utf-8'
    if 'program' in request.GET and request.GET['program']:
        program_name = request.GET['program']
    else:
        program_name = Default_Program
    program, count = OperationDB.getProgram(program_name)
    if count != 0:
        versions_dict = OperationDB.readIterationsAccordProgramID(program.id)
        versions = versions_dict['versions']
    else:
        versions = []
    if 'version' in request.GET and request.GET['version']:
        versionstr = request.GET['version']
    else:
        if versions != []:
            versionstr = versions[::-1][0]
        else:
            versionstr = ''
    if 'scoretype' in request.GET and request.GET['scoretype']:
        scoretype = request.GET['scoretype']
    else:
        scoretype = 'all'
    try:
        data, versions = bugBar_scores(versionstr, program_name, type=scoretype, useto='data')
        code = 0
        totalcount = len(versions)
        message = 'success'
    except Exception as e:
        code = 1001
        totalcount = 0
        data = []
        versions = []
        message = 'error:查询失败\n' + str(e)
    rdict = {
        'code': code,
        'count': totalcount,
        'data': data,
        'versions': versions,
        'msg': message
    }
    return_json = json.dumps(rdict)
    return HttpResponse(return_json)

@permission_required('Bug.view_detail')
@login_required
def efficiency(request):
    contextdict = {}
    contextdict['quality_style'] =  'color: #fff;font-weight:bold'
    contextdict['view_xl'] = 'layui-nav-itemed'
    return render(request,'quality/taskscore.html',contextdict)


@permission_required('Bug.view_detail')
@login_required
def autotask(request):
    contextdict = {}
    contextdict['quality_style'] =  'color: #fff;font-weight:bold'
    contextdict['view_auto'] = 'layui-nav-itemed'
    return render(request,'quality/taskscore.html',contextdict)