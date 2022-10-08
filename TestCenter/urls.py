"""TestCenter URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path
from . import views
from Bug import BugViews

urlpatterns = [
    url(r'^$',views.index_view),
    path('admin/',admin.site.urls),
    path('index/',views.index_view),
    path('login/',views.login_view),
    path('reset/',views.resetPwd),
    path('register/',views.register_view),
    path('logout/',views.logout_view),
    path('testtools/',views.testtools),
    path('usermanage/',views.userManage),
    path('buglist/',BugViews.buglist),
    path('total/',BugViews.total),
    path('total_update/',BugViews.total_update),
    path('query_bugs_total/',BugViews.query_bugs_total),
    path('mangesetting/',BugViews.manage_setting),
    path('query_bugs/',BugViews.queryBugList),
    path('uploadexcel/',BugViews.readExcelAndWrite),
    path('uploadapi/',BugViews.readApiAndWrite),
    path('addRuncases/',BugViews.addRuncases),
    path('updateTesterInfo/',BugViews.updateTesterInfo),
    path('updateDeveloperInfo/',BugViews.updateDeveloperInfo),
    path('updateProgramTechScores/',BugViews.updateProgramTechScores),
    path('updateProgramTechScores_new/',BugViews.updateProgramTechScores_new),
    path('addProgram/',BugViews.addProgram),
    path('addIteration/',BugViews.addIteration),
    path('iteration/',BugViews.iteration),
    path('iteration_update/',BugViews.iteration_update),
    path('query_bugs_iteration/',BugViews.query_bugs_iteration),

    path('recently/', BugViews.recently),
    path('recently_update/', BugViews.recently_update),
    path('query_bugs_recently/', BugViews.query_bugs_recently),

    path('bugModule/',BugViews.module),
    path('module_update/',BugViews.module_update),
    path('getIterations/',BugViews.getIterations),
    path('getRootProgramIterations/',BugViews.getRootProgramIterations),
    path('getRootProgramTargetIterationInfo/',BugViews.getRootProgramTargetIterationInfo),
    path('query_bugs_module/',BugViews.query_bugs_module),

    path('bugType/', BugViews.bugtype),
    path('type_update/', BugViews.type_update),
    path('query_bugs_type/', BugViews.query_bugs_type),

    path('developQuality/', BugViews.developer),
    path('developer_update/', BugViews.developer_update),
    path('query_bugs_developer/', BugViews.query_bugs_developer),

    path('testerQuality/', BugViews.tester),
    path('tester_update/', BugViews.tester_update),
    path('query_bugs_tester/', BugViews.query_bugs_tester),
    path('score_rate_setting/', BugViews.score_rate_setting),
    path('update_Rage/', BugViews.updateRage),
    path('task_score/', BugViews.task_score),
    path('leader_score/', BugViews.leader_score),
    path('score_statistics/', BugViews.score_statistics),
    path('score_statistics_update/', BugViews.score_statistics_update),
    path('query_score_statistics/', BugViews.query_score_statistics),
    path('performance_statistics_update/', BugViews.performance_statistics_update),

    path('efficiency/', BugViews.efficiency),
    path('autotask/', BugViews.autotask),

    path('wordcloud/',views.wordcloud)
]
