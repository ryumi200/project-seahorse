import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect

# .envから環境変数を読み込む
load_dotenv()

# Flaskアプリケーションを初期化
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or "fallback-secret-key"
# データベース設定
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///task.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# CSRF保護を有効にする
csrf = CSRFProtect(app)

# SQLAlchemyインスタンスを作成
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = "login"

# ルートをインポート
from app import routes, models


@login.user_loader
def load_user(id):
    return models.User.query.get(int(id))
