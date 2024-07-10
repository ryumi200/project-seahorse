from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from dotenv import load_dotenv

# .envから環境変数を読み込む
load_dotenv()

# Flaskアプリケーションを初期化
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or "fallback-secret-key"
# データベース設定
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///task.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# SQLAlchemyインスタンスを作成
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = "login"

# ルートをインポート
from app import routes, models


@login.user_loader
def load_user(id):
    return models.User.query.get(int(id))
