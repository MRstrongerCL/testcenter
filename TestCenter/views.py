# coding:utf-8
from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from rest_framework.views import APIView
from django.db import transaction
from django import forms
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib.auth.models import  Group,User,Permission
from pyecharts.globals import SymbolType
from pyecharts.charts import Bar, Pie, Page, WordCloud
from pyecharts.faker import Faker
from pyecharts import options as opts
from TestCenter.LogicLib import OperationDB
from TestCenter.LogicLib.BusinessFunc.mycharts import myline
from TestCenter.LogicLib.BusinessFunc.forms import UserForm

import json
REMOTE_HOST='127.0.0.1:8000'


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

def hello(request):
    return HttpResponse('Hello world!')

def runoob(request):
    context = {}
    context['hello'] = 'Hello World use templats!'
    context['name'] = '中科汇源测试平台'
    context['views'] = ['质量管理','测试工具','思维总结']
    context['time'] = datetime.now()
    context['chars'] = 'abcdefghjklmnopq'
    context['views_str'] = "<a href='https://www.runoob.com/'>点击跳转</a>"
    return render(request,'runoob.html',context)

def layui(request):
    return render(request,'layui.html')

def testtools(request):
    contextdict = {}
    contextdict['tools_style'] = 'color: #fff;font-weight:bold'
    return render(request,'testtools/toolsindex.html',contextdict)

def userManage(request):
    contextdict = {}
    contextdict['users_style'] = 'color: #fff;font-weight:bold'
    return render(request,'usermanage/usermanageIndex.html',contextdict)

@login_required(login_url='/login/')
def index_view(request):
    contextdict = {}
    contextdict['quality_style'] = 'color: #fff;font-weight:bold'
    # current_user_set = request.user
    # print(current_user_set)
    # current_group_set = Group.objects.get(user=current_user_set)
    # print(current_group_set)
    # pers = current_user_set.get_group_permissions()
    # print(pers)
    # group_name = current_group_set.name
    # if 'Bug.add_detail' not in pers:
    #     print(group_name)
    return render(request, 'index.html', contextdict)

def login_view(request):
    if request.method == "POST":
        username = request.POST['Username']
        password = request.POST['Password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            message = "登录成功！"
            return json_response({},msg=message)
        else:
            message = "用户或密码不正确！"
            return json_error({},msg=message)
    else:
        return render(request, 'login.html')

@login_required
def resetPwd(request):
    if request.method == "POST":
        username = request.POST['Username']
        password = request.POST['Password']
        password2 = request.POST['PasswordCopy']
        cur_username = request.user.username
        if cur_username != username:
            message = "修改用户不是当前登录用户！"
            return json_error({}, msg=message)
        if password != password2:
            message = "两次密码输入不一致！"
            return json_error({}, msg=message)
        else:
            try:
                user = User.objects.get(username=username)
            except:
                message = "用户不存在！"
                return json_error({}, msg=message)
            if user is not None and user != []:
                user.set_password(password)
                user.save()
                message = "重置成功！"
                logout(request)
                return json_response({},msg=message)
            else:
                message = "用户不存在！"
                return json_error({},msg=message)
    else:
        return render(request, 'reset.html')

def register_view(request):
    if request.method == 'POST':
        user = request.POST['Username']
        pwd = request.POST['Password']
        email = request.POST['Email']
        try:
            user = User.objects.create_user(username=user, password=pwd, email=email)
        except:
            message = "用户名或邮箱已存在！"
            return json_error({}, msg=message)
        if user:
            message = "注册成功！"
            return json_response({},msg=message)
        else:
            message = "注册失败！"
            return json_error({},msg=message)

def logout_view(request):
    logout(request)
    return redirect('/login/')

# ==============================  案例调试 =============================

def wordcloud(request):
    words = [
    ("Sam S Club", 10000),
    ("Macys", 6181),
    ("Amy Schumer", 4386),
    ("Jurassic World", 4055),
    ("Charter Communications", 2467),
    ("Chick Fil A", 2244),
    ("Planet Fitness", 1868),
    ("Pitch Perfect", 1484),
    ("Express", 1112),
    ("Home", 865),
    ("Johnny Depp", 847),
    ("Lena Dunham", 582),
    ("Lewis Hamilton", 555),
    ("KXAN", 550),
    ("Mary Ellen Mark", 462),
    ("Farrah Abraham", 366),
    ("Rita Ora", 360),
    ("Serena Williams", 282),
    ("NCAA baseball tournament", 273),
    ("Point Break", 265),
    ]

    c = (
        WordCloud()
        .add("", words, word_size_range=[20, 100])
        .set_global_opts(title_opts=opts.TitleOpts(title="WordCloud-基本示例"))
    )
    return HttpResponse(c.render_embed())

def university_picture(request):
    l = myline()  # 生成图像实例
    contextdict = dict(
        quality_style='color: #fff;font-weight:bold',
        view_v2='layui-nav-itemed',
        iteration_v2_style='background-color: #009688;color: #fff;',
        myechart=l.render_embed() # 必须要有
    )
    # return HttpResponse(template.render(context, request))
    return render(request,'iteration.html',contextdict)

# 数据库操作
def testdb(request):
    test1 = OperationDB.readExcelAndWrite2DB()
    return HttpResponse("<p>数据添加成功！</p>")