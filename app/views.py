from flask import render_template, flash, redirect,g,url_for,session,request,jsonify

from flask_login import login_user, logout_user, current_user, login_required,AnonymousUserMixin
from app import app,lm,db
from .models import User,Wxbot
from .forms import LoginForm,RegistrationForm
from .wechat import wx_is_login_state,wx_logout,wx_login_bat,allowed_file
import os
import hashlib
import time

@app.before_request
def before_request():
    g.user = current_user


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    try:
        isfile=os.path.isfile(g.user.imgpath)
    except:
        isfile=False
    if not g.user.is_authenticated:
        return render_template('wechat.html',
                           isfile=isfile,
                           function_list=Wxbot().GetSetting())
    if g.user.isadmin:
        return render_template('wechat.html',
                           isfile=isfile,
                           function_list=Wxbot().GetSetting())
    else:
        return render_template('wechat.html',
                           isfile=isfile,
                           function_list=Wxbot().GetSetting())

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

#登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    # g 对象 存储生命周期内已经登录的用户，不用再次登录 直接重定向至 主页
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            session['remember_me'] = form.remember_me.data
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('index'))

        flash('Invalid username or password.')
    return render_template('login.html',
                           title='Sign In',
                           form=form)
#注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    password=form.password.data,
                    pid=999999,
                    isadmin=False)
        user.save()
        flash('注册成功，请使用注册帐号登录吧！')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

#退出登录
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

###微信视图
@app.route('/wechat', methods=['GET', 'POST'])
def wechat():
    return redirect(url_for('index'))


@app.route('/wechat/login/', methods=['GET', 'POST'])
def wechat_login():
    try:
        if 'wechat' in request.headers['Referer']:
            flash('请勿重复获取')
            return redirect(url_for('index'))
    except:
        flash('请勿重复获取')
        return redirect(url_for('index'))
    setting=Wxbot().GetSetting()
    temp = request.args.get('timestamp')
    if not setting['Onbot']:
        flash('管理员禁止登录')
        return redirect(url_for('index'))
    if g.user.is_authenticated:
        if g.user.sendtext==None and g.user.imgpath==None and setting['Oncustom']:
            flash('请先设置发送内容')
            return redirect(url_for('index'))
        ret = wx_is_login_state()
        if not ret:
            wx_logout()
            WX_PID = wx_login_bat(temp)
            if WX_PID:
                flash('请在120秒内扫码登录，过期失效')
                return render_template('wxchat/wxlogin.html',
                                       img_path='%s.jpg' % temp,
                                       is_wxchat=ret,
                                       active_page='wechat_login',
                                       function_list=setting)
            flash('获取二维码失败，请重新获取')
            wx_logout()
            return render_template('wxchat/wxlogin.html',
                                   img_path=False,
                                   is_wxchat=ret,
                                   active_page='wechat_login',
                                   function_list=setting)
        flash('请勿重复登录')
        return redirect(url_for('index'))
    #未登录用户获取二维码
    WX_PID = wx_login_bat(temp)
    if WX_PID:
        flash('请在120秒内扫码登录，过期失效')
        return render_template('wxchat/wxlogin.html',
                               img_path='%s.jpg' % temp,
                               is_wxchat=False,
                               active_page='wechat_login',
                               function_list=setting)
    flash('获取二维码失败，请重新获取')
    return redirect(url_for('index'))

@app.route('/wechat/setting', methods = ['POST','GET'])
def wechat_setting():
    if not g.user.is_authenticated:
        flash('注册登录后使用，自定义消息')
        return redirect(url_for('index'))
    if request.method == 'POST':
        user = g.user
        file = request.files['file']
        if file and allowed_file(file.filename):
            ext = file.filename.split('.')[1]
            name = '%s' % g.user.email + str(time.time())
            name=hashlib.md5(name.encode()).hexdigest()[:15]
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], '%s.%s'%(name,ext)))
            user.imgpath=os.path.join(app.config['UPLOAD_FOLDER'], '%s.%s'%(name,ext))
            user.cover =url_for('.static',filename='cache/%s'%('%s.%s'%(name,ext)))
            flash('上传成功 使用图片内容')
        user.istextimg=False #表示使用图片
        user.save()
    return redirect(url_for('index'))


@app.route('/wechat/setting1', methods = ['POST','GET'])
def wechat_setting1():
    if request.method == 'POST':
        if not g.user.is_authenticated:
            return jsonify({
                'text': '注册登录后使用，自定义消息'
            })
        text1 = request.form['text1']
        if len(text1)>50:
            return jsonify({
                'text':'内容太长,保存失败'
            })
        user=g.user
        user.sendtext = text1
        user.istextimg=True
        user.save()
        flash('上传成功 使用文字内容')
        return jsonify({
            'text': '上传成功'
        })
    flash('上传失败')
    return redirect(url_for('index'))

@app.route('/wechat/setting3', methods = ['POST','GET'])
@login_required
def wechat_setting3():
    if not g.user.is_authenticated:
        flash('登录成功后，可以使用自定义消息')
        return redirect(url_for('index'))
    if not g.user.isadmin:
        flash('非法调用')
        return redirect(url_for('index'))
    if request.method == 'POST':
        try:
            SendInterval=int(request.form['SendInterval'])
            SendRestnumber = int(request.form['SendRestnumber'])
            SendRest = int(request.form['SendRest'])
            SendOften=int(request.form['SendOften'])
        except:
            return jsonify({
                'text':'消息间隔设置错误'
            })
        if request.form['Onbot']=='true':
            Onbot=True
        else:
            Onbot=False
        if request.form['Oncustom']=='true':
            Oncustom=True
        else:
            Oncustom = False
        if request.form['Ontail']=='true':
            Ontail=True
        else:
            Ontail = False
        if request.form['OnSendTwoMsg']=='true':
            OnSendTwoMsg=True
        else:
            OnSendTwoMsg = False
        TailText1=request.form['settext1']
        TailText2 = request.form['settext2']
        TailText3 = request.form['settext3']
        TailText4 = request.form['settext4']
        TailText5 = request.form['settext5']
        setting=Wxbot().get()
        setting.Onbot=Onbot
        setting.Oncustom=Oncustom
        setting.Ontail=Ontail
        setting.TailText1 = TailText1
        setting.TailText2 = TailText2
        setting.TailText3 = TailText3
        setting.TailText4 = TailText4
        setting.TailText5 = TailText5
        setting.SendInterval=SendInterval
        setting.SendRestnumber = SendRestnumber
        setting.SendRest = SendRest
        setting.OnSendTwoMsg=OnSendTwoMsg
        setting.SendOften = SendOften
        setting.save()
    flash('保存成功')
    return redirect(url_for('index'))

@app.route('/wechat/wxlogout/', methods=['GET', 'POST'])
def wechat_wxlogout():
    if not g.user.is_authenticated:
        flash('未注册登录用户，请在手机端微信 上方点击退出登录')
        return redirect(url_for('index'))
    ret = wx_is_login_state()
    if ret:
        a = wx_logout()
        flash(a)
        return redirect(url_for('wechat'))
    flash('未登录微信')
    return redirect(url_for('wechat'))


@app.errorhandler(404)
def internal_error(error):
    return redirect(url_for('index'))


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return redirect(url_for('index'))