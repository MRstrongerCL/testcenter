from django.db import models

# Create your models here.
class detail(models.Model):
    title = models.CharField(u'bug标题',  blank=True,  max_length=512,  null=True,  default='',  help_text='显示在下方')
    third_id = models.CharField(u'第三方id',  blank=True,  max_length=50,  null=True,  default='')
    iteration = models.CharField(u'迭代版本',  blank=True,  max_length=50,  null=True,  default='')
    Severity = models.CharField(choices=(('1',u'致命'),('2',u'严重'),('3',u'一般'),('4',u'轻微'),('5',u'建议')), max_length=20, default='')
    priority = models.CharField(choices=(('1',u'非常紧急'),('2',u'紧急'),('3',u'一般'),('4',u'不紧急'),('5',u'可缓')), max_length=20, default='')
    bug_type = models.CharField(u'缺陷类型',  blank=True,  max_length=50,  null=True,  default='')
    bug_moudle = models.CharField(u'缺陷模块',  blank=True,  max_length=50,  null=True,  default='')
    bug_owner = models.CharField(u'缺陷归属人',  blank=True,  max_length=50,  null=True,  default='')
    bug_creater = models.CharField(u'缺陷创建人',  blank=True,  max_length=50,  null=True,  default='')
    bug_closer = models.CharField(u'缺陷关闭人',  blank=True,  max_length=50,  null=True,  default='')
    create_time = models.CharField(u'创建时间',  blank=True,  max_length=50,  null=True,  default='')
    update_time = models.CharField(u'更新时间',  blank=True,  max_length=50,  null=True,  default='')
    finish_time = models.CharField(u'完成时间',  blank=True,  max_length=50,  null=True,  default='')
    status = models.CharField(u'缺陷状态',  blank=True,  max_length=50,  null=True,  default='')
    program = models.CharField(u'项目',  blank=True,  max_length=50,  null=True,  default='')
    type_owner = models.CharField(u'归属类型',  blank=True,  max_length=50,  null=True,  default='offline')

class perDeveloper(models.Model):
    product_time = models.CharField(u'本条数据创建时间',  blank=True,  max_length=20,  null=True,  default='')
    developer_name = models.CharField(u'开发者名称',  blank=True,  max_length=20,  null=True,  default='')
    scores = models.CharField(u'分数',  blank=True,  max_length=20,  null=True,  default='')

class perTester(models.Model):
    product_time = models.CharField(u'本条数据创建时间', blank=True, max_length=20, null=True, default='')
    tester_name = models.CharField(u'测试者名称', blank=True, max_length=20, null=True, default='')
    scores = models.CharField(u'分数', blank=True, max_length=20, null=True, default='')

class moudle(models.Model):
    name = models.CharField(max_length=20)

class type(models.Model):
    name = models.CharField(max_length=20)

class iteration(models.Model):
    version = models.CharField(u'迭代版本', blank=True,  max_length=50,  null=True,  default='',)
    program_id = models.CharField(u'项目ID', blank=True,  max_length=50,  null=True,  default='',)
    start_time = models.CharField(u'迭代开始时间',  blank=True,  max_length=50,  null=True,  default='')
    end_time = models.CharField(u'迭代结束时间',  blank=True,  max_length=50,  null=True,  default='')
    create_time = models.CharField(u'创建时间',  blank=True,  max_length=50,  null=True,  default='')

class program(models.Model):
    name = models.CharField(u'项目名称', blank=True,  max_length=50,  null=True,  default='',)

class son_program(models.Model):
    name = models.CharField(u'子项目名称', blank=True,  max_length=50,  null=True,  default='',)
    parent_program_id = models.CharField(u'父项目ID', blank=True,  max_length=50,  null=True,  default='',)
    online_total_no = models.CharField(u'线上总计',  blank=True,  max_length=50,  null=True,  default='')
    offline_total_no = models.CharField(u'线下统计',  blank=True,  max_length=50,  null=True,  default='')
    online_resloved_no = models.CharField(u'线上解决数',  blank=True,  max_length=50,  null=True,  default='')
    offline_resloved_no = models.CharField(u'线下解决数',  blank=True,  max_length=50,  null=True,  default='')
    update_time = models.CharField(u'创建时间',  blank=True,  max_length=50,  null=True,  default='')

class testdetail(models.Model):
    tester = models.CharField(u'测试人员名称', blank=True,  max_length=50,  null=True,  default='',)
    iteration_id = models.CharField(u'迭代ID', blank=True,  max_length=50,  null=True,  default='',)
    son_program_id = models.CharField(u'子项目ID', blank=True,  max_length=50,  null=True,  default='',)
    s_time = models.CharField(u'开始时间',  blank=True,  max_length=50,  null=True,  default='')
    e_time = models.CharField(u'结束时间',  blank=True,  max_length=50,  null=True,  default='')
    passRunCount = models.CharField(u'通过用例数',  blank=True,  max_length=50,  null=True,  default='')
    failedRunCount = models.CharField(u'失败用例数',  blank=True,  max_length=50,  null=True,  default='')
    blockedRunCount = models.CharField(u'阻塞用例数',  blank=True,  max_length=50,  null=True,  default='')
    notRunCount = models.CharField(u'未执行用例数',  blank=True,  max_length=50,  null=True,  default='')
    offline_BugCount = models.CharField(u'迭代bug数',  blank=True,  max_length=50,  null=True,  default='')
    online_BugCount = models.CharField(u'线上bug数',  blank=True,  max_length=50,  null=True,  default='')
    lost_BugCount = models.CharField(u'漏测bug数',  blank=True,  max_length=50,  null=True,  default='')
    passReviewCount = models.CharField(u'评审通过用例数', blank=True, max_length=50, null=True, default='')
    failedReviewCount = models.CharField(u'评审不通过用例数', blank=True, max_length=50, null=True, default='')
    notReviewCount = models.CharField(u'未评审用例数', blank=True, max_length=50, null=True, default='')
    createdCasesCount = models.CharField(u'新增用例数', blank=True, max_length=50, null=True, default='')
    reviewCasesCount = models.CharField(u'新增用例数', blank=True, max_length=50, null=True, default='')
    ProgramScores = models.CharField(u'项目主管评分', blank=True, max_length=50, null=True, default='')
    TechScores = models.CharField(u'技术主管评分', blank=True, max_length=50, null=True, default='')
    reviewCasesCount = models.CharField(u'新增用例数', blank=True, max_length=50, null=True, default='')
    testDelayTime = models.CharField(u'测试完成延期时间', blank=True, max_length=50, null=True, default='')
    autoFinishRate = models.CharField(u'自动化完成率', blank=True, max_length=50, null=True, default='')
    programScoreDescription = models.CharField(u'项目主管评分说明', blank=True, max_length=1000, null=True, default='')
    techScoreDescription = models.CharField(u'技术主管评分说明', blank=True, max_length=1000, null=True, default='')
    update_time = models.CharField(u'更新时间', blank=True, max_length=50, null=True, default='')

class developdetail(models.Model):
    developer = models.CharField(u'开发人员名称', blank=True,  max_length=50,  null=True,  default='',)
    iteration_id = models.CharField(u'迭代ID', blank=True,  max_length=50,  null=True,  default='',)
    son_program_id = models.CharField(u'子项目ID', blank=True,  max_length=50,  null=True,  default='',)
    s_time = models.CharField(u'开始时间',  blank=True,  max_length=50,  null=True,  default='')
    e_time = models.CharField(u'结束时间',  blank=True,  max_length=50,  null=True,  default='')
    reopenBugCount = models.CharField(u'缺陷reopen个数',  blank=True,  max_length=50,  null=True,  default='')
    failedSmokeCount = models.CharField(u'冒烟测试失败测试',  blank=True,  max_length=50,  null=True,  default='')
    delayTestTimes = models.CharField(u'提测延期时间',  blank=True,  max_length=50,  null=True,  default='')
    ProgramScores = models.CharField(u'项目主管评分', blank=True, max_length=50, null=True, default='')
    TechScores = models.CharField(u'技术主管评分', blank=True, max_length=50, null=True, default='')
    programScoreDescription = models.CharField(u'项目主管评分说明', blank=True, max_length=1000, null=True, default='')
    techScoreDescription = models.CharField(u'技术主管评分说明', blank=True, max_length=1000, null=True, default='')
    update_time = models.CharField(u'更新时间', blank=True, max_length=50, null=True, default='')

class rate(models.Model):
    type = models.CharField(u'系数类型',  blank=True,  max_length=50,  null=True,  default='')
    rateNum = models.CharField(u'系数数值',  blank=True,  max_length=50,  null=True,  default='')
    update_time = models.CharField(u'更新时间', blank=True, max_length=50, null=True, default='')