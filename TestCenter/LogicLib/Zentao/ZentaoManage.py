# coding:utf-8
# author: Chenliang
# CreateTime: 20190926 15:30
# desc: 调度执行robotframework 脚本，实现重跑上一次失败用例,并回填测试结果到禅道

import re
import json
import subprocess
import requests
from TestCenter.LogicLib.PublicMethods import Get_Date,random_strs,Byte2Str
from TestCenter.LogicLib.SourceData.StatisticsAndAnalysisBug import StatisticsBugFromList
from TestCenter.LogicLib.Config import zentao_account

def AssertEqual(result):
    '''
    检查禅道API接口返回的状态
    :param result: api result
    :return:
    '''
    nr = result.json()
    status = nr['status']
    if status != 'success':
        raise Exception("Compare Error: this api response is not successful !!!")

def excute_cmd(cmd_str,title_str='Report:'):
    con = subprocess.Popen(cmd_str,stdout=subprocess.PIPE)
    r_str = con.stdout
    # result_str = subprocess.check_output(cmd_str,shell=True)

    while True:
        result_str = str(r_str.readline())
        if title_str in result_str:
            print("----> Cmd : %s Excute finished ..." % cmd_str)
            print(result_str)
            return True
    print("----> Cmd : %s Excute Failed ..." % cmd_str)
    return False

class Manage_Zendao():
    '''对接禅道API接口，实现一系列功能'''
    def __init__(self,domain='zentao.ihaoshenghuo.com',user='Auto',pwd='auto123456'):
        '''
        初始化接口请求session对象，并登陆用户
        :param domain: 域名，可以是zentao.ihaoshenghuo.com，也可以是 192.168.2.188:8000
        :param port:
        :param user:
        :param pwd:
        '''
        print("---> Init and Login Zendao ...")
        self.head_url = 'https://{}/zentao/'.format(domain)
        self.ses = requests.session()
        self.loginIn(user,pwd)

    def loginIn(self,user,pwd):
        '''
        用户登录
        :param user: 用户账号
        :param pwd: 密码
        :return: None
        '''
        getSessionId_url = self.head_url + "api-getsessionid.json"
        result = self.ses.get(getSessionId_url)
        AssertEqual(result)
        # print result.content
        result = result.json()
        # print result
        rr = result['data'].encode('utf8')
        r = Byte2Str(rr)
        m = '.+"sessionID":"(.+)","rand".+'
        p = re.compile(m)
        g = p.match(r)
        session_id = g.group(1)
        # print session_id
        login_url = self.head_url + 'user-login.json?zentaosid=%s' % session_id
        body = {'account': user, 'password': pwd}
        result = self.ses.post(login_url, body)
        AssertEqual(result)

    def loginOut(self):
        '''
        用户登出
        :return: None
        '''
        loginOut_url = self.head_url + 'user-logout.json'
        result = self.ses.get(loginOut_url)
        AssertEqual(result)
        print("---> logout Zendao and close session ...")

    def getUserName(self,userkey):
        '''获取用户名称'''
        userlist = self.getCompanyUser()
        users = self.handleUsers(userlist)
        username = users[userkey] if userkey in users.keys() else userkey
        return username

    def getProducts(self,product_name=''):
        '''
        获取所有产品
        :param product_name: 产品名称，默认为空则返回所有产品，否则返回对应id
        :return: None
        '''
        request_url = self.head_url + 'product-index.json'
        result = self.ses.get(request_url)
        AssertEqual(result)
        rejson = result.json()
        data = json.loads(rejson['data'])
        products = data['products']
        if product_name != '' or product_name != None:
            for id,name in products.items():
                if name == product_name:
                    return id
            return None
        return products

    def getProductCases(self,product_id=''):
        '''
        获取对应产品的所有用例
        :param product_name: 产品名称，默认为空则返回所有产品，否则返回对应id
        :return: None
        '''
        request_url = self.head_url + 'testcase-browse-{0}-0-all-0-id_desc-999999-999999-1.json'.format(str(product_id))
        result = self.ses.get(request_url)
        AssertEqual(result)
        rejson = result.json()
        data = json.loads(rejson['data'])
        cases = data['cases']
        # print(len(cases))
        return cases

    def getProductTargetCreatedCases(self,product_name,stime,etime):
        '''
        获取对应产品指定时间范围新增和评审的用例
        :param product_name: 产品名称
        :param stime: 开始时间
        :param etime: 结束时间
        :return: 用例列表
        '''

        userlist = self.getCompanyUser()
        users = self.handleUsers(userlist)
        productID = self.getProducts(product_name=product_name)
        casesdict = self.getProductCases(product_id=productID)
        runerPerinfo = {}
        for id,case in casesdict.items():
            openedDate = case['openedDate']
            py = case['openedBy']
            openedUser = users[py] if py in users.keys() else py
            if stime <= openedDate <= etime:
                if openedUser not in runerPerinfo.keys():
                    runerPerinfo[openedUser] = {
                        "createdCasesCount": 0,
                        "reviewCasesCount": 0,
                        "passReviewCount": 0,
                        "failedReviewCount": 0,
                        "notReviewCount": 0,
                        'runner': openedUser
                    }
                runerPerinfo[openedUser]['createdCasesCount'] += 1
            if "reviewedDate" in case.keys():
                reviewedDate = case['reviewedDate']
                if stime <= reviewedDate <= etime:
                    py = case['reviewedBy']
                    if py != '' and py != None :
                        reviewedUser = users[py] if py in users.keys() else py
                        if reviewedUser not in runerPerinfo.keys():
                            runerPerinfo[reviewedUser] = {
                                "createdCasesCount": 0,
                                "reviewCasesCount": 0,
                                "passReviewCount": 0,
                                "failedReviewCount": 0,
                                "notReviewCount": 0,
                                'runner': reviewedUser
                            }
                        runerPerinfo[reviewedUser]["reviewCasesCount"] += 1

                        if openedUser not in runerPerinfo.keys():
                            runerPerinfo[openedUser] = {
                                "createdCasesCount": 0,
                                "reviewCasesCount": 0,
                                "passReviewCount": 0,
                                "failedReviewCount": 0,
                                "notReviewCount": 0,
                                'runner': openedUser
                            }
                        status = case['status']
                        if status == 'normal':
                            runerPerinfo[openedUser]['passReviewCount'] += 1
                        elif status == 'fail':
                            runerPerinfo[openedUser]['failedReviewCount'] += 1
                        else:
                            runerPerinfo[openedUser]['notReviewCount'] += 1

        return runerPerinfo

    def getProductTargetRunCases(self,product_name,stime,etime):
        '''
        获取对应产品指定时间范围执行的用例
        :param product_name: 产品名称
        :param stime: 开始时间
        :param etime: 结束时间
        :return: 用例列表
        '''

        userlist = self.getCompanyUser()
        users = self.handleUsers(userlist)
        productID = self.getProducts(product_name=product_name)
        casesdict = self.getProductCases(product_id=productID)
        runerPerinfo = {}
        runerPerCountList = []
        for id,case in casesdict.items():
            lastRunDate = case['lastRunDate']
            if stime <= lastRunDate <= etime:
                py = case['lastRunner']
                lastRunner = users[py]
                if lastRunner not in runerPerinfo.keys():
                    runerPerinfo[lastRunner] = []
                    runerPerinfo[lastRunner].append(case)
                else:
                    runerPerinfo[lastRunner].append(case)
        for runner,cases in runerPerinfo.items():
            notRunCount = 0
            passRunCount = 0
            failedRunCount = 0
            blockeddRunCount = 0
            for case in cases:
                lastRunResult = case['lastRunResult']
                # print(case)
                if lastRunResult == 'pass':
                    passRunCount += 1
                elif lastRunResult == 'fail':
                    failedRunCount += 1
                elif lastRunResult == 'block':
                    blockeddRunCount += 1
                else:
                    notRunCount += 1
            caseRunInfo = {
                "passRunCount":passRunCount,
                "failedRunCount":failedRunCount,
                "blockedRunCount":blockeddRunCount,
                "notRunCount":notRunCount,
                'runner':runner
            }
            runerPerCountList.append(caseRunInfo)
        return runerPerCountList

    def getTargetTaskId(self,taskname,productId=1):
        '''
        获取指定名称测试单编号（ID）
        :param taskname: 测试单名称
        :param productId: 产品ID 默认1
        :return: taskID：测试单编号
        '''
        taskId = None
        listtask_url = self.head_url + "testtask-browse-{}-0-local,doing.json".format(productId)
        result = self.ses.get(listtask_url)
        AssertEqual(result)
        # print result.content
        rejson = result.json()
        data = json.loads(rejson['data'])
        tasks = data['tasks']  # 任务列表
        for key, value in tasks.items():
            if taskname == value['name']:
                taskId = value['id']
                print (value['id'])
                break
        return taskId

    def createTask(self,taskname,productId=1):
        '''
        创建测试任务单
        :param taskname: 测试单名称
        :param productId: 产品ID
        :return: taskId：测试单ID
        '''
        # 获取创建测试单时需要的版本等参数
        taskCreate_url = self.head_url + 'testtask-create-{}.json'.format(productId)
        result = self.ses.get(taskCreate_url)
        AssertEqual(result)
        rejson = result.json()
        data = json.loads(rejson['data'])
        projects = data['projects']  #项目列表
        builds = data['builds']  #版本列表
        builds.pop("")
        buildId = 0
        build_version = "V 0.0"
        for key,value in builds.items():
            cur_n = int(key)
            if cur_n > buildId:
                buildId = cur_n
                build_version = value
        print(buildId,build_version)
        cur_date = Get_Date()
        taskname_N = "【{}】".format(build_version) + taskname+"{}".format(cur_date)
        print(taskname_N.decode('utf-8'))
        # 查询当日回归测试单是否存在
        task_id = self.getTargetTaskId(taskname_N,productId)
        if task_id is None:
            # 创建测试单
            body = {
                "product": 1, # 1是产品-> 易维帮助台 6.0
                "project": 77, # 77是项目-> 产品迭代主线
                "build": buildId,  # 版本ID
                "owner": "Auto", # 负责人
                "pri": 2, # 优先级
                "begin": cur_date,
                "end": cur_date,
                "status": "doing", # 状态
                "name": taskname_N,
                "desc": taskname,
                "mailto[]": {"uid": random_strs(13)}
            }
            result = self.ses.post(taskCreate_url,body)
            # print result.content
            # 查询新建的回归测试单是否存在
            task_id = self.getTargetTaskId(taskname_N, productId)
        else:
            print("This taskname is exist ! Don't need to create it ...")
        return task_id

    def getProductTasks(self,product_id='9'):
        '''
        获取对应产品的所有测试单
        :param product_name: 产品名称，默认为空则返回所有产品，否则返回对应id
        :return: None
        '''
        request_url = self.head_url + 'testtask-browse-{0}--local,totalStatus-id_desc-99999-99999-1-0-0.json'.format(str(product_id))
        result = self.ses.get(request_url)
        AssertEqual(result)
        rejson = result.json()
        data = json.loads(rejson['data'])
        tasks = data['tasks']
        print(len(tasks))
        return tasks

    def getProductTargetTasksRunCases(self,product_name,stime,etime):
        '''
        获取对应产品 所有测试单 指定时间范围执行的用例
        :param product_name: 产品名称
        :param stime: 开始时间
        :param etime: 结束时间
        :return: 用例列表
        '''

        userlist = self.getCompanyUser()
        users = self.handleUsers(userlist)
        productID = self.getProducts(product_name=product_name)
        tasksdict = self.getProductTasks(product_id=productID)
        casesdict = {}
        runerPerinfo = {}
        runerPerCountList = []

        for id,task in tasksdict.items():
            begin = task['begin']
            end = task['end']
            if (stime <= begin <= etime) or (stime <= end <= etime):
                taskcases = self.getTaskCases(id)
                casesdict.update(taskcases)

        for id,case in casesdict.items():
            lastRunDate = case['lastRunDate']
            lastRunResult = case['lastRunResult']
            if (stime <= lastRunDate <= etime) or (lastRunResult == ''):
                lastRunner = case['lastRunner']
                if lastRunner != '':
                    lastRunnerName = users[lastRunner]
                    curUser = lastRunnerName
                else:
                    assignedTo = case['assignedTo']
                    if assignedTo != '':
                        assignedUser = users[assignedTo]
                        curUser = assignedUser
                    else:
                        curUser = '其他'
                if curUser not in runerPerinfo.keys():
                    runerPerinfo[curUser] = []
                    runerPerinfo[curUser].append(case)
                else:
                    runerPerinfo[curUser].append(case)

        caseRunInfo = {}
        for runner, cases in runerPerinfo.items():
            notRunCount = 0
            passRunCount = 0
            failedRunCount = 0
            blockeddRunCount = 0
            for case in cases:
                lastRunResult = case['lastRunResult']
                # print(case)
                if lastRunResult == 'pass':
                    passRunCount += 1
                elif lastRunResult == 'fail':
                    failedRunCount += 1
                elif lastRunResult == 'block':
                    blockeddRunCount += 1
                else:
                    notRunCount += 1
            caseRunInfo[runner] = {
                "passRunCount": passRunCount,
                "failedRunCount": failedRunCount,
                "blockedRunCount": blockeddRunCount,
                "notRunCount": notRunCount,
                'runner': runner
            }
            # runerPerCountList.append(caseRunInfo)
        return caseRunInfo

    def getSuiteCases(self, taskNo,suiteId=17):
        '''
        按套件关联用例
        :param taskNo: 测试单ID
        :param suiteId: 套件ID  (默认16 回归用例ALL)
        :return: 用例编号，用例版本
        '''
        linkcase_url = self.head_url + "testtask-linkCase-{}-bysuite-{}-1-1.json".format(taskNo, suiteId)
        result = self.ses.get(linkcase_url)
        AssertEqual(result)
        rejson = result.json()
        data = json.loads(rejson['data'])
        cases = data['cases']  # 任务列表
        cases_list = []
        for case in cases:
            cases_list.append({'id':case['id'],'version':case['version']})
        return cases_list

    def linkCases(self,taskNo,suiteId=17):
        '''
        按套件关联用例
        :param taskNo: 测试单ID
        :param suiteId: 套件ID  (默认16 回归用例ALL)
        :return: None
        '''
        linkcase_url = self.head_url + "testtask-linkCase-{}-bysuite-{}.json".format(taskNo,suiteId)
        cases = self.getSuiteCases(taskNo,suiteId)
        cases_body = {"cases":[]}
        for case in cases:
            id = case['id']
            version = case['version']
            cases_body['cases[{}]'.format(id)] = id
            cases_body['versions[{}]'.format(id)] = version
        # print linkcase_url
        # print cases_body
        result = self.ses.post(linkcase_url,cases_body)
        AssertEqual(result)
        # print result.content

    def searchCasesByKeyword(self,taskNo,keyword):
        '''
        按关键字搜索任务单中用例
        :param taskNo: 测试单no
        :param keyword: 关键字
        :return: cases dict
        '''
        # 调试未完成，搜索不完整，参数可能有误
        buildQuery_url = self.head_url + 'search-buildQuery.json'
        body = {
            'fieldmodule': 'ZERO',
            'fieldid':{
                'andOr1': 'AND',
                'field1': 'keywords',
                'operator1': 'include',
                'value1': keyword
            },
            'module': 'testtask',
            'actionURL': '/zentao/testtask-cases-{}-bySearch-myQueryID.json'.format(taskNo)
        }
        result = self.ses.post(buildQuery_url, body)

        search_url = self.head_url + 'testtask-cases-{}-bySearch-myQueryID.json'.format(taskNo)
        result = self.ses.get(search_url)
        AssertEqual(result)
        print(result.content)
        rejson = result.json()
        data = json.loads(rejson['data'])
        runs = data['runs']
        cases_version = {}
        for key, value in runs.items():
            cases_version[value['case']] = {'version': value['version'], 'runid': key, 'keywords': value['keywords']}
        # print cases_version
        return cases_version

    def asignCasesByKeyword(self,taskNo,casesInfoDict,someone,tkeyword):
        '''
        按关键字指派执行人
        :param taskNo: 测试单no
        :param casesInfoDict: 用例集字典
        :param someone: 被指派人 （当前有：xiaobei,daoqing,chenliang）
        :param tkeyword: 用例关键词
        :return: None
        '''
        asign_url = self.head_url + 'testtask-batchAssign-{}.json'.format(taskNo)
        body = {
            'assignedTo':someone
        }
        for caseno,info in casesInfoDict.items():
            keyword = info['keywords']
            if tkeyword in keyword:
                body.setdefault('caseIDList[{}]'.format(caseno),caseno)
        result = self.ses.post(asign_url,body)
        # AssertEqual(result)
        # print result.content

    def getTaskCases(self,taskNo):
        '''
        获取测试单中关联的用例
        :param taskNo: 测试单编号（ID）
        :return: cases_version 用例编号，执行id，version
        '''
        taskcase_url = self.head_url + 'testtask-cases-{}-all-1-version-1.json'.format(taskNo)
        result = self.ses.get(taskcase_url)
        AssertEqual(result)
        # print result.content
        data = result.json()['data']
        data = json.loads(data)
        runs = data['runs']
        # print runs
        # print runs.keys()
        # if runs != {}:
        #     print(len(runs.keys()))
        # cases_version = {}
        # for key,value in runs.items():
        #     cases_version[value['case']] = {'version':value['version'],'runid':key, 'keywords': value['keywords']}
        # print cases_version
        # return cases_version
        return runs

    def getCaseStepsIDs(self,caseNo,version):
        '''
        获取用例中最后一步的stepID
        :param caseNo: 用例编号
        :param version: 用例版本
        :return: stepID：最后一步ID
        '''
        testcase_url = self.head_url + 'testcase-view-{}-{}.json'.format(caseNo,version)
        result = self.ses.get(testcase_url)
        AssertEqual(result)
        # print result.content
        result = result.json()
        # result = json.loads(result.content.decode())
        data1 = result['data'].encode('utf8')
        data = json.loads(data1)
        # print data
        # print data['case']['steps']
        m = '.+"steps":(.+),"files".+'
        p = re.compile(m)
        g = p.match(data1)
        steps = g.group(1)
        # print steps
        # print type(steps)
        steps_dict = json.loads(steps)
        keys = steps_dict.keys()
        # print keys
        return keys[0]

    def runCase(self,staus='pass',runid=12405,caseNo=8444,stepid=22510,version=1,failMsg="自动化脚本执行失败"):
        '''
        执行测试单中的用例，回填结果
        :param staus: pass/fail
        :param runid: 用例执行ID
        :param caseNo: 用例编号（ID）
        :param stepid: 用例最后一步ID
        :param version: 用例版本
        :param failMsg: 失败描述
        :return: None
        '''
        runcase_url = self.head_url + 'testtask-runCase-{}-{}-{}.json'.format(runid,caseNo,version)
        # print runcase_url
        if staus.lower() == 'pass':
            failMsg = ''
            staus = "pass"
        else:
            staus = "fail"
        body = {
            'steps[{}]'.format(stepid): staus,
            'reals[{}]'.format(stepid): failMsg,
            'case': caseNo,
            'version': version,
            'files{}[]'.format(stepid): "",
            'labels{}[]'.format(stepid): ""
        }
        # print body
        result = self.ses.post(runcase_url,body)
        # print result.content

    def getBugs(self,productID,total=99999,pernum=99999,page=1):
        '''
        根据产品id获取bug
        :param productID:  产品id
        :return: list
        '''
        rquest_url = self.head_url + 'bug-browse-{0}-0-bysearch-myqureyID-id-{1}-{2}-{3}.json'.format(productID,pernum,total,page)
        # print rquest_url
        result = self.ses.get(rquest_url)
        new_result = result.json()
        data1 = new_result['data'].encode('utf8')
        data = json.loads(data1)
        title = data['title']
        bugs = data['bugs']
        print(title)
        # print(bugs)
        print(len(bugs))
        return bugs

    def searchBugs(self,productID):
        '''
        搜索查询bug
        :param productID:  产品id
        :return: list
        '''
        rquest_url = self.head_url + 'search-buildQuery.json'
        # print rquest_url
        body = {
            "fieldproduct":3,
            "fieldconfirmed": "ZERO",
            "fieldmodule": "ZERO",
            "andOr1": "AND",
            "field1": "title",
            "operator1": "include",
            "value1": "管理",
            "andOr4": "AND",
            "field4": "openedDate",
            "operator4": ">=",
            "value4": "2021-07-26",
            "module": "bug",
            "actionURL": "/zentao/bug-browse-3-0-bySearch-myQueryID.json",
            "groupItems": 3,
            "formType": "lite"
        }
        result = self.ses.post(rquest_url,body)
        new_result = result.json()
        data1 = new_result['data'].encode('utf8')
        data = json.loads(data1)
        bugs = data['bugs']
        print(bugs)
        print(len(bugs))
        return bugs

    def getBugField(self,productID):
        '''
        搜索查询bug的自定义字段
        :param productID:  产品id
        :return: dict
        '''
        rquest_url = self.head_url + 'bug-ajaxGetBugFieldOptions-{}.json'.format(productID)
        result = self.ses.get(rquest_url)
        new_result = result.json()
        return new_result

    def getCompanyUser(self):
        '''
        获取所有用户
        :return: list
        '''
        rquest_url = self.head_url + 'company-browse-bysearch-myqureyID-id-9999-9999-1.json'
        result = self.ses.get(rquest_url)
        new_result = result.json()
        data1 = new_result['data'].encode('utf8')
        data = json.loads(data1)
        users = data['users']
        return users

    def handleUsers(self,usersinfo):
        '''只取账户种有效信息'''
        users = {}
        for userinfo in usersinfo:
            users[userinfo['account']] = userinfo['realname']
        return users

    def close(self):
        '''
        用户登出，关闭接口对象
        :return: None
        '''
        self.loginOut()
        self.ses.close()

def CreateTaskAndExecute_Zendao(casesResult=[{'id':'7895','status':'pass'}]):
    '''
    创建回归测试任务，并回填用例执行结果
    :return:
    '''
    MZ = Manage_Zendao()
    # 创建测试单
    task_no = MZ.createTask(taskname="回归测试")
    # 按套件关联测试用例
    MZ.linkCases(task_no)
    # 获取关联的测试用例
    cv = MZ.getTaskCases(taskNo=task_no)
    # 暂时指派写死
    MZ.asignCasesByKeyword(task_no, cv, 'xiaobei', tkeyword='xxb')
    MZ.asignCasesByKeyword(task_no, cv, 'chenliang', tkeyword='cl')
    MZ.asignCasesByKeyword(task_no, cv, 'daoqing', tkeyword='zdq')
    # 执行
    TaskCaseNoList = cv.keys()
    for case in casesResult:
        case_no = case['id']
        if case_no in TaskCaseNoList:
            ver_id = cv[case_no]['version']
            run_id = cv[case_no]['runid']
            stepid = MZ.getCaseStepsIDs(caseNo=case_no,version=ver_id)
            MZ.runCase(staus=case['status'],runid=run_id,caseNo=case_no,stepid=stepid,version=ver_id)
        else:
            print("There is no this caseNo in the task! Case No: %s" % case_no)
            pass
    MZ.close()

def returnBugsInfo(programName='',s_time='',e_time=''):
    '''获取对应产品的bug情况
    :return bugs_info:
    '''
    MZ = Manage_Zendao(user=zentao_account['user'], pwd=zentao_account['password'])
    id = MZ.getProducts(product_name=programName)
    userlist = MZ.getCompanyUser()
    users = MZ.handleUsers(userlist)
    bugfields = MZ.getBugField(productID=id)
    bugs = MZ.getBugs(productID=id)
    MZ.close()
    on_total, on_resolved, off_total, off_resolved = StatisticsBugFromList.Statistics_total_zentoAPI(bugs)
    new_bugs = StatisticsBugFromList.StatisticsAll_zentao_api(bugs,bugfields,users,s_time,e_time)
    # print(len(new_bugs))
    # print(new_bugs)
    return new_bugs,on_total,on_resolved,off_total,off_resolved

def returnRunCases(son_programe_name,stime,etime):
    '''
    获取指定产品对应的最近一次用例执行情况，筛选时间范围内的
    :param son_programe_name: 产品名称
    :param stime: 开始执行时间
    :param etime: 结束执行时间
    :return: list
    '''
    MZ = Manage_Zendao(user='chenliang', pwd='cl123456')
    # cases = MZ.getProductTargetRunCases(son_programe_name, stime, etime)
    cases1 = MZ.getProductTargetTasksRunCases(son_programe_name, stime, etime)
    cases2 = MZ.getProductTargetCreatedCases(son_programe_name, stime, etime)
    MZ.close()
    users = set(list(cases1.keys()) + list(cases2.keys()))
    cases = []
    for user in users:
        case = {
            "passRunCount": 0,
            "failedRunCount": 0,
            "blockedRunCount": 0,
            "notRunCount": 0,
            "passReviewCount":0,
            "failedReviewCount":0,
            "notReviewCount":0,
            "createdCasesCount":0,
            "reviewCasesCount":0,
            'runner': ''
        }
        if user in cases1.keys():
            case.update(cases1[user])
        if user in cases2.keys():
            case.update(cases2[user])
        cases.append(case)
    return cases

def SampleTest():
    MZ = Manage_Zendao(user='chenliang',pwd='cl123456')
    # sts = MZ.getProductCases('9')
    sts = MZ.getProductTargetCreatedCases('HSH-东语移动用户端',stime='2021-08-21',etime='2021-08-27')
    print(sts)
    MZ.close()

if __name__ == '__main__':
    SampleTest()
    # returnBugsInfo('HSH-新零售',s_time='2021-07-26',e_time='2021-07-30')
