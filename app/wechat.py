import win32api
import psutil
import os
import shutil
import socket
import time,datetime
from flask import g
from config import WX_QR_CODE_JPG,basedir


def allowed_file(filename):
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def wx_login_bat(temp):
    '''
    :param temp: 时间戳参数
    :return: 图片名称
    '''
    if os.path.exists(WX_QR_CODE_JPG):
        os.remove(WX_QR_CODE_JPG)
    win32api.ShellExecute(0, 'open', 'python.exe', 'mian.py', '', 1)
    img_path=os.path.join(basedir,'app','static','cache','%s.jpg'%temp)
    starttime = datetime.datetime.now()
    while 1:
        if os.path.exists(WX_QR_CODE_JPG):
            #移动图片到模版文件夹
            ret=g.user.is_authenticated
            senduserid(ret)
            shutil.move(WX_QR_CODE_JPG,img_path)
            pid=getpid()
            if ret:
                g.user.pid=pid
                g.user.save()
            return True
        time.sleep(1)
        endtime = datetime.datetime.now()
        if (endtime - starttime).seconds > 30:
            return False

def wx_is_login_state():
    '''
    通过pid检测微信子进程是否还在运行
    :return:
    '''
    pid=g.user.pid
    if psutil.pid_exists(pid):
        return True
    return False



def wx_logout():
    '''
    强行关闭微信pid
    :return:
    '''
    pid = g.user.pid
    try:
        if psutil.pid_exists(pid):
            os.system('taskkill /PID %s /F /T' % pid)
        return '关闭微信成功'
    except:
        return '关闭微信成功'


def getpid():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto('pid'.encode(), ('127.0.0.1', 8888))
    ret=s.recv(1024).decode('utf-8')
    s.close()
    return ret

def senduserid(ret1):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if ret1:
        ret = '%s' % g.user.id
        ret = 'userid%s' % ret
        s.sendto(ret.encode(), ('127.0.0.1', 8888))
    else:
        ret = 'userid99999'
        s.sendto(ret.encode(), ('127.0.0.1', 8888))

