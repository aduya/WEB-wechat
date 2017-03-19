from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
#读取配置文件

app.config.from_object('config')
#创建数据库对象
db = SQLAlchemy(app)

#创建登录对象
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

#导入模版为全局变量

from app import views, models