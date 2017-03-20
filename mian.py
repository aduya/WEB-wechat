# -*- coding: utf-8 -*-
from itchat.content import *
from threading import Thread
import itchat
import time
import datetime
import os
import random
from app.models import User,Wxbot

global userid,SETTING,JSF,islogin,IsSendMsgNow
SETTING=Wxbot().GetSetting()#获取设置
userid=False#用户标识
islogin=False#是否登录成功
IsSendMsgNow=True #是否发送小i系
JSF=0#初始化僵尸粉个数
#收到好友邀请自动添加好友
@itchat.msg_register(FRIENDS)
def add_friend(msg):
    itchat.add_friend(**msg['Text'])
    itchat.send_msg('Nice to meet you!', msg['RecommendInfo']['UserName'])

@itchat.msg_register(NOTE)
def get_uin(msg):
    global JSF,IsSendMsgNow
    if '朋友验证请求' in msg['Text'] or '对方拒收' in msg['Text']:
        JSF=JSF+1
        itchat.set_alias(msg['FromUserName'],'A00000【僵尸粉】%s'%JSF)
    if '过于频繁' in msg['Text']:
        IsSendMsgNow=False



def wx_logout():
    '''
    强行关闭微信pid
    :return:
    '''
    pid = '%s' % os.getpid()
    os.system('taskkill /PID %s /F /T' % pid)

#UPD 通讯
def UDP():
    global userid,islogin
    import socket
    import os
    starttime = datetime.datetime.now()
    while True:
        ss = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # 绑定端口:
            ss.bind(('127.0.0.1', 8888))
            while True:
                data, addr = ss.recvfrom(1024)
                text = data.decode('utf-8')
                if text == 'pid':
                    pid = '%s' % os.getpid()
                    ss.sendto(pid.encode(), addr)
                    ss.close()
                    break
                if 'userid' in text:
                    if int(text[6:]) ==99999:
                        userid = '陌生人'
                    else:
                        userid = User.query.get(int(text[6:]))
                    print(userid)
            break
        except BaseException as e:
            print(e)
    while True:
        endtime = datetime.datetime.now()
        if (endtime - starttime).seconds > 60:
            print('超过110秒')
            wx_logout()
        if islogin:
            print('关闭检测时间线程')
            return False
        time.sleep(5)

def notice(text):
    itchat.send(text, toUserName='filehelper')

def Sendmsg(text):
    global JSF,userid,IsSendMsgNow
    sendnum=0
    allnum=0
    friend=itchat.get_friends(True)
    Newtext=text
    for n in friend:
        sendnum =sendnum+1
        allnum=allnum+1
        #判断是否等待是否发送消息频繁
        if not IsSendMsgNow:
            notice('发送消息频繁，等待 %s 秒后继续发送 '%SETTING['SendOften'])
            time.sleep(SETTING['SendOften'])
            IsSendMsgNow=True
            #需等待继续发送消息
        #============================
        #组合小尾巴消息
        if SETTING['Ontail'] and not '@img@' in text or text==' ':
            Newtext='%s\r\n%s'%(text,SETTING['TailTextAll'][random.randint(0,4)])
        #==============
        itchat.send(Newtext,n['UserName'])
        print(n['UserName'])
        try:
            #如果设置的图片消息，是否接着发送小尾巴消息
            if SETTING['OnSendTwoMsg'] and not userid.istextimg:
                itchat.send(SETTING['TailTextAll'][random.randint(0,4)], n['UserName'])
        except:
            # 普通用户会出错 直接跳过
            pass
        if sendnum==SETTING['SendRestnumber']:
            print('短暂休息 %s 秒  已经检测 %s 人，共有僵尸粉 %s 人。好友总数 %s' % (SETTING['SendRest'], allnum, JSF, len(friend)))
            notice('短暂休息 %s 秒  已经检测 %s 人，共有僵尸粉 %s 人。好友总数 %s'%(SETTING['SendRest'],allnum,JSF,len(friend)))
            time.sleep(SETTING['SendRest'])
            sendnum=0
        else:
            time.sleep(SETTING['SendInterval'])
    print('检测完毕  已经检测 %s 人，共有僵尸粉 %s 人。好友总数 %s' % (allnum, JSF, len(friend)))
    notice('检测完毕  已经检测 %s 人，共有僵尸粉 %s 人。好友总数 %s' % (allnum, JSF, len(friend)))
    itchat.logout()
    exit()


thr = Thread(target=UDP, args=[])
thr.setDaemon(True)
thr.start()
itchat.auto_login(False,exitCallback=wx_logout)#暂存登录状态
islogin=True
while True:
    if userid:
        if userid=='陌生人':
            sendtext =' '
        else:
            if SETTING['Oncustom']:
                if userid.istextimg: #为真为文字消息  假为图片消息
                    sendtext = userid.sendtext
                else:
                    sendtext = '@img@%s' % userid.imgpath
            else:
                sendtext = ' '
        #判断是否添加后缀
        thr1 = Thread(target=Sendmsg, args=[sendtext])
        thr1.setDaemon(True)
        thr1.start()
        itchat.run()
        wx_logout()
    time.sleep(1)

    # sendtext=[]
    # #组合消息列表
    # msglist=userid().GetSendMsgList()
    # if msglist['sendmsg1']!='无':
    #     if SETTING['Ontail']:
    #         sendtext.append('%s\r\n%s'%(msglist['sendmsg1'], SETTING['TailText']))
    #     else:
    #         sendtext.append(msglist['sendmsg1'])
    # if msglist['sendmsg2']!='无':
    #     if SETTING['Ontail']:
    #         sendtext.append('%s\r\n%s'%(msglist['sendmsg1'], SETTING['TailText']))
    #     else:
    #         sendtext.append(msglist['sendmsg2'])
    # if msglist['sendmsg3']!='无':
    #     if SETTING['Ontail']:
    #         sendtext.append('%s\r\n%s'%(msglist['sendmsg1'], SETTING['TailText']))
    #     else:
    #         sendtext.append(msglist['sendmsg3'])
    # if msglist['sendmsg4']!='无':
    #     if SETTING['Ontail']:
    #         sendtext.append('%s\r\n%s'%(msglist['sendmsg1'], SETTING['TailText']))
    #     else:
    #         sendtext.append(msglist['sendmsg4'])
    # if msglist['sendmsg5']!='无':
    #     if SETTING['Ontail']:
    #         sendtext.append('%s\r\n%s'%(msglist['sendmsg1'], SETTING['TailText']))
    #     else:
    #         sendtext.append(msglist['sendmsg5'])