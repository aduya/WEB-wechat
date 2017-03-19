import os

#数据库配置
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_RECORD_QUERIES = True
DATABASE_QUERY_TIMEOUT = 0.5

#表单验证配置
CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

WX_LOGIN_START_BAT=os.path.join(basedir, 'bot','start.bat')
WX_QR_CODE_JPG=os.path.join(basedir,'QR.jpg')#微信验证码图片
if os.path.exists(WX_QR_CODE_JPG):
    os.remove(WX_QR_CODE_JPG)


UPLOAD_FOLDER = os.path.join(basedir, 'app','static','cache')
MAX_CONTENT_LENGTH = 500 * 1024  # 500kb
