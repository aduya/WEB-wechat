from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(64), index = True, unique = True)#网站邮箱
    password = db.Column(db.String(126))#网站密码
    isadmin=db.Column(db.Boolean)#是否是管理员
    pid = db.Column(db.Integer)  #进程pid
    sendtext=db.Column(db.Text) #自定义文字消息
    istextimg=db.Column(db.Boolean)#使用什么发送内容
    cover = db.Column(db.String(64)) #图片url
    imgpath= db.Column(db.String(64)) #图片路径

    def is_authenticated(self):
        return True
    #is_authenticated 方法有一个具有迷惑性的名称。一般而言，这个方法应该只返回 True，除非表示用户的对象因为某些原因不允许被认证。

    def is_active(self):
        return True
    #is_active 方法应该返回 True，除非是用户是无效的，比如因为他们的账号是被禁止。

    def is_anonymous(self):
        return False
    #is_anonymous 方法应该返回 True，除非是伪造的用户不允许登录系统。

    def verify_password(self, password):
        #对比用户密码
        if self.password==password:
            return True
        else:
            return False
    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3
    def save(self):
        db.session.add(self)
        db.session.commit()

    def GetSendMsgList(self):
        return {
            'sendmsg1':self.sendmsg1,
            'sendmsg2': self.sendmsg2,
            'sendmsg3': self.sendmsg3,
            'sendmsg4': self.sendmsg4,
            'sendmsg5': self.sendmsg5
        }
    def __repr__(self):
        return '<User %r>' % (self.email)


class Wxbot(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    Onbot=db.Column(db.Boolean)#是否开启微信登录功能
    Oncustom=db.Column(db.Boolean)#是否开启自定义功能
    Ontail=db.Column(db.Boolean)#是否开启小尾巴功能
    OnSendTwoMsg=db.Column(db.Boolean)#是否开启发送两条信息,图片内容加尾巴
    SendText=db.Column(db.String(64)) #当用户未设置内容时，发送该文本
    SendInterval=db.Column(db.Integer)#发送消息间隔
    SendRestnumber=db.Column(db.Integer)#发送多少个消息后 休息
    SendRest=db.Column(db.Integer)#休息多少秒
    SendOften=db.Column(db.Integer)#频繁等待
    #5个小尾巴内容
    TailText1 = db.Column(db.Text,default='无')  #发送内容1
    TailText2 = db.Column(db.Text,default='无')  # 发送内容2
    TailText3 = db.Column(db.Text,default='无')  # 发送内容3
    TailText4 = db.Column(db.Text,default='无')  # 发送内容4
    TailText5 = db.Column(db.Text,default='无')  # 发送内容5
    # 5个消息框

    def get(self):
        q = Wxbot.query.get(1)
        if q:
            return q
        else:
            q = Wxbot()
            return q

    def save(self):
        db.session.add(self)
        db.session.commit()

    def GetSetting(self):
        q=self.get()
        return {
            'Onbot':q.Onbot,
            'Oncustom':q.Oncustom,
            'Ontail':q.Ontail,
            'TailTextAll':[
                q.TailText1,
                q.TailText2,
                q.TailText3,
                q.TailText4,
                q.TailText5,
            ],
            'SendText':q.SendText,
            'SendInterval':q.SendInterval,
            'SendRest':q.SendRest,
            'SendRestnumber':q.SendRestnumber,
            'OnSendTwoMsg':q.OnSendTwoMsg,
            'SendOften':q.SendOften
        }
    def __repr__(self):
        return '<Wxbot %r>' % (self.id)