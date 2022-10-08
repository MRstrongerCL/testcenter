# -*- coding: UTF-8 -*-
#!/bin/sh
'''
Author: chenliang
Created Time: 2016/5/31
Describtion: Public method Manage
修改记录：
    2021-09-18： 陈亮 新增rsa加密解密算法
    2021-12-21: ra 新增随机身份证号、随机手机号
'''

import sys
import os
from time import time
import datetime
import subprocess
from time import sleep
import json
from requests import *
import re,csv
from random import Random
from ftplib import FTP
# from MyTelnet import do_telnet
import hashlib
import urllib
import xlrd

def take_screenshot(browser, save_fn="capture.png"):
    browser.save_screenshot(save_fn)


def ReadFile(filePath):
    if os.path.exists(filePath):
        return open(filePath, 'rb+')
    else:
        raise IOError("No such file : %s" % filePath)

def ReadCsvForList(csvPath):
    read_list = []
    with open(csvPath, 'rb+') as csvfile:
        read = csv.reader(csvfile)
        for line in read:
            read_list.append(line)
        csvfile.close()
    return read_list

def WiteCsvForList(csvPath,list):
    writelist = []
    # if os.path.exists(csvPath):
    #     with open(csvPath, 'r') as csvfile:
    #         for line in csvfile:
    #             newline = line.strip('\r\n').split(',')
    #             writelist.append(newline)
    # writelist.append(lists)
    # print writelist
    # with open(csvPath,'wb+') as csvfile:
    #     writer = csv.writer(csvfile)
    #     writer.writerows(writelist)
    with open(csvPath, 'ab+') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(list)
        csvfile.close()

def WiteCsvForLists(csvPath,lists):
    writelist = []
    # if os.path.exists(csvPath):
    #     with open(csvPath, 'r') as csvfile:
    #         for line in csvfile:
    #             newline = line.strip('\r\n').split(',')
    #             writelist.append(newline)
    # writelist.append(lists)
    # print writelist
    # with open(csvPath,'wb+') as csvfile:
    #     writer = csv.writer(csvfile)
    #     writer.writerows(writelist)
    with open(csvPath, 'ab+') as csvfile:
        writer = csv.writer(csvfile)
        for line in lists:
            writer.writerow(line)
        csvfile.close()

def WiteCsvForDict(csvPath,dicts,keys_list):
    # dicts：key是标题，value是数值
    # keys_list：标题栏
    with open(csvPath, 'ab+') as csvfile:
        writer = csv.DictWriter(csvfile,keys_list)
        writer.writerow(dicts)
        csvfile.close()

def Ascii2Chinese(str1):
    if str1==None:
        return None
    if type(str1)==int:
        str1=str(str1)
    return str1.decode("gb2312")

def Connect_AndroidDevice(device_ip_port,timeout=20):
    try:
        adb_env_path = os.environ['ANDROID_HOME']
    except KeyError as key:
        raise("adb connect device Failed,Have No the Environ,KeyError:%s" % key)
    adb_path = os.path.join(adb_env_path,'platform-tools\\adb.exe')
    connect_cmd_str = "%s connect %s" % (adb_path,device_ip_port)
    adbdevicecmd = "%s devices" % (adb_path)
    con = subprocess.Popen(connect_cmd_str,stdout=subprocess.PIPE)
    now_time = time()
    end_time = now_time + int(timeout)
    r_str = con.stdout
    status = 0
    return_faild_info = ''
    while now_time < end_time:
        result_str = str(r_str.readline())
        print (result_str)
        if len(result_str) > 5:
            return_faild_info = result_str
        matchstr = '%s\tdevice' % device_ip_port
        matchstr1 = 'connected to %s' % device_ip_port
        matchstr2 = 'already connected to %s' % device_ip_port
        if matchstr1 in result_str or matchstr2 in result_str:
            print ("adb Conect %s Success !!!" % device_ip_port)
            for i in range(5):
                adbdevices = subprocess.check_output(adbdevicecmd,shell=True)
                if matchstr in adbdevices:
                    status = 1
                    break
                else:
                    sleep(1)
            if status == 1:
                adbdvicesinfo = Ascii2Chinese(adbdevices)
                print (adbdvicesinfo)
                return True
        else:
            print ("Connect failed:, Go on ...")
            sleep(0.5)
        now_time = time()
    if status == 0:
        print ("Connect Failed, And timeout.Failed info:\n%s\nPlease check:\n\t1,adb environment;\n\t2,android device's adbwireless tool has start server;\n\t3,adb's port 5073 has used;\n\t4,the androied device had not authorisation " % return_faild_info)
        raise("Connect %s Failed, And timeout %sS .Failed info:\n%s\nPlease check:\n\t1,adb environment;\n\t2,android device's adbwireless tool has start server;\n\t3,adb's port 5073 has used;\n\t4,the androied device had not authorisation" % (device_ip_port,timeout,return_faild_info))

def Connect_LocalAndroidDevice(devicename,timeout=20):
    try:
        adb_env_path = os.environ['ANDROID_HOME']
    except KeyError as key:
        raise("adb connect device Failed,Have No the Environ,KeyError:%s" % key)
    adb_path = os.path.join(adb_env_path,'platform-tools\\adb.exe')
    matchstr = '%s\tdevice' % devicename
    adbdevicecmd = "%s devices" % (adb_path)
    now_time = time()
    end_time = now_time + int(timeout)
    status = 0
    return_faild_info = ''
    while now_time < end_time:
        adbdevices = subprocess.check_output(adbdevicecmd,shell=True)
        if matchstr in adbdevices:
            adbdvicesinfo = Ascii2Chinese(adbdevices)
            print (adbdvicesinfo)
            return True
        else:
            print ("Connect failed:, Go on ...")
            sleep(2)
        now_time = time()
    if status == 0:
        print ("Connect Failed, And timeout.Failed info:\n%s\nPlease check:\n\t1,adb environment;\n\t2,android device's adbwireless tool has start server;\n\t3,adb's port 5073 has used;\n\t4,the androied device had not authorisation " % return_faild_info)
        raise("Connect %s Failed, And timeout %sS .Failed info:\n%s\nPlease check:\n\t1,adb environment;\n\t2,android device's adbwireless tool has start server;\n\t3,adb's port 5073 has used;\n\t4,the androied device had not authorisation" % ('127.0.0.1',timeout,return_faild_info))

def disconnect_Android_device(device_ip_port):
    try:
        adb_env_path = os.environ['ANDROID_HOME']
    except KeyError as key:
        key = Ascii2Chinese(key)
        raise("adb connect device Failed,Have No the Environ,KeyError:%s" % key)
    adb_path = os.path.join(adb_env_path,'platform-tools\\adb.exe')
    disconnect_cmd_str = "%s disconnect %s" % (adb_path,device_ip_port)
    try:
        print("At first,if the pc had device connected, disconnect it ...")
        result = subprocess.call(disconnect_cmd_str,shell=True)
    except:
        pass
    if result==0:
        print ("disconnect %s Success !" % device_ip_port)
    elif result==1:
        print ("has no connected %s, don't need disconnect !" % device_ip_port)

def Start_Appium_Server(timeout=30,AppiumHome_path=None,port=4723,bootstrap_port=4724):
    timeout = int(timeout)
    p = os.getcwd()
    subprocess.call("taskkill /F /IM node.exe")

    if AppiumHome_path==None:
        try:
            AppiumHome_path = os.environ['APPIUM_HOME'].split(';')[0]
            print("Cmd: cd /d %s" % AppiumHome_path)
            os.system("cd /d %s" % AppiumHome_path)
            print("Current dir: %s" % os.getcwd())
        except KeyError as key:
            raise("Start Appium Server Failed,Have No the Environ,KeyError:%s" % key)

    print ("Appium Path: %s" % AppiumHome_path)
    appium_log_dir = os.path.join(AppiumHome_path,"RobotLog")
    if not os.path.exists(appium_log_dir):
        os.makedirs(appium_log_dir)
    appium_log_path = os.path.join(AppiumHome_path,"RobotLog\log_%s.txt" % Get_Now_TimeStr())
    appiumcmd_path = os.path.join(AppiumHome_path,'node_modules\\.bin\\appium.cmd')
    # cmd_str ='start appium.cmd ' +'-a 127.0.0.1 -p ' + str(port) +' --bootstrap-port ' + str(bootstrap_port) + ' --session-override'+ ' --log "' + appium_log_path +'" --command-timeout 600'
    cmd_str =appiumcmd_path +' -a 127.0.0.1 -p ' + str(port) +' --bootstrap-port ' + str(bootstrap_port) + ' --session-override'+ ' --log "' + appium_log_path +'" --command-timeout 600'
    print (cmd_str)

    # 创建cmd执行启动appium
    startAppiumCmd_path = os.path.join(p,'StartAppium.cmd')
    if os.path.exists(startAppiumCmd_path):
        os.system('del /f/q %s' % startAppiumCmd_path)
    f = open(startAppiumCmd_path,"a")
    f.write(cmd_str)
    f.flush()
    f.close()

     #创建vbs执行appium后台程序
    startAppiumVbs_path = os.path.join(p,'startAppiumVbs.VBS')
    if not os.path.exists(startAppiumVbs_path):
        startbackVbs_str = 'Set ws = CreateObject("Wscript.Shell")\nws.run "cmd /c StartAppium",vbhide'
        f = open(startAppiumVbs_path,'a')
        f.write(startbackVbs_str)
        f.flush()
        f.close()
    # 监控appium启动成功
    app = subprocess.call(startAppiumVbs_path,shell=True,stdout=subprocess.PIPE)
    # app = os.system(startAppiumVbs_path)
    now_time = time()
    end_time = now_time + timeout
    status = 0
    result = 'Init Null'
    while now_time < end_time:
        linshifile = os.path.join(p,'linshi.txt')
        cmdstr = 'netstat -ano | findstr "4723" > %s' % linshifile
        os.system(cmdstr)
        f = open(linshifile,'r')
        rlinelist = f.readlines()
        f.close()
        if rlinelist != []:
            result = rlinelist[0]
            if 'LISTENING' in result:
                print (result)
                status = 1
                os.system('del /s/q %s' % linshifile)
                break
            else:
                sleep(0.5)
        now_time = time()
    if status ==1 :
        print ("Start Appium Success !!!")
        print('Start Appium Success,%s' % result)
        sleep(2)
        return True
    else:
        print ("Start Appium Failed !!!")
        os.system('del /s/q %s' % linshifile)
        raise('Start Appium Failed and Timeout %sS, Please Check:\n\t1,APPIUM_HOME environ Path;\n\t2,the port 4073 had used;\n\t3,wait time is not enough' % (timeout,result))

def Kill_Adb():
    r = os.system("taskkill /F /IM adb.exe")
    print("taskkill /F/IM adb.exe stauts: %s" % r)

def Kill_Appium():
    r = os.system("taskkill /F /IM appium.exe")
    print("taskkill /F/IM appium.exe stauts: %s" % r)

def Numbers_Should_Bigthan(num1,num2):
    '''
    num1 >  num2
    '''
    try:
        if '.' in str(num1) or '.' in str(num2):
            num1 = float(num1)
            num2 = float(num2)
        else:
            num1 = int(num1)
            num2 = int(num2)
        if num1>num2:
            return True
        else:
            return False
    except:
        print ("This Time Compare Failed")
        return False

def Numbers_Should_Smallthan(num1,num2):
    '''
    num1 <  num2
    '''
    try:
        if '.' in str(num1) or '.' in str(num2):
            num1 = float(num1)
            num2 = float(num2)
        else:
            num1 = int(num1)
            num2 = int(num2)
        if num1<num2:
            return True
        else:
            return False
    except:
        print ("This Time Compare Failed")
        return False

def Numbers_Should_Equal(num1,num2):
    '''
    num1 ==  num2
    '''
    try:
        print ("num1:{} -- num2:{}".format(num1,num2))
        print ("type1:{} -- type2:{}".format(type(num1),type(num2)))
        if '.' in str(num1) or '.' in str(num2):
            num1 = float(num1)
            num2 = float(num2)
        else:
            num1 = int(num1)
            num2 = int(num2)
        print ("num1:{} -- num2:{}".format(num1,num2))
        print ("type1:{} -- type2:{}".format(type(num1),type(num2)))
        if num1 == num2:
            return True
        else:
            return False
    except:
        print ("This Time Compare Failed")
        return False

def Numbers_Eval(numbers_str):
    result = False
    try:
        numbers_str = str(numbers_str)
        result = eval(numbers_str)
        return result
    except Exception as e:
        print (e)
        print("Eval Failed: %s" % e)
        return result


class CompareException(Exception):
    pass
    # def __init__(self, first, second):
    #     Exception.__init__(self)
    #     self.first = first
    #     self.second = second
    #     print "Compare Error: first-%s, second-%s" % (self.first,self.second)

def assert_Bigthan(arg1,arg2, msg=None):
    '''
    arg1 > arg2
    '''
    try:
        if arg1 > arg2:
            return True
        else:
            print (msg)
            return False
    except Exception as e:
        print ("Compare Failed: ")
        raise e

def assert_Smallthan(arg1,arg2, msg=None):
    '''
    arg1 < arg2
    '''
    try:
        if arg1 < arg2:
            return True
        else:
            print (msg)
            return False
    except Exception as e:
        print ("Compare Failed: ")
        raise e

def assert_Equal(arg1,arg2, msg=None):
    '''
    arg1 = arg2
    '''
    try:
        # print arg1,type(arg1),arg2,type(arg2)
        if arg1 == arg2:
            return True
        else:
            print (msg)
            return False
    except Exception as e:
        print ("Compare Failed: ")
        raise e

def assert_Not_Equal(arg1,arg2, msg=None):
    '''
    arg1 = arg2
    '''
    try:
        if arg1 != arg2:
            return True
        else:
            print (msg)
            return False
    except Exception as e:
        print ("Compare Failed: ")
        raise e

def assert_isNone(arg,msg=None):
    try:
        if arg == None:
            return True
        else:
            print (msg)
            return False
    except Exception as e:
        print ("Compare Failed: ")
        raise e

def assert_contains(arg_big,arg_small,msg=None):
    try:
        if arg_small in arg_big:
            return True
        else:
            print (msg)
            return False
    except Exception as e:
        print ("Compare Failed: ")
        raise e

def assert_isnotNone(arg,msg=None):
    try:
        if arg != None:
            return True
        else:
            print (msg)
            return False
    except Exception as e:
        print ("Compare Failed: ")
        raise e

def assert_in(arg1,arg2,msg=None):
    try:
        if arg1 in arg2:
            return True
        else:
            print(msg)
            return False
    except Exception as e:
        print ("Compare Failed: %s not in %s" % (arg1,arg2))
        raise e

def str_2_int(strs):
    try:
        rint = int(strs)
    except:
        rint = 0
    return rint

def str_2_float(strs):
    try:
        rint = float(strs)
    except:
        rint = 0
    return rint

def int_2_strlist(input):
    new = list(str(input))
    int_list = []
    for i in new:
        int_list.append(int(i))
    print(int_list)
    return int_list

def Get_Date(timetype='today',days=0):
    now=datetime.datetime.now()
    if timetype.lower()=='today':
        date = now
    elif timetype.lower()=='tomorrow':
        date = now + datetime.timedelta(days=1)
    elif timetype.lower()=='yesterday':
        date = now - datetime.timedelta(days=1)
    elif timetype.lower()=='auto':
        date = now + datetime.timedelta(days=days)
    else:
        print("No this type %s" % timetype)
        return False
    month = "{:0>2}".format(date.month)
    day = "{:0>2}".format(date.day)
    r_str = "%s-%s-%s" % (date.year, month, day)
    return r_str

def Get_Now_TimeStr():
    now=datetime.datetime.now()
    r_str = ("{}-{:0>2}-{:0>2}_{:0>2}-{:0>2}-{:0>2}".format(now.year,now.month,now.day,now.hour,now.minute,now.second))
    return r_str

def Get_Current_Time():
    now=datetime.datetime.now()
    r_str = ("%s-%s-%s %s:%s:%s:%s" % (now.year,now.month,now.day,now.hour,now.minute,now.second,now.microsecond))
    return r_str


def Get_Next_Time(day=0,hour=0,minute=0,second=0):
    add_time = datetime.timedelta(days=day,hours=hour,minutes=minute,seconds=second)
    now=datetime.datetime.now()
    next = now + add_time
    r_str = ("{}-{:0>2}-{:0>2} {:0>2}:{:0>2}:{:0>2}".format(next.year,next.month,next.day,next.hour,next.minute,next.second))
    return r_str

def Get_Tomrrow_Time():
    now=datetime.datetime.now()
    tomrrow = now + datetime.timedelta(days=1)
    r_str = '{:%Y-%m-%d %X}'.format(tomrrow)
    return r_str

def Get_Yesterday_Time(days=-1):
    now=datetime.datetime.now()
    tomrrow = now + datetime.timedelta(days)
    r_str = '{:%Y-%m-%d %X}'.format(tomrrow)
    return r_str

def productCurrentTimeStamp(days=0,hours=0,minutes=0,seconds=0,Mtype=True,day_stamp=False):
    '''
    生产时间戳 （参数不为0时，表示未来时间戳）
    :param days: 天
    :param hours: 时
    :param minutes: 分
    :param seconds: 秒
    :param Mtype:  true/false  是否毫秒级
    :return: timeStamp: 时间戳
    day_stamp:只返回年月日的时间戳，时分秒为0
    '''
    #生成时间戳
    import time
    # t = time.time()
    # print (t)                       #原始时间数据
    # print (int(t))                  #秒级时间戳
    # print (int(round(t * 1000)))    #毫秒级时间戳
    # nowTime = lambda:int(round(t * 1000))
    # print (nowTime())             #毫秒级时间戳，基于lambda
    # print (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))  # 日期格式化
    # #日期转成时间戳
    # dt = '2018-01-01 10:40:30'
    # ts = int(round(time.mktime(time.strptime(dt, "%Y-%m-%d %H:%M:%S"))))
    # print (ts)
    # #将秒级时间戳转为日期
    # ts = 1515774430
    # dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))
    # print(dt)
    add_time = datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    now = datetime.datetime.now()
    next = now + add_time
    if Mtype:
        r_str = ("%s-%s-%s %s:%s:%s:%s" % (next.year, next.month, next.day, next.hour, next.minute, next.second, next.microsecond))
        ts = round(time.mktime(time.strptime(r_str, "%Y-%m-%d %H:%M:%S:%f")),3)
        timeStamp = int(ts * 1000)
        if day_stamp:
            r_str = ("%s-%s-%s %s:%s:%s:%s" % (
            next.year, next.month, next.day, 0,0, 0, 0))
            ts = round(time.mktime(time.strptime(r_str, "%Y-%m-%d %H:%M:%S:%f")), 3)
            timeStamp = int(ts * 1000)

    else:
        r_str = ("%s-%s-%s %s:%s:%s" % (next.year, next.month, next.day, next.hour, next.minute, next.second))
        ts = round(time.mktime(time.strptime(r_str, "%Y-%m-%d %H:%M:%S")))
        timeStamp = int(ts)
    return timeStamp

def Run_exe_or_bat(path):
   subprocess.Popen(path)

def random_int(randomlength=12):
    str = ''
    chars1='123456789'
    chars2='0123456789'
    random = Random()
    try:
        randomlength = int(randomlength)
    except:
        pass
    fistrno = random.choice(chars1)
    for i in range(randomlength-1):
        str += random.choice(chars2)
    all_strs = fistrno + str
    all_no = int(all_strs)
    return all_no

def random_nums(randomlength=12):
    str = ''
    chars = '0123456789'
    length = len(chars) - 1
    random = Random()
    try:
        randomlength = int(randomlength)
    except:
        pass
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str

def random_strs(randomlength=12):
    str = ''
    chars = 'AaBbCcDdEeFf0123456789'
    length = len(chars) - 1
    random = Random()
    try:
        randomlength = int(randomlength)
    except:
        pass
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str

def Utf8_To_GBK(strs):
    try:
        print (type(strs))
        strs = strs.decode('utf-8').encode('gbk')
    except Exception as e:
        print (e)
    return strs

def Unicode_To_GBK(strs):
    try:
        print (type(strs))
        strs = strs.encode('gbk')
    except Exception as e:
        print (e)
    return strs

def Utf8_To_Unicode(strs):
    try:
        print (type(strs))
        strs = strs.decode('utf-8')
    except Exception as e:
        print(e)
    return strs

def parse_json(arg):
    new_arg = json.loads(arg)
    return new_arg

def str_decode_uicode(arg):
    try:
        arg = str(arg)
        newarg = arg.decode('utf-8')
    except:
        newarg = arg
    return newarg

def list_decode_uicode(arg):
    new_arg = []
    for i in arg:
        new_arg.append(i.decode('utf-8'))
    return new_arg

def dict_decode_uicode(arg):
    new_arg = {}
    for key,value in arg.items():
        new_arg[key]=value.decode('utf-8')
    return new_arg

def str_encode_utf8(strs):
    try:
        newstr = strs.encode('utf-8')
    except:
        newstr = strs
    return newstr

def str_encode_utf8_butCh(strs):
    try:
        strs = strs.decode('utf8')
    except:
        pass
    #matcher = re.compile(u'[\u4e00-\u9fa5]+')
    newstr = ''
    for one in strs:
        #match = matcher.search(ustrs)
        #if match:
        print ("Star Print uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu")
        print (one)
        if one >= u'\u4e00' and one<=u'\u9fa5':
            # newstr = ''
            # for uchar in strs:
            #     if uchar >= u'\u4e00' and uchar<=u'\u9fa5':
            #         uchar = uchar.encode("utf8")
            #     else:
            #         uchar = uchar.encode('utf-8')
            #     newstr = newstr + uchar
            newone = one.encode('gb2312')
            print ("--------------------------")
            print (newone)
        else:
            newone = one.encode('utf-8')
        newstr = newstr + newone
    return newstr

def list_encode_utf8(arg):
    new_arg = []
    for i in arg:
        new_arg.append(i.encode('utf-8'))
    return new_arg

def dict_encode_utf8(arg):
    new_arg = {}
    for key,value in arg.items():
        new_arg[key]=value.encode('utf-8')
    return new_arg

def Rnum_to_Numstr(r_num):
    typearg = type(r_num)
    if typearg == list:
        n_list = []
        for dit in r_num:
            if type(dit) == dict:
                n_dit = {}
                for key,value in dit.items():
                    new_value = Rnum_to_Numstr(value)
                    n_dit[key] = new_value
            elif type(dit) == list:
                n_dit = []
                for itm in dit:
                    n_dit.append(Rnum_to_Numstr(itm))
            else:
                n_dit = rnumber_parse_str(dit)
            n_list.append(n_dit)
        new_arg = n_list
    elif typearg == dict:
        n_dict = {}
        for key,value in r_num.items():
            if type(value) == dict:
                n_dit = {}
                for key1,value1 in value.items():
                    new_value1 = Rnum_to_Numstr(value1)
                    n_dit[key1] = new_value1
            elif type(value) == list:
                n_dit = []
                for itm in value:
                    n_dit.append(Rnum_to_Numstr(itm))
            else:
                 n_dit = rnumber_parse_str(value)
            n_dict[key] = n_dit
        new_arg = n_dict
    else:
        new_arg = rnumber_parse_str(r_num)
    return new_arg

def str_to_listordict(strs):
    list1 = eval(strs)
    return list1

def is_number(strs):
    """判断一串字符或数字是否是数字"""
    print ("*** This is is_number Function ***")
    if type(strs)==str:
        try:
            strs = strs.encode('utf-8')
        except Exception as e:
            print ("Can't encode strs : %s " % strs)
    try:
        if strs != '':
            # if strs[0] != '0':
            #     uchar = float(strs)
            #     return True
            if len(str(strs)) > 1:
                if strs[0] == '0':
                    return False
            uchar = float(strs)
            return True
    except Exception as e:
        return False

def str_parse_number(num_strs):
    try:
        number = int(num_strs)
        return number
    except:
        number = float(num_strs)
        return number

def rnumber_parse_str(r_num):
    try:
        matcher = re.compile('r[0-9]+[\.]?[0-9]*')
        match = matcher.search(r_num)
        if match:
            new_strs = r_num.strip("r")
        else:
            new_strs = r_num
        return new_strs
    except:
        print ("number_parse_str error : %s ,%s" % (r_num,type(r_num)))
        return r_num

def Create_My_Dictionary(*args):
    '''
    create dictionary
    :param args: a='abc',b=[1,2,3]
    :return: new_dict:{"a"='abc';'b':[1 2 3]}
    '''
    try:
        new_dict = {}
        for eachone in args:
            l = eachone.split('=')
            key = l[0]
            value = eval(l[1])
            new_dict[key]=value
        return new_dict
    except Exception as e:
        raise e

def Arg1_Contain_Arg2(arg1,arg2):
    try:
        if arg2 in arg1:
            return True
        else:
            return False
    except Exception as e:
        raise e

def Remove_Str_From_List(l,rs,count=None):
    if count==None:
        c = l.count(rs)
        for i in range(c):
            l.remove(rs)
    else:
        c = int(count)
        sc = l.count(rs)
        if sc <= c:
            tc = sc
        else:
            tc = c
        for i in range(tc):
            l.remove(rs)
    return l

def Post_Http(url,RFdict1):
    jsons = json.dumps(RFdict1)
    https = post(url,jsons)
    return https.text

def Ftp_Put_PadLog(dirpath,store_url_port):
    store_ip = store_url_port.split(':')[0]
    if os.path.exists(dirpath):
        ftp_ip = '10.66.161.36'
        ftp_port = 21
        ftp_user = 'robot'
        ftp_passwd = '123456'
        ftp=FTP()
        # ftp.set_debuglevel(2)
        ftp.connect(host=ftp_ip,port=ftp_port,timeout=999)
        ftp.login(user=ftp_user,passwd=ftp_passwd)
        print (ftp.getwelcome())
        newpath = os.path.join(dirpath,os.listdir(dirpath)[0])
        newfilename = '[%s]_' % store_ip + os.path.split(dirpath)[1]
        filename = newfilename + '.txt'
        ftp.cwd("PadLog")
        ftp.storbinary('STOR %s' % filename, open(newpath,'rb'))
        # print ftp.dir()
        # ftp.set_debuglevel(0)
        ftp.quit()
        print('put the pad log to ftp server Success !!!')
    else:
        raise("Has no the file path : %s" % dirpath)

def Parse_Decimal_SqlData(sqldata):
    data = str(sqldata)
    match_str ='\(\(([a-zA-z]+.?[a-zA-z]*\((.+)\)),\),\)'
    p = re.compile(match_str)
    m = p.match(data)
    if m:
        print("this str should parse sql tuple data ...")
        old_s = m.group(1)
        new_s = m.group(2)
        data = data.replace(old_s,new_s)
    re_str = eval(data)
    return re_str

def Re_Get_Html_Str(htmlstr,t_re):
    '''
    Get target str From html strs Use Re Function

    :param htmlstr:  all html strs

    :param t_re:  target re

    :return: math_str
    '''
    t_xiaofei = '.+id="amount">([0-9]+.[0-9]+)<.+'
    t_xf =  '.+id="serviceCharge-tip">([0-9]+.[0-9]+)<.+'
    t_service =  '.+id="tip-amount">([0-9]+.[0-9]+)<.+'
    t_youhui =  '.+id="discount-amount">([0-9]+.[0-9]+)<.+'
    t_yingshou =  '.+id="should-amount">([0-9]+.[0-9]+)<.+'
    # t_re = t_yingshou
    htmllist = htmlstr.split('\n')
    p = re.compile(t_re)
    for line in htmllist:
        math = p.match(line)
        if math:
            print (line)
            return math.group(1)

def old_md5(sign_str):
    print(sign_str)
    sign_u = urllib.quote(sign_str)
    # print(sign_u)
    sign_u_l = sign_u.lower()
    # print(sign_u_l)
    s = sign_u_l.encode('unicode_escape')
    # print(s)
    _sign = hashlib.md5(s).hexdigest()
    # print(_sign)
    return  _sign

def new_md5(sign_str,urlencode_status=True):
    # print(sign_str)
    if urlencode_status:
        sign_u = urllib.urlencode({"value": sign_str})
        sign_u = sign_u.split('=')[-1]
    else:
        sign_u = sign_str
    print(sign_u)
    # sign_u_l = sign_u.lower()
    # print(sign_u_l)
    _sign = hashlib.md5(sign_u.encode('utf-8')).hexdigest()
    # print(_sign)
    return  _sign

def get_rows(excelname,sheet_index=0,excel_ty=1,colnum=0,projectname='ccs1'):
    """获取sheet1的不为空的行数量
       excelname：excel名称
       sheet_index：sheet索引
       excel_ty=1:excel 第一列取值重复不去重计算；取值2：去重计算列数量
       colnum:代表第几列数， 取值某一行的第几列
    """
    filepath=os.path.join(os.path.dirname(os.path.dirname(__file__)),'Package')
    project_filepath=list(x for x in os.walk(filepath, 'Package'))
    if projectname not in project_filepath[0][1]:
        os.mkdir(os.path.join(filepath,projectname))
    excel_path=os.path.join(os.path.join(filepath,projectname),excelname)
    workbook = xlrd.open_workbook(excel_path)
    # 根据sheet索引或者名称获取sheet内容
    num=0
    sheet2 = workbook.sheet_by_index(sheet_index)  # sheet索引从0开始
    row_values=[]
    for i in range(sheet2.nrows):
        if sheet2.row_values(i)[colnum] !='':
            num=num+1
            row_values.append(sheet2.row_values(i)[0])
    # 去掉表头
    set_row=set(row_values)
    if excel_ty == 1:
        return num-1
    if excel_ty == 2:
        return  len(set_row)-1

def write_excel(excelnme,content,projectname='ccs1'):
    """写入exel
    excelnme:excel名称
    content:写入的内容
    project:项目名称，与package中的自己文件同名
    """
    filepath=os.path.join(os.path.dirname(os.path.dirname(__file__)),'Package')
    project_filepath=list(x for x in os.walk(filepath, 'Package'))
    if projectname not in project_filepath[0][1]:
        os.mkdir(os.path.join(filepath,projectname))
    excel_path=os.path.join(os.path.join(filepath,projectname),excelnme)
    f = open(excel_path, 'wb+')
    f.write(content)
    f.close()


def get_row_value(excelname,sheet_index,row_num,projectname='ccs1'):
    """获取某行的取值
       excelname：excel名称
       sheet_index：sheet的索引
       row_num：行数
    """
    filepath=os.path.join(os.path.dirname(os.path.dirname(__file__)),'Package')
    project_filepath=list(x for x in os.walk(filepath, 'Package'))
    if projectname not in project_filepath[0][1]:
        os.mkdir(os.path.join(filepath,projectname))
    excel_path=os.path.join(os.path.join(filepath,projectname),excelname)
    workbook = xlrd.open_workbook(excel_path)
    # 根据sheet索引或者名称获取sheet内容
    sheet2 = workbook.sheet_by_index(sheet_index)  # sheet索引从0开始
    return sheet2.row_values(row_num)

def get_col_value(excelname,sheet_index,col_num,projectname='ccs1'):
    """获取某列的取值
       excelname：excel名称
       sheet_index：sheet的索引
       row_num：列数
    """
    filepath=os.path.join(os.path.dirname(os.path.dirname(__file__)),'Package')
    project_filepath=list(x for x in os.walk(filepath, 'Package'))
    if projectname not in project_filepath[0][1]:
        os.mkdir(os.path.join(filepath,projectname))
    excel_path=os.path.join(os.path.join(filepath,projectname),excelname)
    workbook = xlrd.open_workbook(excel_path)
    # 根据sheet索引或者名称获取sheet内容
    sheet2 = workbook.sheet_by_index(sheet_index)  # sheet索引从0开始
    return sheet2.col_values(col_num)

def datetotimestamp(data):
    """timeclass：转换类型1、2
       timestamp：时间戳
    """
    import time
    from datetime import datetime
    dt = datetime.strptime(data, '%Y-%m-%d')
    tp = dt.timetuple()
    return time.mktime(tp)

def dict_to_json(par_json):
    return json.dumps(par_json)

def Byte2Str(b_str):
    return str(b_str, encoding='utf-8')

def randomPhone():
    #随机手机号
    headlist = ["147", "157", "150", "151", "152", "153", "155", "156", "157", "158", "159", "130", "131", "132",
                "133", "134", "135", "136", "137", "138", "139", "180", "182", "185", "186", "187", "188", "189"]
    tail = ""
    random = Random()
    while (len(tail) != 8):
        tail = str(random.randint(00000000, 99999999))
    head = str(random.choice(headlist))
    phone = head + tail
    return phone

def randomID():
    #随机身份证
    random = Random()
    headChoice = [511602, 511603, 511621, 511622, 511623, 511681, 511700, 511701, 511702, 511703, 511722, 511723,
           511725, 511781, 511800, 511801, 511802, 511803, 511822, 511823, 511824, 511825, 511826, 511827, 511900,
           511901, 511902, 511903, 511921, 511922, 511923, 512000, 512001, 512002, 512021, 512022, 512081, 513200,
           513221, 513222, 513223, 513224, 513225, 513226, 513227, 513228, 513229, 513230, 513231, 513232, 513233,
           513300, 513321, 513322, 513323, 513324, 513325, 513326, 513327, 513328, 513329, 513330, 513331, 513332,
           513333, 513334, 513335, 513336, 513337, 513338, 513400, 513401, 513422, 513423, 513424, 513425, 513426,
           513427, 513428, 513429, 513430, 513431, 513432, 513433, 513434, 513435, 513436, 513437, 520000, 520100,
           520101, 520102, 520103, 520111, 520112, 520113, 520115, 520121, 520122, 520123, 520181, 520200, 520201,
           520203, 520221, 520222, 520300, 520301, 520302, 520303, 520321, 520322, 520323, 520324, 520325,]
    idhead = str(random.choice(headChoice))
    idyear = str(random.randint(1970, 2012))
    iddate = datetime.date.today() + datetime.timedelta(days=random.randint(1, 366))
    idcard = idhead + idyear + iddate.strftime('%m%d') + str(random.randint(100, 300))
    i = 0
    count = 0
    weight = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    #权重项
    checkcode = {'0': '1', '1': '0', '2': 'X', '3': '9', '4': '8', '5': '7', '6': '6', '7': '5', '8': '5', '9': '3','10': '2'}
    # 校验码映射
    for i in range(0, len(idcard)):
        count = count + int(idcard[i]) * weight[i]
        idcard = idcard + checkcode[str(count % 11)]  # 算出校验码
        return idcard

if __name__=='__main__':
    # get_col_value()
    # f = open(r"C:\Users\chenliang\Desktop\testhtml.html","r")
    # all = f.read()
    # f.close()
    a = Get_Date(timetype='auto',days=-3)
    print(a)